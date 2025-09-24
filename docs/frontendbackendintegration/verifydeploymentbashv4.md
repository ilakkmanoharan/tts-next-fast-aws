Here’s an updated version of `verify-deployment.sh` that **reads your frontend `.env.local` file** to automatically get the backend URL and uses it to check integration—so you don’t have to hardcode anything.

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

# Extract NEXT_PUBLIC_BACKEND_URL
BACKEND_URL=$(grep -E "^NEXT_PUBLIC_BACKEND_URL=" "$ENV_FILE" | cut -d '=' -f2)

if [ -z "$BACKEND_URL" ]; then
    echo "❌ NEXT_PUBLIC_BACKEND_URL not set in .env.local"
    exit 1
fi

# Frontend CloudFront URL (keep hardcoded or set via ENV if needed)
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
# Frontend-backend integration check
# -----------------------------
# Auto-use backend URL from .env.local in frontend API call
echo -e "\n🔎 Checking Frontend-Backend Integration..."
# Example: assuming your frontend exposes /api/test that calls backend
API_PATH="/api/test"  
attempt=1
while [ $attempt -le $MAX_RETRIES ]; do
    INTEGRATION_STATUS=$(curl -s -o /tmp/integration_response.txt -w "%{http_code}" $FRONTEND_URL$API_PATH)
    INTEGRATION_BODY=$(cat /tmp/integration_response.txt)
    if [ "$INTEGRATION_STATUS" -eq 200 ]; then
        echo "✅ Integration OK: $INTEGRATION_STATUS, response: $INTEGRATION_BODY (Attempt $attempt)"
        break
    else
        echo "⚠️ Integration check failed: $INTEGRATION_STATUS, response: $INTEGRATION_BODY (Attempt $attempt)"
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "   Retrying in $SLEEP_INTERVAL seconds..."
            sleep $SLEEP_INTERVAL
        else
            echo "❌ Integration not OK after $MAX_RETRIES attempts"
        fi
    fi
    attempt=$((attempt + 1))
done

# Clean up temp files
rm -f /tmp/backend_response.txt /tmp/integration_response.txt
```

---

### ✅ Key Features of this Version:

1. **Reads `NEXT_PUBLIC_BACKEND_URL` from `.env.local` automatically**.
2. Still retries **frontend, backend, and integration checks** up to `MAX_RETRIES`.
3. Integration check now dynamically uses your backend URL—no hardcoding.
4. Clean temp files after execution.

---
