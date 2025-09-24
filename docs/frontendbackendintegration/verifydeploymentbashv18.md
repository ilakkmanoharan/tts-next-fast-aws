Let’s extend your all-in-one deployment verification script to also **generate an interactive HTML dashboard** and save it inside the `scripts/` folder. Here’s the updated version:

```bash
#!/bin/bash

# -----------------------------
# CONFIGURATION
# -----------------------------
SCRIPTS_DIR="./scripts"
ENV_FILE="./.env.local"
FRONTEND_URL="https://dpy3jeqrdnvsx.cloudfront.net"
MAX_RETRIES=3
SLEEP_INTERVAL=3
SLACK_WEBHOOK_URL="" # optional Slack webhook
STATIC_DIRS=("public" ".next/static")
REPORT_MD="$SCRIPTS_DIR/deployment-full-report.md"
REPORT_CSV="$SCRIPTS_DIR/deployment-full-report.csv"
DASHBOARD_HTML="$SCRIPTS_DIR/deployment-dashboard.html"

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
# ENSURE SCRIPTS DIR EXISTS
# -----------------------------
mkdir -p "$SCRIPTS_DIR"

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

# -----------------------------
# GENERATE INTERACTIVE HTML DASHBOARD
# -----------------------------
echo -e "\n🎨 Generating interactive HTML dashboard..."
cat > $DASHBOARD_HTML <<EOL
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Deployment Dashboard</title>
<style>
body { font-family: Arial, sans-serif; padding: 20px; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { cursor: pointer; background-color: #f4f4f4; }
tr:nth-child(even){background-color: #f9f9f9;}
tr.failed { background-color: #f8d7da; }
tr.slow { background-color: #fff3cd; }
</style>
</head>
<body>
<h1>Deployment Verification Dashboard</h1>
<input type="text" id="searchInput" placeholder="Search..." onkeyup="filterTable()">
<table id="reportTable">
<thead>
<tr>
<th onclick="sortTable(0)">URL</th>
<th onclick="sortTable(1)">Description</th>
<th onclick="sortTable(2)">HTTP Status</th>
</tr>
</thead>
<tbody>
EOL

# Add table rows from CSV
tail -n +2 $REPORT_CSV | while IFS=, read -r url desc status; do
    class=""
    if [[ "$status" != "200" ]]; then
        class="failed"
    fi
    echo "<tr class='$class'><td><a href='$url' target='_blank'>$url</a></td><td>$desc</td><td>$status</td></tr>" >> $DASHBOARD_HTML
done

cat >> $DASHBOARD_HTML <<'EOL'
</tbody>
</table>
<script>
function sortTable(n) {
  var table=document.getElementById("reportTable"), rows, switching, i, x, y, shouldSwitch, dir, switchcount=0;
  switching=true; dir="asc";
  while(switching){ switching=false; rows=table.rows;
    for(i=1;i<rows.length-1;i++){ shouldSwitch=false;
      x=rows[i].getElementsByTagName("TD")[n];
      y=rows[i+1].getElementsByTagName("TD")[n];
      if(dir=="asc"){ if(x.innerHTML.toLowerCase()>y.innerHTML.toLowerCase()){ shouldSwitch=true; break;} }
      else if(dir=="desc"){ if(x.innerHTML.toLowerCase()<y.innerHTML.toLowerCase()){ shouldSwitch=true; break;} }
    }
    if(shouldSwitch){ rows[i].parentNode.insertBefore(rows[i+1],rows[i]); switching=true; switchcount++; }
    else{ if(switchcount==0 && dir=="asc"){ dir="desc"; switching=true; } }
  }
}
function filterTable() {
  var input=document.getElementById("searchInput"), filter=input.value.toLowerCase(), table=document.getElementById("reportTable"), tr=table.getElementsByTagName("tr");
  for(var i=1;i<tr.length;i++){ var td=tr[i].getElementsByTagName("td"); var show=false;
    for(var j=0;j<td.length;j++){ if(td[j].innerHTML.toLowerCase().indexOf(filter)>-1){ show=true; } }
    tr[i].style.display=show?"":"none";
  }
}
</script>
</body>
</html>
EOL

echo -e "\n🎉 Full deployment verification completed!"
echo "Markdown report: $REPORT_MD"
echo "CSV report: $REPORT_CSV"
echo "Interactive HTML dashboard: $DASHBOARD_HTML"
exit 0
```

---

### ✅ What This Updated Script Does

1. Performs **all previous checks** (frontend, HTTPS redirect, CloudFront headers, backend health, API routes, static assets, and internal link crawl).
2. Saves **all reports in `scripts/`**:

```
scripts/deployment-full-report.md
scripts/deployment-full-report.csv
scripts/deployment-dashboard.html
```

3. Generates a **browser-friendly interactive dashboard** with:

* Search box
* Sortable columns
* Color-coded failed rows
* Clickable links

4. Slack notifications remain optional.
5. CI/CD friendly: exits non-zero on critical failures.

---

You can now run everything in one step from the project root:

```bash
./scripts/verify-deployment-full.sh
```

And all QA artifacts remain neatly inside `scripts/`.

---

Next step: We can also **add a performance threshold** (e.g., highlight pages/API calls taking more than 3 seconds) to the HTML dashboard.

