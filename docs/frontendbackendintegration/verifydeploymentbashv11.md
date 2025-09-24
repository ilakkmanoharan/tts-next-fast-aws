Let’s combine **everything** into a **single, comprehensive deployment verification script** that:

1. Checks **frontend homepage and HTTPS**.
2. Validates **HTTP → HTTPS redirect**.
3. Checks **CloudFront caching headers**.
4. Validates **backend health**.
5. Tests **Next.js API routes**.
6. Validates **all static assets** (`public/` and `.next/static/`).
7. **Crawls all internal frontend pages** and validates links.
8. Generates **Markdown and CSV reports** for all checks.
9. Optional **Slack notifications** for failures.
10. Fails CI/CD if any critical check fails.

Here’s the **all-in-one script**:

```bash
#!/bin/bash

# -----------------------------
# CONFIGURATION
# -----------------------------
ENV_FILE="./.env.local"
FRONTEND_URL="https://dpy3jeqrdnvsx.cloudfront.net"
MAX_RETRIES=3
SLEEP_INTERVAL=3
SLACK_WEBHOOK_URL="" # optional Slack webhook
STATIC_DIRS=("public" ".next/static")
REPORT_MD="deployment-full-report.md"
REPORT_CSV="deployment-full-report.csv"

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
    local attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}" $url)
        if [ "$HTTP_STATUS" -eq 200 ]; then
            echo "✅ $description: $HTTP_STATUS (Attempt $attempt)"
            echo "$url,$description,200" >> $REPORT_CSV
            echo "|$url|$description|200|" >> $REPORT_MD
            return 0
        else
            echo "⚠️ $description failed: $HTTP_STATUS (Attempt $attempt)"
            if [ $attempt -lt $MAX_RETRIES ]; then
                sleep $SLEEP_INTERVAL
            fi
        fi
        attempt=$((attempt + 1))
    done
    echo "❌ $description not reachable!"
    notify_slack "$description not reachable!"
    echo "$url,$description,$HTTP_STATUS" >> $REPORT_CSV
    echo "|$url|$description|$HTTP_STATUS|" >> $REPORT_MD
    return 1
}

# -----------------------------
# INIT REPORT FILES
# -----------------------------
echo "|URL|Description|HTTP Status|" > $REPORT_MD
echo "|---|---|---|" >> $REPORT_MD
echo "URL,Description,HTTP Status" > $REPORT_CSV

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
retry_check "$FRONTEND_URL" "Frontend Home Page" || exit 1

# HTTP → HTTPS redirect check
REDIRECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${FRONTEND_URL#https://}")
if [[ "$REDIRECT_STATUS" == 301 || "$REDIRECT_STATUS" == 308 ]]; then
    echo "✅ HTTP redirects to HTTPS: $REDIRECT_STATUS"
    echo "$FRONTEND_URL,Redirect to HTTPS,$REDIRECT_STATUS" >> $REPORT_CSV
    echo "|$FRONTEND_URL|Redirect to HTTPS|$REDIRECT_STATUS|" >> $REPORT_MD
else
    echo "⚠️ HTTP redirect missing: $REDIRECT_STATUS"
    notify_slack "HTTP redirect missing!"
    echo "$FRONTEND_URL,Redirect to HTTPS,$REDIRECT_STATUS" >> $REPORT_CSV
    echo "|$FRONTEND_URL|Redirect to HTTPS|$REDIRECT_STATUS|" >> $REPORT_MD
fi

# CloudFront cache header
CACHE_HEADER=$(curl -s -D - -o /dev/null $FRONTEND_URL | grep -i "x-cache")
if [ -n "$CACHE_HEADER" ]; then
    echo "✅ CloudFront cache header: $CACHE_HEADER"
    echo "$FRONTEND_URL,CloudFront Cache Header,200" >> $REPORT_CSV
    echo "|$FRONTEND_URL|CloudFront Cache Header|200|" >> $REPORT_MD
else
    echo "⚠️ CloudFront cache header missing!"
    notify_slack "CloudFront cache header missing!"
    echo "$FRONTEND_URL,CloudFront Cache Header,FAIL" >> $REPORT_CSV
    echo "|$FRONTEND_URL|CloudFront Cache Header|FAIL|" >> $REPORT_MD
fi

# -----------------------------
# BACKEND HEALTH
# -----------------------------
retry_check "$BACKEND_URL/health" "Backend Health" || exit 1

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
    retry_check "$FRONTEND_URL$api_path" "API $api_path" || exit 1
done

# -----------------------------
# STATIC ASSETS CHECK
# -----------------------------
for dir in "${STATIC_DIRS[@]}"; do
    if [ -d "./$dir" ]; then
        while IFS= read -r -d '' file; do
            asset_path="${file#./}"
            retry_check "$FRONTEND_URL/$asset_path" "Asset $asset_path" || exit 1
        done < <(find ./$dir -type f -print0)
    fi
done

# -----------------------------
# FRONTEND CRAWL (all internal links)
# -----------------------------
echo -e "\n🔎 Crawling frontend for internal links..."
VISITED=()
TO_VISIT=("$FRONTEND_URL")

while [ ${#TO_VISIT[@]} -gt 0 ]; do
    CURRENT=${TO_VISIT[0]}
    TO_VISIT=("${TO_VISIT[@]:1}")

    if [[ " ${VISITED[@]} " =~ " ${CURRENT} " ]]; then
        continue
    fi
    VISITED+=("$CURRENT")

    retry_check "$CURRENT" "Page Check" || continue

    # Extract internal links
    LINKS=$(curl -s $CURRENT | grep -Eo '<a [^>]+>' | grep -Eo 'href="[^"]+"' | cut -d'"' -f2)
    for link in $LINKS; do
        if [[ "$link" == /* ]]; then
            FULL_LINK="$FRONTEND_URL$link"
            if [[ ! " ${VISITED[@]} " =~ " ${FULL_LINK} " && ! " ${TO_VISIT[@]} " =~ " ${FULL_LINK} " ]]; then
                TO_VISIT+=("$FULL_LINK")
            fi
        fi
    done
done

echo -e "\n🎉 Full deployment verification completed!"
echo "Markdown report: $REPORT_MD"
echo "CSV report: $REPORT_CSV"
exit 0
```

---

### ✅ What This Script Does

1. Frontend HTTPS + redirects + CloudFront caching headers
2. Backend health check
3. Next.js API routes verification
4. All static assets verification (`public/` & `.next/static/`)
5. Full **internal link crawl** to catch broken pages
6. Logs everything in **Markdown** and **CSV** for CI/CD or audits
7. Optional Slack notifications for failures
8. Exits with non-zero code if any critical check fails

---

This is now a **complete deployment verification pipeline**.


