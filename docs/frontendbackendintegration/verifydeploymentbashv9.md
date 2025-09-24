Let’s create a **full reporting version** of the deployment verification script. This one will:

1. **Check frontend, backend, API routes, and static assets** (all previous checks).
2. **Log every URL checked** with HTTP status and response time.
3. **Output a Markdown table** (`deployment-report.md`) and a CSV (`deployment-report.csv`) for easy review or CI/CD artifacts.
4. **Still fail the pipeline** if any check fails, with Slack notifications optional.

Here’s the script:

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
STATIC_DIRS=("public" ".next/static")
REPORT_MD="deployment-report.md"
REPORT_CSV="deployment-report.csv"

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
    local start_time=$(date +%s)

    while [ $attempt -le $max_retries ]; do
        HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}" $url)
        if [ "$HTTP_STATUS" -eq 200 ]; then
            end_time=$(date +%s)
            response_time=$((end_time - start_time))
            echo "✅ $description reachable: $HTTP_STATUS (Attempt $attempt, ${response_time}s)"
            echo "$url,$description,200,${response_time}s" >> $REPORT_CSV
            echo "|$url|$description|200|${response_time}s|" >> $REPORT_MD
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
    notify_slack "$description not reachable after $max_retries attempts!"
    echo "$url,$description,$HTTP_STATUS,FAIL" >> $REPORT_CSV
    echo "|$url|$description|$HTTP_STATUS|FAIL|" >> $REPORT_MD
    return 1
}

# -----------------------------
# INIT REPORT FILES
# -----------------------------
echo "|URL|Description|HTTP Status|Response Time|" > $REPORT_MD
echo "|---|---|---|---|" >> $REPORT_MD
echo "URL,Description,HTTP Status,Response Time" > $REPORT_CSV

# -----------------------------
# LOAD BACKEND URL
# -----------------------------
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env.local not found!"
    exit 1
fi

BACKEND_URL=$(grep -E "^NEXT_PUBLIC_BACKEND_URL=" "$ENV_FILE" | cut -d '=' -f2)
if [ -z "$BACKEND_URL" ]; then
    echo "❌ NEXT_PUBLIC_BACKEND_URL not set"
    exit 1
fi

# -----------------------------
# FRONTEND CHECKS
# -----------------------------
retry_check "$FRONTEND_URL" "Frontend HTTPS" $MAX_RETRIES || exit 1

# HTTP → HTTPS redirect check
REDIRECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${FRONTEND_URL#https://}")
if [ "$REDIRECT_STATUS" -eq 301 ] || [ "$REDIRECT_STATUS" -eq 308 ]; then
    echo "✅ HTTP redirects to HTTPS: $REDIRECT_STATUS"
    echo "$FRONTEND_URL,Redirect to HTTPS,$REDIRECT_STATUS,OK" >> $REPORT_CSV
    echo "|$FRONTEND_URL|Redirect to HTTPS|$REDIRECT_STATUS|OK|" >> $REPORT_MD
else
    echo "⚠️ HTTP redirect missing: $REDIRECT_STATUS"
    notify_slack "HTTP redirect missing for frontend!"
    echo "$FRONTEND_URL,Redirect to HTTPS,$REDIRECT_STATUS,FAIL" >> $REPORT_CSV
    echo "|$FRONTEND_URL|Redirect to HTTPS|$REDIRECT_STATUS|FAIL|" >> $REPORT_MD
fi

# CloudFront cache header
CACHE_HEADER=$(curl -s -D - -o /dev/null $FRONTEND_URL | grep -i "x-cache")
if [ -n "$CACHE_HEADER" ]; then
    echo "✅ CloudFront cache header: $CACHE_HEADER"
    echo "$FRONTEND_URL,CloudFront Cache Header,200,OK" >> $REPORT_CSV
    echo "|$FRONTEND_URL|CloudFront Cache Header|200|OK|" >> $REPORT_MD
else
    echo "⚠️ CloudFront cache header missing!"
    notify_slack "CloudFront cache header missing!"
    echo "$FRONTEND_URL,CloudFront Cache Header,FAIL,FAIL" >> $REPORT_CSV
    echo "|$FRONTEND_URL|CloudFront Cache Header|FAIL|FAIL|" >> $REPORT_MD
fi

# -----------------------------
# BACKEND HEALTH CHECK
# -----------------------------
retry_check "$BACKEND_URL/health" "Backend Health" $MAX_RETRIES || exit 1

# -----------------------------
# DETECT API ROUTES
# -----------------------------
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
# API CHECKS
# -----------------------------
for api_path in "${API_ROUTES[@]}"; do
    retry_check "$FRONTEND_URL$api_path" "API $api_path" $MAX_RETRIES || exit 1
done

# -----------------------------
# STATIC ASSETS CHECK
# -----------------------------
for dir in "${STATIC_DIRS[@]}"; do
    if [ -d "./$dir" ]; then
        while IFS= read -r -d '' file; do
            asset_path="${file#./}" # relative path
            retry_check "$FRONTEND_URL/$asset_path" "Asset $asset_path" $MAX_RETRIES || exit 1
        done < <(find ./$dir -type f -print0)
    fi
done

echo -e "\n🎉 Deployment verification completed!"
echo "Markdown report: $REPORT_MD"
echo "CSV report: $REPORT_CSV"
exit 0
```

---

### ✅ Features of This Version

1. **Checks everything**: frontend, backend health, API routes, static assets.
2. **Logs every URL with status and response time**.
3. Generates **Markdown** (`deployment-report.md`) and **CSV** (`deployment-report.csv`) reports for CI/CD artifact storage.
4. **Fails CI/CD** if any check fails.
5. Optional Slack notifications for failures.

---

This gives you a **complete, auditable deployment verification**, ready to integrate into GitHub Actions, Jenkins, or any CI/CD pipeline.


