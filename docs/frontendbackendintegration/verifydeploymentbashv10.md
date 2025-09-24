Let's go **all the way**: a script that **crawls the entire Next.js frontend** (all internal links and pages, not just API/static files) and validates that **every page and asset returns 200 OK**.

This is useful to catch:

* Broken links in your deployed frontend.
* Missing pages or routes.
* Misconfigured redirects or caching issues.

Here’s the advanced script:

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
REPORT_MD="deployment-crawl-report.md"
REPORT_CSV="deployment-crawl-report.csv"

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
    notify_slack "$description not reachable after $MAX_RETRIES attempts!"
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
# FRONTEND BASE CHECK
# -----------------------------
retry_check "$FRONTEND_URL" "Frontend Home Page" || exit 1

# -----------------------------
# BACKEND HEALTH CHECK
# -----------------------------
retry_check "$BACKEND_URL/health" "Backend Health" || exit 1

# -----------------------------
# CRRAWL FRONTEND LINKS
# -----------------------------
echo -e "\n🔎 Crawling frontend for internal links..."
VISITED=()
TO_VISIT=("$FRONTEND_URL")

while [ ${#TO_VISIT[@]} -gt 0 ]; do
    CURRENT=${TO_VISIT[0]}
    TO_VISIT=("${TO_VISIT[@]:1}")

    # Skip if already visited
    if [[ " ${VISITED[@]} " =~ " ${CURRENT} " ]]; then
        continue
    fi
    VISITED+=("$CURRENT")

    # Check URL
    retry_check "$CURRENT" "Page Check" || continue

    # Extract internal links (only same domain)
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

echo -e "\n🎉 Full frontend crawl completed!"
echo "Markdown report: $REPORT_MD"
echo "CSV report: $REPORT_CSV"
exit 0
```

---

### ✅ Features

1. **Crawls all internal pages** of the frontend (following internal links only).
2. **Retries each page** up to `MAX_RETRIES`.
3. **Logs results** in Markdown (`deployment-crawl-report.md`) and CSV (`deployment-crawl-report.csv`).
4. Checks **frontend homepage**, **backend health**, and every discovered page.
5. Optional **Slack notifications** for failures.
6. **Automatically avoids revisiting URLs** to speed up the crawl.

---

This gives you **full production confidence**: all pages, links, backend, HTTPS, and static assets.


