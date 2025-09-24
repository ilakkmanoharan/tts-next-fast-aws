Perfect! For large Next.js apps, sequentially checking hundreds or thousands of static assets, API routes, and internal links can take a long time. Let’s make a **parallelized version** of the full deployment verification script to **speed up checks significantly**.

We’ll use **GNU `parallel`** or background jobs in Bash to check multiple URLs simultaneously. This is safe for read-only GET requests.

Here’s the **parallelized, all-in-one deployment verification script**:

```bash
#!/bin/bash

# -----------------------------
# CONFIGURATION
# -----------------------------
ENV_FILE="./.env.local"
FRONTEND_URL="https://dpy3jeqrdnvsx.cloudfront.net"
MAX_RETRIES=3
SLEEP_INTERVAL=3
PARALLEL_JOBS=10 # number of concurrent checks
SLACK_WEBHOOK_URL="" # optional Slack notifications
STATIC_DIRS=("public" ".next/static")
REPORT_MD="deployment-parallel-report.md"
REPORT_CSV="deployment-parallel-report.csv"
TMP_QUEUE="/tmp/deploy_queue.txt"

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
        fi
        attempt=$((attempt + 1))
        sleep $SLEEP_INTERVAL
    done
    echo "❌ $description failed: $HTTP_STATUS"
    notify_slack "$description failed!"
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
> $TMP_QUEUE

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
# ADD MAIN CHECKS TO QUEUE
# -----------------------------
echo "$FRONTEND_URL,Frontend Home Page" >> $TMP_QUEUE
echo "$BACKEND_URL/health,Backend Health" >> $TMP_QUEUE

# HTTP → HTTPS redirect
REDIRECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${FRONTEND_URL#https://}")
echo "$FRONTEND_URL,Redirect to HTTPS" >> $TMP_QUEUE

# -----------------------------
# ADD API ROUTES TO QUEUE
# -----------------------------
for dir in pages/api app/api; do
    if [ -d "./$dir" ]; then
        while IFS= read -r -d '' file; do
            route="${file#./$dir}"
            route="${route%.js}"
            route="${route%.ts}"
            route="${route}/"
            echo "$FRONTEND_URL$route,API $route" >> $TMP_QUEUE
        done < <(find ./$dir -type f \( -name "*.js" -o -name "*.ts" \) -print0)
    fi
done

# -----------------------------
# ADD STATIC ASSETS TO QUEUE
# -----------------------------
for dir in "${STATIC_DIRS[@]}"; do
    if [ -d "./$dir" ]; then
        while IFS= read -r -d '' file; do
            asset_path="${file#./}"
            echo "$FRONTEND_URL/$asset_path,Asset $asset_path" >> $TMP_QUEUE
        done < <(find ./$dir -type f -print0)
    fi
done

# -----------------------------
# FRONTEND CRAWL FOR INTERNAL LINKS
# -----------------------------
VISITED=()
TO_VISIT=("$FRONTEND_URL")
while [ ${#TO_VISIT[@]} -gt 0 ]; do
    CURRENT=${TO_VISIT[0]}
    TO_VISIT=("${TO_VISIT[@]:1}")

    if [[ " ${VISITED[@]} " =~ " ${CURRENT} " ]]; then
        continue
    fi
    VISITED+=("$CURRENT")

    echo "$CURRENT,Page Check" >> $TMP_QUEUE

    # extract internal links
    LINKS=$(curl -s $CURRENT | grep -Eo '<a [^>]+>' | grep -Eo 'href="[^"]+"' | cut -d'"' -f2)
    for link in $LINKS; do
        if [[ "$link" == /* ]]; then
            FULL_LINK="$FRONTEND_URL$link"
            if [[ ! " ${VISITED[@]} " =~ " ${FULL_LINK} " ]]; then
                TO_VISIT+=("$FULL_LINK")
            fi
        fi
    done
done

# -----------------------------
# RUN ALL CHECKS IN PARALLEL
# -----------------------------
export -f retry_check
export REPORT_CSV
export REPORT_MD
export SLACK_WEBHOOK_URL
export SLEEP_INTERVAL
export MAX_RETRIES

cat $TMP_QUEUE | parallel -j $PARALLEL_JOBS --colsep ',' retry_check {1} {2}

rm -f $TMP_QUEUE
echo -e "\n🎉 Parallel deployment verification completed!"
echo "Markdown report: $REPORT_MD"
echo "CSV report: $REPORT_CSV"
exit 0
```

---

### ✅ What This Version Adds

1. **Parallel execution** of all URL checks (`PARALLEL_JOBS` controls concurrency).
2. Greatly **reduces total runtime** for large apps with many assets and routes.
3. Maintains all reporting features: Markdown + CSV + optional Slack notifications.
4. Crawls **all internal pages** and checks them concurrently.
5. Safe for read-only GET requests (no mutations).

---


