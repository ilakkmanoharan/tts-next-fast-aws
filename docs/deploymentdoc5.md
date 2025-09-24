Running **staging + production** side by side is one of the nicest parts of AWS Copilot.

You just define multiple **environments** in your `manifest.yml`, and each one gets its own URL (e.g., `api-test.mydomain.com` for staging, `api.mydomain.com` for production).

---

## 📄 `copilot/backend/manifest.yml` (staging + prod with custom domains)

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

variables:
  ENV: "production"

environments:
  test:
    count: 1
    variables:
      ENV: "staging"
    http:
      alias: api-test.mydomain.com   # 👈 staging subdomain
  prod:
    count: 2
    cpu: 512
    memory: 1024
    variables:
      ENV: "production"
    http:
      alias: api.mydomain.com        # 👈 production domain
```

---

## 🚀 Steps to Deploy Both Environments

1. **Initialize your app with domain support** (do this only once):

   ```bash
   copilot app init my-backend-app --domain mydomain.com
   ```

2. **Create test (staging) environment**:

   ```bash
   copilot env init --name test --region us-east-1
   copilot deploy --name backend --env test
   ```

   * Copilot will create `api-test.mydomain.com`
   * You’ll be able to test new versions here first.

3. **Create production environment**:

   ```bash
   copilot env init --name prod --region us-east-1
   copilot deploy --name backend --env prod
   ```

   * Copilot will create `api.mydomain.com`
   * This is your live, stable environment.

---

## 🌟 Workflow After Setup

* Deploy new builds to **staging first**:

  ```bash
  copilot deploy --name backend --env test
  ```

  Test it on `https://api-test.mydomain.com`.

* When ready, deploy to **production**:

  ```bash
  copilot deploy --name backend --env prod
  ```

---

✅ With this setup, you have:

* A **test environment** (`api-test.mydomain.com`)
* A **production environment** (`api.mydomain.com`)
* Both managed with **Route53 + ACM certs + ALB**, no manual config.

---
