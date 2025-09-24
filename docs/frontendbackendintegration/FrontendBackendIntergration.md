Great! 🚀 Let’s make a **full checklist + automated test script** so you can quickly verify that your frontend and backend are wired up correctly without manually poking around.

---

# ✅ Frontend–Backend Integration Checklist

### 1. **Frontend Deployment Check**

* [ ] Open CloudFront URL:
  👉 `https://dpy3jeqrdnvsx.cloudfront.net`
* [ ] Ensure it loads without **403/404 errors**.
* [ ] Confirm static assets load (CSS/JS in dev tools → Network tab).

---

### 2. **Backend URL Environment Variable**

* [ ] Verify `.env.local` in frontend contains:

  ```
  NEXT_PUBLIC_BACKEND_URL=http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com
  ```
* [ ] Confirm the frontend code **uses this env var** in API calls (e.g., `fetch(`\${process.env.NEXT\_PUBLIC\_BACKEND\_URL}/api/...`)`).

---

### 3. **API Integration Test via Browser**

* [ ] Open **DevTools → Network tab**.
* [ ] Trigger an action in the frontend (button, form, etc.).
* [ ] Verify requests go to **ALB URL** and not localhost.
* [ ] Check responses are `200 OK` and return correct JSON.

---

### 4. **Direct Backend Health Check**

Run in terminal:

```bash
curl http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com/health
```

Expected:

```json
{"status":"ok"}
```

---

### 5. **End-to-End Automated Test Script**

Here’s a Node.js script you can drop into your project (e.g., `verify-deployment.js`) and run with `node verify-deployment.js`:

```javascript
import fetch from "node-fetch";

const FRONTEND_URL = "https://dpy3jeqrdnvsx.cloudfront.net";
const BACKEND_URL =
  "http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com";

async function checkFrontend() {
  console.log("🔎 Checking frontend...");
  try {
    const res = await fetch(FRONTEND_URL);
    if (res.ok) {
      console.log(`✅ Frontend reachable: ${res.status}`);
    } else {
      console.error(`❌ Frontend error: ${res.status}`);
    }
  } catch (err) {
    console.error("❌ Frontend not reachable:", err.message);
  }
}

async function checkBackend() {
  console.log("\n🔎 Checking backend...");
  try {
    const res = await fetch(`${BACKEND_URL}/health`);
    const text = await res.text();
    if (res.ok) {
      console.log(`✅ Backend reachable: ${res.status}, response: ${text}`);
    } else {
      console.error(`❌ Backend error: ${res.status}, response: ${text}`);
    }
  } catch (err) {
    console.error("❌ Backend not reachable:", err.message);
  }
}

async function checkIntegration() {
  console.log("\n🔎 Checking frontend-backend integration...");
  try {
    // Adjust path to match your API endpoint
    const res = await fetch(`${FRONTEND_URL}/api/test`);
    const text = await res.text();
    if (res.ok) {
      console.log(`✅ Integration OK: ${res.status}, response: ${text}`);
    } else {
      console.error(`❌ Integration error: ${res.status}, response: ${text}`);
    }
  } catch (err) {
    console.error("❌ Integration failed:", err.message);
  }
}

(async () => {
  await checkFrontend();
  await checkBackend();
  await checkIntegration();
})();
```

---

### 6. **Optional Improvements**

* [ ] Add HTTPS (ACM certificate + CloudFront).
* [ ] Set up a **custom domain** → CloudFront (instead of cloudfront.net).
* [ ] Enable **CloudFront + ALB logs** for observability.
* [ ] Add script into **CI/CD pipeline** to automatically verify after deploys.

---

