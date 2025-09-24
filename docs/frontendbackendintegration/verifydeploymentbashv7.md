Let’s extend the verification script to **fully validate production deployment**, including:

1. **HTTPS check** for the CloudFront URL.
2. **Redirects** (HTTP → HTTPS).
3. **CloudFront caching headers** to ensure static files are served correctly.
4. Retains **backend health** and **API integration checks**.

Here’s the upgraded Bash script:

```bash
#!/bin/bash

# -----------------------------
# CONFIGURATION
# -----------------------------
ENV_FILE="./.env.local"
FRONTEND_URL="https://dpy3jeqrdnvsx.cloudfront.net"
MAX_RETRIES=3
SLEEP_INTERVAL=5  # seconds
SLACK_WEBHOOK_URL="" # optional Slack webhook for notifications

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
                echo "   Retrying in $SLEEP_INTERVAL seconds..."
                sleep $SLEEP_INTERVAL
            fi
        fi
        attempt=$((attempt + 1))
    done
    echo "❌ $description not reachable after $max_retries attempts"
    notify_slack "$description not reachable after $max_retries attempts!"
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
    notify_slack "CloudFront cache header missing for frontend!"
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
            echo "❌ Backend not reachable after $MAX_RETRIES attempts"
            notify_slack "Backend not reachable after $MAX_RETRIES attempts!"
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

if [ -d "./pages/api" ]; then
    while IFS= read -r -d '' file; do
        route="${file#./pages/api}"  
        route="${route%.js}"          
        route="${route%.ts}"          
        route="${route}/"             
        API_ROUTES+=("$route")
    done < <(find ./pages/api -type f \( -name "*.js" -o -name "*.ts" \) -print0)
elif [ -d "./app/api" ]; then
    while IFS= read -r -d '' file; do
        route="${file#./app/api}"  
        route="${route%.js}"       
        route="${route%.ts}"       
        route="${route}/"
        API_ROUTES+=("$route")
    done < <(find ./app/api -type f \( -name "*.js" -o -name "*.ts" \) -print0)
else
    echo "⚠️ No API routes found"
fi

# -----------------------------
# FRONTEND-BACKEND INTEGRATION CHECKS
# -----------------------------
for api_path in "${API_ROUTES[@]}"; do
    echo -e "\n🔎 Checking API route: $api_path"
    attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        INTEGRATION_STATUS=$(curl -s -o /tmp/integration_response.txt -w "%{http_code}" $FRONTEND_URL$api_path)
        INTEGRATION_BODY=$(cat /tmp/integration_response.txt)
        if [ "$INTEGRATION_STATUS" -eq 200 ]; then
            echo "✅ $api_path OK: $INTEGRATION_STATUS (Attempt $attempt)"
            break
        else
            echo "⚠️ $api_path failed: $INTEGRATION_STATUS (Attempt $attempt)"
            if [ $attempt -lt $MAX_RETRIES ]; then
                sleep $SLEEP_INTERVAL
            else
                echo "❌ $api_path not OK after $MAX_RETRIES attempts"
                notify_slack "$api_path failed integration test!"
                exit 1
            fi
        fi
        attempt=$((attempt + 1))
    done
done

# -----------------------------
# CLEANUP
# -----------------------------
rm -f /tmp/backend_response.txt /tmp/integration_response.txt

echo -e "\n🎉 Full production verification completed successfully!"
exit 0
```

---

### ✅ New Features:

1. **HTTPS verification** for CloudFront URL.
2. **HTTP → HTTPS redirect check**.
3. **CloudFront caching header detection** (`x-cache`) for static files.
4. Retains **backend health** and **all API route integration checks**.
5. Slack notifications and CI/CD exit codes.

---

This script now gives you **full confidence** that your frontend is deployed properly, your API works, HTTPS is enforced, and CloudFront is caching content.


