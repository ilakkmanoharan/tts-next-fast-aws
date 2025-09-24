Here’s a clear set of commands to run your `verify-deployment-full.sh` script located in the `scripts/` folder:

---

### 1️⃣ Give Execute Permission (first time only)

```bash
chmod +x ./scripts/verify-deployment-full.sh
```

---

### 2️⃣ Run the Script

```bash
./scripts/verify-deployment-full.sh
```

This will:

* Check frontend HTTPS, redirects, CloudFront headers
* Check backend health
* Validate API routes
* Validate static assets
* Crawl all internal frontend pages
* Generate Markdown, CSV, and HTML reports inside `scripts/`
* Optionally send Slack notifications for failures

---

### 3️⃣ View Reports

* Markdown report:

```bash
cat ./scripts/deployment-full-report.md
```

* CSV report:

```bash
cat ./scripts/deployment-full-report.csv
```

* Interactive HTML dashboard: open in a browser

```bash
open ./scripts/deployment-dashboard.html   # macOS
# or
xdg-open ./scripts/deployment-dashboard.html  # Linux
```

---

### 4️⃣ Optional: Run in CI/CD

In CI/CD, just call the script and it will **exit non-zero on failures**, failing the pipeline automatically:

```bash
./scripts/verify-deployment-full.sh
```

---
Here’s a clear set of commands to run your `verify-deployment-full.sh` script located in the `scripts/` folder:

---

### 1️⃣ Give Execute Permission (first time only)

```bash
chmod +x ./scripts/verify-deployment-full.sh
```

---

### 2️⃣ Run the Script

```bash
./scripts/verify-deployment-full.sh
```

This will:

* Check frontend HTTPS, redirects, CloudFront headers
* Check backend health
* Validate API routes
* Validate static assets
* Crawl all internal frontend pages
* Generate Markdown, CSV, and HTML reports inside `scripts/`
* Optionally send Slack notifications for failures

---

### 3️⃣ View Reports

* Markdown report:

```bash
cat ./scripts/deployment-full-report.md
```

* CSV report:

```bash
cat ./scripts/deployment-full-report.csv
```

* Interactive HTML dashboard: open in a browser

```bash
open ./scripts/deployment-dashboard.html   # macOS
# or
xdg-open ./scripts/deployment-dashboard.html  # Linux
```

---

### 4️⃣ Optional: Run in CI/CD

In CI/CD, just call the script and it will **exit non-zero on failures**, failing the pipeline automatically:

```bash
./scripts/verify-deployment-full.sh
```

---

Next step: We can also give you a **single command to run the script and immediately open the HTML dashboard** in your browser for quick verification.


---

You can use a **single command** to run the script and automatically open the HTML dashboard in your browser:

### macOS

```bash
./scripts/verify-deployment-full.sh && open ./scripts/deployment-dashboard.html
```

### Linux

```bash
./scripts/verify-deployment-full.sh && xdg-open ./scripts/deployment-dashboard.html
```

✅ What this does:

1. Runs the full deployment verification script.
2. Generates Markdown, CSV, and HTML reports inside `scripts/`.
3. Opens the interactive HTML dashboard in your default browser **only if the script completes successfully**.

---

Next step::: I can also give a **version that opens the dashboard even if some checks fail**, so you can inspect slow/failing pages immediately.

__

Here’s a version that **always opens the HTML dashboard**, even if some checks fail:

### macOS

```bash
./scripts/verify-deployment-full.sh; open ./scripts/deployment-dashboard.html
```

### Linux

```bash
./scripts/verify-deployment-full.sh; xdg-open ./scripts/deployment-dashboard.html
```

✅ Key differences from the previous command:

* Uses `;` instead of `&&`, so the **dashboard opens regardless of script exit status**.
* You can immediately inspect **slow or failing pages** in the HTML report without waiting for all checks to succeed.

---

Next step: We can also give a **one-liner that runs the script in the background and opens the dashboard while continuing to log progress in the terminal**—useful for long crawls.

-----

Here’s a **one-liner that runs the script in the background, streams logs, and opens the dashboard immediately**:

### macOS

```bash
nohup ./scripts/verify-deployment-full.sh > ./scripts/verify-deployment.log 2>&1 & open ./scripts/deployment-dashboard.html
```

### Linux

```bash
nohup ./scripts/verify-deployment-full.sh > ./scripts/verify-deployment.log 2>&1 & xdg-open ./scripts/deployment-dashboard.html
```

✅ What this does:

1. Runs the deployment verification script **in the background** (`nohup ... &`).
2. Streams all logs to `./scripts/verify-deployment.log` (so you can check progress anytime).
3. Immediately opens the interactive HTML dashboard in your default browser.
4. Allows you to **inspect pages while the crawl or checks are still running**.

---

Next ste: We can also give a **version that auto-refreshes the HTML dashboard every few seconds** so you can watch slow/failing pages appear in real time.



