A **ready-to-run Copilot config (`manifest.yml`)** for the backend service on port `8000`.

When you run `copilot init` or `copilot deploy`, Copilot generates this file under `copilot/backend/manifest.yml`. You can edit it before deploying.

---

## 📄 `copilot/backend/manifest.yml`

```yaml
# The manifest for the "backend" service.
# Read more: https://aws.github.io/copilot-cli/docs/manifest/lb-web-service/

name: backend
type: Load Balanced Web Service

# Docker build configuration
image:
  build: ./Dockerfile   # Path to your Dockerfile
  port: 8000            # Container port your app listens on

cpu: 256                 # 0.25 vCPU
memory: 512              # 512 MiB
count: 1                 # Desired tasks running

http:
  path: '/'              # Route incoming traffic to "/"
  healthcheck: '/'       # Path Copilot uses for container health check
  target_container: backend

# Optional: environment variables
variables:
  ENV: "production"

# Deployment environments
environments:
  test:
    count: 1
  prod:
    count: 2
    cpu: 512
    memory: 1024
```

---

## 🚀 Steps to Use

1. Create your app:

   ```bash
   copilot app init my-backend-app
   ```

2. Create the service (this will also generate the `manifest.yml`):

   ```bash
   copilot svc init --name backend --svc-type "Load Balanced Web Service" --dockerfile ./Dockerfile --port 8000
   ```

3. Replace the generated `manifest.yml` with the one above (or edit it directly).

4. Deploy to an environment:

   ```bash
   copilot env init --name test --region us-east-1
   copilot deploy --name backend --env test
   ```

   At the end you’ll get a URL like:

   ```
   https://backend-test.my-backend-app.amazonaws.com
   ```

---

✅ That’s it — clean config, runs on **Fargate + ALB**, no manual AWS CLI networking setup.
