Let’s take the dashboard to the next level with **interactive search and sortable columns**. This will allow you to:

* Filter by slow pages, failed pages, or any URL/description.
* Sort by status, response time, or URL.
* Keep collapsible sections for Frontend, API, and Assets.

Here’s the **fully interactive HTML dashboard generator**:

```bash
#!/bin/bash

# -----------------------------
# CONFIG
# -----------------------------
REPORT_JSON="deployment-enterprise-report.json"
DASHBOARD_HTML="deployment-dashboard-interactive.html"

# -----------------------------
# BEGIN HTML
# -----------------------------
cat <<EOL > $DASHBOARD_HTML
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Interactive Deployment Verification Dashboard</title>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
  h1 { text-align: center; }
  table { width: 100%; border-collapse: collapse; margin-top: 10px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background-color: #333; color: white; cursor: pointer; }
  tr:nth-child(even) { background-color: #f2f2f2; }
  tr.failed { background-color: #f8d7da; }
  tr.slow { background-color: #fff3cd; }
  a { color: #0066cc; text-decoration: none; }
  summary { font-size: 1.1em; font-weight: bold; margin-top: 10px; }
  input.search { margin-bottom: 10px; padding: 5px; width: 300px; }
</style>
</head>
<body>
<h1>Interactive Deployment Verification Dashboard</h1>
<p>Legend: <span style="background-color:#fff3cd;">Slow (>3s)</span>, <span style="background-color:#f8d7da;">Failed</span></p>
EOL

# -----------------------------
# FUNCTION TO ADD TABLES
# -----------------------------
add_table_interactive() {
    local type=$1
    echo "<details open><summary>$type</summary>" >> $DASHBOARD_HTML
    echo "<input class='search' type='text' placeholder='Search $type...' onkeyup='filterTable(this, \"$type\")'>" >> $DASHBOARD_HTML
    echo "<table id=\"$type\">" >> $DASHBOARD_HTML
    echo "<thead><tr>" >> $DASHBOARD_HTML
    echo "<th onclick='sortTable(\"$type\", 0)'>URL</th>" >> $DASHBOARD_HTML
    echo "<th onclick='sortTable(\"$type\", 1)'>Description</th>" >> $DASHBOARD_HTML
    echo "<th onclick='sortTable(\"$type\", 2)'>Status</th>" >> $DASHBOARD_HTML
    echo "<th onclick='sortTable(\"$type\", 3)'>Response Time (s)</th>" >> $DASHBOARD_HTML
    echo "</tr></thead><tbody>" >> $DASHBOARD_HTML

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
add_table_interactive "Frontend"
add_table_interactive "API"
add_table_interactive "Asset"

# -----------------------------
# ADD JS FOR SEARCH + SORT
# -----------------------------
cat <<'EOL' >> $DASHBOARD_HTML
<script>
function filterTable(input, type) {
    var filter = input.value.toLowerCase();
    var table = document.getElementById(type);
    var tr = table.getElementsByTagName("tr");
    for (var i = 1; i < tr.length; i++) {
        var tds = tr[i].getElementsByTagName("td");
        var show = false;
        for (var j = 0; j < tds.length; j++) {
            if (tds[j].innerText.toLowerCase().indexOf(filter) > -1) {
                show = true; break;
            }
        }
        tr[i].style.display = show ? "" : "none";
    }
}

function sortTable(type, col) {
    var table = document.getElementById(type);
    var rows = Array.from(table.rows).slice(1);
    var asc = table.asc = !table.asc;
    rows.sort(function(a,b){
        var x = a.cells[col].innerText.toLowerCase();
        var y = b.cells[col].innerText.toLowerCase();
        if(!isNaN(parseFloat(x)) && !isNaN(parseFloat(y))) {
            return asc ? x - y : y - x;
        }
        return asc ? x.localeCompare(y) : y.localeCompare(x);
    });
    for(var i = 0; i < rows.length; i++) table.appendChild(rows[i]);
}
</script>
</body>
</html>
EOL

echo "🎉 Interactive dashboard generated: $DASHBOARD_HTML"
```

---

### ✅ Features Added

1. **Search box per section**

   * Filter by URL, description, status, or response time.

2. **Sortable columns**

   * Click column headers to sort ascending/descending.
   * Works for URL, Description, Status, and Response Time.

3. **Collapsible sections remain**

   * Frontend, API, Assets

4. **Color-coded rows**

   * Red = failed
   * Yellow = slow (>3s)

5. **Clickable links** to open pages/assets directly.

---

This gives you a **full interactive QA dashboard** for your deployment that’s **easy to navigate and share** with your team.

Next step: We can **also integrate performance graphs** (like a small bar chart showing response times per page/API) directly into this dashboard for an at-a-glance visual performance overview.

