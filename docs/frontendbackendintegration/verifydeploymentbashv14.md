Let’s create a **visual HTML dashboard** for your enterprise deployment verification report. This dashboard will make it easy to **see status, slow pages, broken assets, and API results at a glance**.

Here’s a complete example script that **generates the HTML dashboard** from your JSON report (`deployment-enterprise-report.json`):

```bash
#!/bin/bash

# -----------------------------
# CONFIG
# -----------------------------
REPORT_JSON="deployment-enterprise-report.json"
DASHBOARD_HTML="deployment-dashboard.html"

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
  table { width: 100%; border-collapse: collapse; margin-top: 20px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background-color: #333; color: white; }
  tr:nth-child(even) { background-color: #f2f2f2; }
  tr.failed { background-color: #f8d7da; }
  tr.slow { background-color: #fff3cd; }
  a { color: #0066cc; text-decoration: none; }
</style>
</head>
<body>
<h1>Deployment Verification Dashboard</h1>
<table>
  <thead>
    <tr>
      <th>URL</th>
      <th>Description</th>
      <th>Status</th>
      <th>Response Time (s)</th>
    </tr>
  </thead>
  <tbody>
EOL

# -----------------------------
# ADD ROWS
# -----------------------------
jq -c '.[]' $REPORT_JSON | while read row; do
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

# -----------------------------
# END HTML
# -----------------------------
cat <<EOL >> $DASHBOARD_HTML
  </tbody>
</table>
<p>Legend: <span style="background-color:#f8d7cd;">Slow</span>, <span style="background-color:#f8d7da;">Failed</span></p>
</body>
</html>
EOL

echo "🎉 Dashboard generated: $DASHBOARD_HTML"
```

---

### ✅ Dashboard Features

1. **Color-coded rows**:

   * Red = failed/broken page or asset
   * Yellow = slow (>3 seconds)

2. **Clickable links**: Open any page, API, or asset directly from the dashboard.

3. **Sections in one table**: All frontend pages, API routes, and static assets together.

4. **Legend included**: Easily see slow vs failed resources.

5. **Ready for CI/CD or sharing**: Can be opened in any browser, or hosted on S3/CloudFront.

---


Perfect! Let’s create a **visual HTML dashboard** for your enterprise deployment verification report. This dashboard will make it easy to **see status, slow pages, broken assets, and API results at a glance**.

Here’s a complete example script that **generates the HTML dashboard** from your JSON report (`deployment-enterprise-report.json`):

```bash
#!/bin/bash

# -----------------------------
# CONFIG
# -----------------------------
REPORT_JSON="deployment-enterprise-report.json"
DASHBOARD_HTML="deployment-dashboard.html"

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
  table { width: 100%; border-collapse: collapse; margin-top: 20px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background-color: #333; color: white; }
  tr:nth-child(even) { background-color: #f2f2f2; }
  tr.failed { background-color: #f8d7da; }
  tr.slow { background-color: #fff3cd; }
  a { color: #0066cc; text-decoration: none; }
</style>
</head>
<body>
<h1>Deployment Verification Dashboard</h1>
<table>
  <thead>
    <tr>
      <th>URL</th>
      <th>Description</th>
      <th>Status</th>
      <th>Response Time (s)</th>
    </tr>
  </thead>
  <tbody>
EOL

# -----------------------------
# ADD ROWS
# -----------------------------
jq -c '.[]' $REPORT_JSON | while read row; do
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

# -----------------------------
# END HTML
# -----------------------------
cat <<EOL >> $DASHBOARD_HTML
  </tbody>
</table>
<p>Legend: <span style="background-color:#f8d7cd;">Slow</span>, <span style="background-color:#f8d7da;">Failed</span></p>
</body>
</html>
EOL

echo "🎉 Dashboard generated: $DASHBOARD_HTML"
```

---

### ✅ Dashboard Features

1. **Color-coded rows**:

   * Red = failed/broken page or asset
   * Yellow = slow (>3 seconds)

2. **Clickable links**: Open any page, API, or asset directly from the dashboard.

3. **Sections in one table**: All frontend pages, API routes, and static assets together.

4. **Legend included**: Easily see slow vs failed resources.

5. **Ready for CI/CD or sharing**: Can be opened in any browser, or hosted on S3/CloudFront.

---

Next step (optional): We can extend this dashboard to **group by type**—Frontend Pages / API / Static Assets—and **collapsible sections** so large reports are easier to navigate.


