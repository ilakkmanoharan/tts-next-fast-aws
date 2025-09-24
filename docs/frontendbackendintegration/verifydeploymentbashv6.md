Let’s make the **CI/CD-ready version** of the deployment verification script. This version will:

1. Fail with a non-zero exit code if **any check fails** (so your CI/CD pipeline stops automatically).
2. Optionally send **Slack notifications** on failure.
3. Keep **all the automatic detection and retries** from the previous script.

Here’s the enhanced script:

```bash
#!/bin/bash

# -----------------------------
# CONFIGURATION
# -----------------------------
ENV_FILE="./.env.local"
FRONTEND_URL="https://dpy3jeqrdnvsx.cloudfront.net"
MAX_RETRIES=3
SLEEP_INTERVAL=5  # seconds between retries

# Slack webhook URL (optional)
SLACK_WEBHOOK_URL="" # set to your webhook URL if you want notifications

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

# Send Slack notification
notify_slack() {
    local message=$1
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -s -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" $SLACK_WEBHOOK_URL
    fi
}

# Retry check function
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
    notify_slack "$description not reachable after $max_retries attempts!"
    return 1
}

# -----------------------------
# Load backend URL from .env.local
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
# CHECK FRONTEND
# -----------------------------
echo "🔎 Checking Frontend..."
retry_check "$FRONTEND_URL" "Frontend" $MAX_RETRIES || exit 1

# -----------------------------
# CHECK BACKEND HEALTH
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
# DETECT ALL NEXT.JS API ROUTES
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
                notify_slack "$api_path failed integration test after $MAX_RETRIES attempts!"
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

echo -e "\n🎉 All checks passed successfully!"
exit 0
```

---

### ✅ Features

1. **Fails the CI/CD pipeline** if any check fails (`exit 1`).
2. **Slack notifications** if a check fails (optional, just set `SLACK_WEBHOOK_URL`).
3. Automatic **detection of backend URL** and **all API routes**.
4. Retries failed requests up to `MAX_RETRIES`.
5. Detailed logs for each attempt.

---

You can now add this to your **CI/CD workflow** after deployment. For example, in GitHub Actions:

```yaml
- name: Verify Deployment
  run: bash ./verify-deployment.sh
```

---


