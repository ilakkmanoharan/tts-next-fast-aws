Let’s enhance your HTML dashboard to **group by type**—Frontend Pages, API Routes, and Static Assets—with **collapsible sections** for easier navigation in large reports.

Here’s the updated **enterprise dashboard generator**:

```bash
#!/bin/bash

# -----------------------------
# CONFIG
# -----------------------------
REPORT_JSON="deployment-enterprise-report.json"
DASHBOARD_HTML="deployment-dashboard-collapsible.html"

# -----------------------------
# BEGIN HTML
# -----------------------------
cat <<EOL > $DASHBOARD_HTML
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Deployment Verification Dashboard</title>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
  h1 { text-align: center; }
  table { width: 100%; border-collapse: collapse; margin-top: 10px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background-color: #333; color: white; }
  tr:nth-child(even) { background-color: #f2f2f2; }
  tr.failed { background-color: #f8d7da; }
  tr.slow { background-color: #fff3cd; }
  a { color: #0066cc; text-decoration: none; }
  summary { font-size: 1.1em; font-weight: bold; margin-top: 10px; }
</style>
</head>
<body>
<h1>Deployment Verification Dashboard</h1>
<p>Legend: <span style="background-color:#fff3cd;">Slow (>3s)</span>, <span style="background-color:#f8d7da;">Failed</span></p>
EOL

# -----------------------------
# FUNCTION TO ADD TABLES
# -----------------------------
add_table() {
    local type=$1
    echo "<details open><summary>$type</summary>" >> $DASHBOARD_HTML
    echo "<table>" >> $DASHBOARD_HTML
    echo "<thead><tr><th>URL</th><th>Description</th><th>Status</th><th>Response Time (s)</th></tr></thead>" >> $DASHBOARD_HTML
    echo "<tbody>" >> $DASHBOARD_HTML

    jq -c ".[] | select(.description | test(\"$type\"))" $REPORT_JSON | while read row; do
        URL=$(echo $row | jq -r '.url')
        DESC=$(echo $row | jq -r '.description')
        STATUS=$(echo $row | jq -r '.status')
        TIME=$(echo $row | jq -r '.response_time')
        CLASS=""

        if [ "$STATUS" != "200" ] || [ "$TIME" == "null" ]; then
            CLASS="failed"
            TIME="FAIL"
        elif (( $(echo "$TIME > 3" | bc -l) )); then
            CLASS="slow"
        fi

        echo "<tr class=\"$CLASS\">" >> $DASHBOARD_HTML
        echo "<td><a href=\"$URL\" target=\"_blank\">$URL</a></td>" >> $DASHBOARD_HTML
        echo "<td>$DESC</td>" >> $DASHBOARD_HTML
        echo "<td>$STATUS</td>" >> $DASHBOARD_HTML
        echo "<td>$TIME</td>" >> $DASHBOARD_HTML
        echo "</tr>" >> $DASHBOARD_HTML
    done

    echo "</tbody></table></details>" >> $DASHBOARD_HTML
}

# -----------------------------
# GENERATE TABLES
# -----------------------------
add_table "Frontend"
add_table "API"
add_table "Asset"

# -----------------------------
# END HTML
# -----------------------------
cat <<EOL >> $DASHBOARD_HTML
</body>
</html>
EOL

echo "🎉 Collapsible dashboard generated: $DASHBOARD_HTML"
```

---

### ✅ Dashboard Features Now

1. **Collapsible sections**

   * Frontend Pages
   * API Routes
   * Static Assets

2. **Color-coded rows**

   * Red = failed/broken page or asset
   * Yellow = slow (>3 seconds)

3. **Clickable links** for quick access

4. **Audit-ready** for CI/CD or team review

5. **Legend** visible at the top

---

This version is **much easier to navigate** for large deployments with hundreds of assets or API endpoints.

Next step: We can also make it **interactive with search and sorting per column**, so you can **filter by slow pages, failures, or specific paths** directly in the browser.


