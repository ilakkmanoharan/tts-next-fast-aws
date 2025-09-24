#AWS COPILOT SETUP GUIDE

**step-by-step instructions** for deploying both your **frontend** and **backend** using **AWS** with ECS/Fargate, CloudFront, and optionally Route 53. I’ll include commands you can run on **Mac/VS Code** and Copilot CLI.

---

## **Assumptions**

* You have **AWS CLI** installed and configured.
* You have **Copilot CLI** installed.
* Your **frontend** is built (e.g., React/Vite/Next.js) and backend is a Dockerized Node.js/Python/Go app.
* Domain is optional; if you have a custom domain, we can configure Route 53 & ACM.

---

# **Step 1: Backend Deployment (ECS + Fargate)**

### **1. Initialize Copilot App**

```bash
# Create a Copilot app
copilot app init tts-next-app
```

### **2. Create a Backend Service**

```bash
# Initialize a backend service
copilot svc init --name backend --svc-type "Load Balanced Web Service" --dockerfile ./backend/Dockerfile
```

* **Options explained:**

  * `--svc-type "Load Balanced Web Service"` → creates ALB with Fargate tasks.
  * `--dockerfile ./backend/Dockerfile` → path to your Dockerfile.

---

### **3. Deploy Backend Service**

```bash
# Deploy to dev environment
copilot env init --name dev --profile default --default-config
copilot svc deploy --name backend --env dev
```

* Copilot creates:

  * ECS Fargate service
  * ALB + target group
  * Security groups
  * CloudWatch log group

---

### **4. Check Logs if Tasks Fail**

```bash
copilot svc logs --name backend --env dev --follow
```

* If tasks **fail ELB health checks**, check:

  1. Your backend listens on the **port exposed in Dockerfile**.
  2. Health check path matches your backend route (e.g., `/health`).
  3. Security group allows traffic on backend port.

---

# **Step 2: Frontend Deployment (Static site on S3 + CloudFront)**

### **1. Build Frontend**

```bash
# React / Vite / Next.js build
cd frontend
npm install
npm run build
```

* Output goes to `frontend/dist` (Vite) or `frontend/build` (React).

---

### **2. Create S3 Bucket**

```bash
aws s3 mb s3://tts-next-frontend --region us-east-1
```

* Enable **static website hosting**:

```bash
aws s3 website s3://tts-next-frontend/ --index-document index.html --error-document index.html
```

---

### **3. Upload Build to S3**

```bash
aws s3 sync build/ s3://tts-next-frontend --delete
```

* Replace `build/` with your frontend build folder.

---

### **4. Setup CloudFront (Optional HTTPS)**

```bash
aws cloudfront create-distribution \
  --origin-domain-name tts-next-frontend.s3.amazonaws.com \
  --default-root-object index.html
```

* If you have a **custom domain**:

  * Request an SSL certificate via **ACM**:

  ```bash
  aws acm request-certificate --domain-name yourdomain.com --validation-method DNS --region us-east-1
  ```

  * Update CloudFront distribution to use your **custom domain** and certificate.

---

### **5. Configure Backend URL**

* Update frontend API calls to point to the **backend ALB URL** provided by Copilot:

```
http://<backend-alb>.us-east-1.elb.amazonaws.com
```

---

# **Step 3: Domain Setup (Optional)**

* Create a hosted zone in **Route 53**.
* Create **A Record** → point to CloudFront distribution.
* Validate ACM certificate for HTTPS.

---

# **Step 4: Verify**

1. Backend: `curl http://<backend-alb>.us-east-1.elb.amazonaws.com/health`
2. Frontend: `https://<cloudfront-url>` or `https://<yourdomain.com>`

---

# **Step 5: Troubleshooting**

* Backend task stops:

```bash
copilot svc logs --previous
```

* Health check fails → ensure **Dockerfile exposes correct port** and service listens on it.
* CloudFront 403 → check **S3 bucket policy** allows public read.

---

✅ This is a **complete line-by-line workflow** from local code → AWS deployment for frontend + backend.

---

