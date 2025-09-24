 **GitHub CI/CD** for Copilot app step-by-step. I’ll give you a clear, copy-and-paste set of commands and two short YAML files you’ll drop into your repo. The plan:

1. Create & push the GitHub repo (root of `TTS-NEXT-FAST-AWS`)
2. Make sure Copilot app + service + manifest exist locally
3. Create Copilot **staging** and **production** environments and **manually deploy staging once** to get its URL (required for a reliable health test)
4. Add `copilot/pipeline.yml` (uses the staging URL for test commands) and commit
5. Run `copilot pipeline init` → authorize GitHub → `copilot pipeline deploy`
6. Verify pipeline runs: stage → manual approval → prod
7. Troubleshoot commands to use if anything fails

Follow these exact steps.

---

## Prerequisites (one-time)

Run these first if you haven’t already:

```bash
# 1) AWS CLI configured
aws sts get-caller-identity

# 2) Copilot installed
copilot --version

# 3) Docker running (for local builds by Copilot)
docker version

# 4) (Recommended) GitHub CLI for convenience
gh auth login
```

---

## A — Create & push your GitHub repo

From the **root** of your project (`TTS-NEXT-FAST-AWS`):

```bash
cd /path/to/TTS-NEXT-FAST-AWS

# init git (if not already a repo)
git init
git add .
git commit -m "Initial commit: backend + frontend + copilot manifest"

# create the GitHub repo (replace <your-username>)
gh repo create <your-username>/TTS-NEXT-FAST-AWS --public --source=. --remote=origin

# push
git branch -M main
git push -u origin main
```

If you prefer the GitHub web UI, create the repo there and push the same commands that `gh` would run.

---

## B — Ensure Copilot app, service and manifest exist locally

(If you already ran `copilot init` earlier, skip `copilot app init`.)

```bash
# from backend folder
cd backend

# (if you haven't) create the app (copilot will not recreate if exists)
copilot app init tts-next-fast-aws
# you should already see: copilot/backend/manifest.yml
```

**Important:** Confirm the `manifest.yml` is at `backend/copilot/backend/manifest.yml` and contains `http.healthcheck.path: /health` and `deploy.rollback: true`. If not, open it and ensure those lines exist. Example minimal relevant parts:

```yaml
# backend/copilot/backend/manifest.yml (excerpt)
name: backend
type: Load Balanced Web Service
cpu: 1024
memory: 512
port: 8000

http:
  path: '/'
  healthcheck:
    path: '/health'
    healthy_threshold: 2
    unhealthy_threshold: 5
    interval: 10s
    timeout: 5s

deploy:
  rollback: true
```

Commit this manifest so it is in your repo:

```bash
git add backend/copilot/backend/manifest.yml
git commit -m "copilot: add backend manifest"
git push
```

---

## C — Create Copilot environments (staging & production)

Run from the **backend** folder (explicitly pass the app name). Use the AWS profile and region you want:

```bash
# create staging env
copilot env init --name staging --app tts-next-fast-aws --profile default --region us-east-1 --default-config

# create production env
copilot env init --name production --app tts-next-fast-aws --profile default --region us-east-1 --default-config
```

If prompts ask for a VPC config pick the default unless you have custom networking needs.

---

## D — Manually deploy to **staging** once (to get a stable staging endpoint)

This ensures we can write a pipeline test that actually hits the staging ALB.

```bash
copilot svc deploy --name backend --env staging
```

When it finishes successfully, get the staging URL:

```bash
copilot svc show --name backend --env staging
```

Look for the line `URL: http://...elb.amazonaws.com` (or domain). Copy that value — call it `STAGING_URL`. Example:

```
STAGING_URL="http://tts-ne-Publi-sFzKQli08OJ0-998814560.us-east-1.elb.amazonaws.com"
```

Test it locally (the endpoint must return HTTP 200):

```bash
curl -f ${STAGING_URL}/health
```

If it returns JSON `{"status":"ok"}` or 200 — good. If not, fix `/health` in your FastAPI and re-deploy `copilot svc deploy` until it does.

---

## E — Add the pipeline manifest (`copilot/pipeline.yml`)

Create file at: `backend/copilot/pipeline.yml` with this content, replacing `<your-username/TTS-NEXT-FAST-AWS>` and the `staging_api` with the `STAGING_URL` you captured.

