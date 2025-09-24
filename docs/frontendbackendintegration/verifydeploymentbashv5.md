We can make an **advanced version** that automatically detects your Next.js API routes from the `pages/api/` or `app/api/` folder and tests each one against the deployed frontend. This way, you don’t need to hardcode `/api/test` or any other paths.

Here’s the script:

```bash
#!/bin/bash

# -----------------------------
# Auto-detect backend URL from .env.local
# -----------------------------
ENV_FILE="./.env.local"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env.local not found in project root!"
    exit 1
fi

BACKEND_URL=$(grep -E "^NEXT_PUBLIC_BACKEND_URL=" "$ENV_FILE" | cut -d '=' -f2)

if [ -z "$BACKEND_URL" ]; then
    echo "❌ NEXT_PUBLIC_BACKEND_URL not set in .env.local"
    exit 1
fi

# Frontend CloudFront URL (can also make dynamic if you want)
FRONTEND_URL="https://dpy3jeqrdnvsx.cloudfront.net"

MAX_RETRIES=3
SLEEP_INTERVAL=5  # seconds between retries

# -----------------------------
# Retry function
# -----------------------------
retry_check() {
    local url=$1
    local description=$2
    local max_retries=$3
    local attempt=1

    while [ $attempt -le $max_retries ]; do
        HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}\n" $url)
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
    return 1
}

# -----------------------------
# Frontend check
# -----------------------------
echo "🔎 Checking Frontend..."
retry_check "$FRONTEND_URL" "Frontend" $MAX_RETRIES

# -----------------------------
# Backend health check
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
            echo "   Retrying in $SLEEP_INTERVAL seconds..."
            sleep $SLEEP_INTERVAL
        else
            echo "❌ Backend not reachable after $MAX_RETRIES attempts"
        fi
    fi
    attempt=$((attempt + 1))
done

# -----------------------------
# Detect all Next.js API routes
# -----------------------------
echo -e "\n🔎 Detecting Next.js API routes..."
API_ROUTES=()

if [ -d "./pages/api" ]; then
    while IFS= read -r -d '' file; do
        # Convert file path to route
        route="${file#./pages/api}"       # remove prefix
        route="${route%.js}"              # remove .js
        route="${route%.ts}"              # remove .ts
        route="${route}/"                 # ensure trailing slash
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
    echo "⚠️ No Next.js API routes found in pages/api/ or app/api/"
fi

# -----------------------------
# Frontend-backend integration checks for all API routes
# -----------------------------
for api_path in "${API_ROUTES[@]}"; do
    echo -e "\n🔎 Checking API route: $api_path"
    attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        INTEGRATION_STATUS=$(curl -s -o /tmp/integration_response.txt -w "%{http_code}" $FRONTEND_URL$api_path)
        INTEGRATION_BODY=$(cat /tmp/integration_response.txt)
        if [ "$INTEGRATION_STATUS" -eq 200 ]; then
            echo "✅ $api_path OK: $INTEGRATION_STATUS, response: $INTEGRATION_BODY (Attempt $attempt)"
            break
        else
            echo "⚠️ $api_path failed: $INTEGRATION_STATUS, response: $INTEGRATION_BODY (Attempt $attempt)"
            if [ $attempt -lt $MAX_RETRIES ]; then
                echo "   Retrying in $SLEEP_INTERVAL seconds..."
                sleep $SLEEP_INTERVAL
            else
                echo "❌ $api_path not OK after $MAX_RETRIES attempts"
            fi
        fi
        attempt=$((attempt + 1))
    done
done

# -----------------------------
# Clean up
# -----------------------------
rm -f /tmp/backend_response.txt /tmp/integration_response.txt
```

---

### ✅ Features of This Advanced Version:

1. **Auto-detects backend URL** from `.env.local`.
2. **Auto-detects all Next.js API routes** from `pages/api/` or `app/api/`.
3. **Retries each check** up to `MAX_RETRIES` with a wait interval.
4. **Reports detailed success/failure** for each route.
5. **No hardcoding of `/api/test`**—everything is dynamic.

---


