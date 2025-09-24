Adding **safe rollback** to your Copilot pipeline so staging failures never reach prod.

AWS Copilot already leans on **CodeDeploy for ECS** under the hood, which supports **automated rollback** if a new task revision fails health checks.
We’ll combine that with pipeline rules.

---

## 🔒 Rollback Strategy for Your Pipeline

### 1. Use Safe Deployment in ECS Service

In your `manifest.yml`, enable **circuit breaker + rolling update**:

```yaml
deployment:
  rolling:
    max_percent: 200
    min_healthy_percent: 100
  circuit_breaker:
    enable: true
    rollback: true
```

✅ What this does:

* Deploys new tasks gradually (keeps old ones running until new ones are healthy).
* If the new version fails (container crashes, unhealthy ALB checks, etc.), **ECS auto-rolls back** to the last working version.

---

### 2. Modify `pipeline.yml`

Add a staging → prod flow with approval (already there), plus guardrails:

```yaml
name: backend-pipeline
version: 1

source:
  provider: GitHub
  properties:
    repository: ajay/my-backend-app
    branch: main

stages:
  - name: test
    env: test
    requires_approval: false
  - name: prod
    env: prod
    requires_approval: true   # ✅ must approve manually before prod
```

This ensures:

* Every push → **deploys to staging (`test`)**.
* ECS **rolls back automatically** if staging fails.
* Only after approval does it go to **production (`prod`)**.

---

### 3. Add Health Checks

Make sure your `manifest.yml` has a **real healthcheck path** (not just `/`) that returns `200 OK` when healthy:

```yaml
http:
  path: '/'
  healthcheck: '/health'   # 👈 e.g., /health endpoint in FastAPI/Express
```

This ensures ECS only marks tasks as healthy when your app is actually ready.

---

### 4. Optional: Manual Rollback (Pipeline CLI)

If prod still has issues after deploy, you can roll back:

```bash
copilot svc rollback --name backend --env prod
```

This reverts to the last working task definition.

---

### 5. Monitor Rollback

```bash
copilot svc status --name backend --env test
copilot svc status --name backend --env prod
```

And in AWS Console → **ECS → Deployments**, you’ll see whether rollback triggered.

---

## ⚡ Summary of Rollback Flow

1. Push code → Pipeline deploys to **staging**.
2. If staging fails → ECS rollback → pipeline **stops**, never reaches prod.
3. If staging passes → you approve → deploys to **prod**.
4. If prod fails → ECS rollback auto-restores previous working version.

---