```yaml
# backend/copilot/pipeline.yml
name: tts-next-fast-aws-pipeline

source:
  provider: GitHub
  properties:
    repository: "<your-username>/TTS-NEXT-FAST-AWS"   # update
    branch: "main"

stages:
  - name: staging
    # A simple test step that retries the staging /health endpoint for ~60s
    test_commands:
      - bash -lc 'for i in $(seq 1 12); do curl -f "REPLACE_WITH_STAGING_URL/health" && exit 0 || sleep 5; done; echo "staging health check failed" && exit 1'
  - name: production
    requires_approval: true
```

**Important:**

* Replace `REPLACE_WITH_STAGING_URL` with the `STAGING_URL` you got from `copilot svc show` (no trailing slash needed).
* Replace `repository` with your real GitHub repo path.

Commit & push:

```bash
git add backend/copilot/pipeline.yml
git commit -m "Add copilot pipeline definition"
git push origin main
```

---

## F — Initialize the Copilot pipeline (connect to GitHub)

From the **backend** folder run:

```bash
copilot pipeline init --app tts-next-fast-aws --name tts-next-fast-aws-pipeline
```

* Copilot will read `copilot/pipeline.yml`.
* It will prompt to connect to GitHub. Follow prompts — it may open a browser to authorize AWS Copilot with GitHub.

  * If you use `gh auth login` earlier, Copilot can use that to create the connection, otherwise follow the OAuth flow.
  * If you can’t open a browser, Copilot will provide instructions to create a GitHub personal access token with repo and admin\:repo\_hook scopes — but the OAuth flow is easiest.

If `copilot pipeline init` errors, re-run with debug:

```bash
COPILOT_DEBUG=true copilot pipeline init ...
```

---

## G — Deploy the pipeline

```bash
copilot pipeline deploy --name tts-next-fast-aws-pipeline
```

This will create CodePipeline, CodeBuild projects, and the GitHub connection. The first time you push to `main` (you already pushed) the pipeline will start:

* **Stage:** Build & deploy to `staging` (copilot will build and deploy)
* After deployment, CodeBuild runs the `test_commands` (the curl loop)

  * If tests succeed → pipeline pauses for **manual approval** before production
  * If tests fail → pipeline fails and will **not** proceed to production

To promote to production, approve in AWS Console (CodePipeline) or follow the approval link generated by pipeline.

---

## H — Verify & Troubleshooting commands

Useful commands while pipeline runs:

```bash
# checkout pipeline status
copilot pipeline status --name tts-next-fast-aws-pipeline

# check service status in an environment
copilot svc status --name backend --env staging
copilot svc status --name backend --env production

# view logs (live)
copilot svc logs --name backend --env staging --follow

# view logs of a stopped task (previous)
copilot svc logs --name backend --env staging --previous

# show service details (contains URL)
copilot svc show --name backend --env staging
```

If staging deploys but the `test_commands` fail:

* Re-check `curl -f ${STAGING_URL}/health` locally.
* If it fails there, fix `/health`, redeploy staging manually with `copilot svc deploy --name backend --env staging`, then update pipeline.yml and push.

If pipeline init/ deploy fails with permissions errors:

* Ensure your AWS IAM user/CLI profile has CloudFormation, CodePipeline, CodeBuild, ECR, ECS, IAM permissions. Running `copilot pipeline init` will create roles; your account needs permission to create them.

---

## I — Rollback behavior (how it works here)

* The `manifest.yml` contains `deploy.rollback: true` → if Copilot detects the Fargate deployment failed (unhealthy tasks) Copilot automatically rolls back the service to the previous healthy revision.
* The pipeline `test_commands` cause CodeBuild to fail when staging health-check fails → pipeline stops and **does not** promote to production.
* Combined, you get an automated staging gate + safe rollback.

---

## J — What to do after pipeline is running

* Push PRs/commits to `main` to trigger the pipeline. It will deploy to staging automatically.
* Approve in the AWS Console CodePipeline to promote to production.
* If you want fully automated production promotion, remove `requires_approval: true` (not recommended for production).

---

## Quick checklist (summary)

* [ ] `backend/copilot/backend/manifest.yml` has correct `healthcheck.path: /health` and `deploy.rollback: true`
* [ ] `copilot env init` run for `staging` and `production`
* [ ] `copilot svc deploy --env staging` ran once and `staging_url` confirmed working
* [ ] `backend/copilot/pipeline.yml` added, with `STAGING_URL` inserted in test command
* [ ] GitHub repo created and `main` pushed with `copilot` folder committed
* [ ] `copilot pipeline init` → authorize GitHub
* [ ] `copilot pipeline deploy`

---


