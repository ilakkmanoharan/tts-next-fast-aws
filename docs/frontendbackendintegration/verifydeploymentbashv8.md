Let’s extend the script to **fully verify all static assets** on CloudFront, so you catch any missing or broken files in production. This is especially useful for Next.js, where static assets live in `/.next/static/` or `public/`.

Here’s the upgraded script:

```bash
#!/bin/bash

# -----------------------------
# CONFIGURATION
# -----------------------------
ENV_FILE="./.env.local"
FRONTEND_URL="https://dpy3jeqrdnvsx.cloudfront.net"
MAX_RETRIES=3
SLEEP_INTERVAL=5
SLACK_WEBHOOK_URL="" # optional Slack webhook

# Paths to check for static assets
STATIC_DIRS=("public" ".next/static")

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
notify_slack() {
    local message=$1
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -s -X POST -H 'Content-type: application/json' \
             --data "{\"text\":\"$message\"}" $SLACK_WEBHOOK_URL
    fi
}

retry_check() {
    local url=$1
    local description=$2
    local max_retries=$3
    local attempt=1

    while [ $attempt -le $max_retries ]; do
        HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}" $url)
        if [ "$HTTP_STATUS" -eq 200 ]; then
            echo "✅ $description reachable: $HTTP_STATUS (Attempt $attempt)"
            return 0
        else
            echo "⚠️ $description check failed: $HTTP_STATUS (Attempt $attempt)"
            if [ $attempt -lt $max_retries ]; then
                sleep $SLEEP_INTERVAL
            fi
        fi
        attempt=$((attempt + 1))
    done
    echo "❌ $description not reachable after $max_retries attempts"
    notify_slack "$description not reachable!"
    return 1
}

# -----------------------------
# LOAD BACKEND URL
# -----------------------------
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env.local not found!"
    exit 1
fi

BACKEND_URL=$(grep -E "^NEXT_PUBLIC_BACKEND_URL=" "$ENV_FILE" | cut -d '=' -f2)
if [ -z "$BACKEND_URL" ]; then
    echo "❌ NEXT_PUBLIC_BACKEND_URL not set in .env.local"
    exit 1
fi

# -----------------------------
# FRONTEND CHECKS
# -----------------------------
echo "🔎 Checking Frontend HTTPS..."
retry_check "$FRONTEND_URL" "Frontend HTTPS" $MAX_RETRIES || exit 1

echo "🔎 Checking HTTP → HTTPS redirect..."
REDIRECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${FRONTEND_URL#https://}")
if [ "$REDIRECT_STATUS" -eq 301 ] || [ "$REDIRECT_STATUS" -eq 308 ]; then
    echo "✅ HTTP redirects to HTTPS: $REDIRECT_STATUS"
else
    echo "⚠️ HTTP redirect missing: $REDIRECT_STATUS"
    notify_slack "HTTP redirect missing for frontend!"
fi

echo "🔎 Checking CloudFront caching headers..."
CACHE_HEADER=$(curl -s -D - -o /dev/null $FRONTEND_URL | grep -i "x-cache")
if [ -n "$CACHE_HEADER" ]; then
    echo "✅ CloudFront cache header present: $CACHE_HEADER"
else
    echo "⚠️ CloudFront cache header missing!"
    notify_slack "CloudFront cache header missing!"
fi

# -----------------------------
# BACKEND HEALTH
# -----------------------------
echo -e "\n🔎 Checking Backend Health..."
attempt=1
while [ $attempt -le $MAX_RETRIES ]; do
    BACKEND_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/backend_response.txt $BACKEND_URL/health)
    HTTP_BODY=$(cat /tmp/backend_response.txt)
    if [ "$BACKEND_RESPONSE" -eq 200 ]; then
        echo "✅ Backend reachable: $BACKEND_RESPONSE, response: $HTTP_BODY (Attempt $attempt)"
        break
    else
        echo "⚠️ Backend check failed: $BACKEND_RESPONSE, response: $HTTP_BODY (Attempt $attempt)"
        if [ $attempt -lt $MAX_RETRIES ]; then
            sleep $SLEEP_INTERVAL
        else
            echo "❌ Backend not reachable!"
            notify_slack "Backend not reachable!"
            exit 1
        fi
    fi
    attempt=$((attempt + 1))
done

# -----------------------------
# DETECT NEXT.JS API ROUTES
# -----------------------------
echo -e "\n🔎 Detecting Next.js API routes..."
API_ROUTES=()

for dir in pages/api app/api; do
    if [ -d "./$dir" ]; then
        while IFS= read -r -d '' file; do
            route="${file#./$dir}"
            route="${route%.js}"
            route="${route%.ts}"
            route="${route}/"
            API_ROUTES+=("$route")
        done < <(find ./$dir -type f \( -name "*.js" -o -name "*.ts" \) -print0)
    fi
done

# -----------------------------
# FRONTEND-BACKEND API CHECKS
# -----------------------------
for api_path in "${API_ROUTES[@]}"; do
    echo -e "\n🔎 Checking API route: $api_path"
    attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        STATUS=$(curl -s -o /tmp/integration_response.txt -w "%{http_code}" $FRONTEND_URL$api_path)
        BODY=$(cat /tmp/integration_response.txt)
        if [ "$STATUS" -eq 200 ]; then
            echo "✅ $api_path OK (Attempt $attempt)"
            break
        else
            echo "⚠️ $api_path failed: $STATUS"
            if [ $attempt -lt $MAX_RETRIES ]; then
                sleep $SLEEP_INTERVAL
            else
                echo "❌ $api_path not OK!"
                notify_slack "$api_path failed integration test!"
                exit 1
            fi
        fi
        attempt=$((attempt + 1))
    done
done

# -----------------------------
# STATIC ASSETS CHECK
# -----------------------------
echo -e "\n🔎 Checking all static assets..."
for dir in "${STATIC_DIRS[@]}"; do
    if [ -d "./$dir" ]; then
        while IFS= read -r -d '' file; do
            asset_path="${file#./}" # relative path
            echo "Checking $asset_path ..."
            retry_check "$FRONTEND_URL/$asset_path" "Asset $asset_path" $MAX_RETRIES || exit 1
        done < <(find ./$dir -type f -print0)
    fi
done

# -----------------------------
# CLEANUP
# -----------------------------
rm -f /tmp/backend_response.txt /tmp/integration_response.txt

echo -e "\n🎉 All production checks including static assets passed successfully!"
exit 0
```

---

### ✅ New Features Added:

1. **Automatically checks all static files** in `public/` and `.next/static/`.
2. Retries failed asset requests up to `MAX_RETRIES`.
3. Fails CI/CD build if any asset is missing or broken.
4. Retains **HTTPS, redirects, caching headers, backend health, and API checks**.

---

This now gives you a **full production verification**: frontend, backend, API routes, HTTPS, redirects, CloudFront caching, and all static assets.

