Extend the **Copilot manifest** so your backend can run on **HTTPS with a custom domain via Route53 + ACM**.

Copilot makes this simple: you just add your domain info, and it handles DNS records, certs, and HTTPS.

---

## 📄 `copilot/backend/manifest.yml` (with custom domain)

```yaml
name: backend
type: Load Balanced Web Service

image:
  build: ./Dockerfile
  port: 8000

cpu: 256
memory: 512
count: 1

http:
  path: '/'
  healthcheck: '/'
  target_container: backend

  # Enable HTTPS + custom domain
  alias: api.mydomain.com   # 👈 Replace with your Route53-managed domain

variables:
  ENV: "production"

environments:
  test:
    count: 1
    http:
      alias: api-test.mydomain.com   # 👈 optional, staging subdomain
  prod:
    count: 2
    cpu: 512
    memory: 1024
    http:
      alias: api.mydomain.com        # 👈 production domain
```

---

## 🚀 Steps to Enable Domain + HTTPS

1. **Pre-requirements**:

   * Your domain (`mydomain.com`) must be hosted in **Route53**.
   * ACM certificate will be auto-created by Copilot.

2. **Initialize app with domain support**:

   ```bash
   copilot app init my-backend-app --domain mydomain.com
   ```

   Copilot will:

   * Create an ACM certificate
   * Add DNS validation records to Route53

3. **Create and deploy environment**:

   ```bash
   copilot env init --name prod --region us-east-1
   copilot deploy --name backend --env prod
   ```

4. **Wait for DNS validation**
   Copilot will update Route53 automatically.
   After a few minutes, you can access:

   ```
   https://api.mydomain.com
   ```

   (with full HTTPS, managed by ACM)

---

## ✅ What Copilot Handles for You

* Creates **ALB** with HTTPS termination
* Creates and validates **ACM certs**
* Manages **Route53 records**
* Ensures **auto-renewal** of certs

---
