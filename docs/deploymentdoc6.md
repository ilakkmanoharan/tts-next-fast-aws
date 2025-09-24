Adding **CI/CD with AWS Copilot Pipelines**.
This way:

* Every push to GitHub → builds Docker → deploys to **staging (`test`)** automatically.
* You test it at `https://api-test.mydomain.com`.
* With one approval step → deploys to **production (`prod`)** at `https://api.mydomain.com`.

---

## 1. Prerequisites

On your Mac / VS Code terminal:

```bash
brew install aws/tap/copilot-cli
aws configure
```

Also, create a GitHub repo (if not already).

---

## 2. Enable Copilot Pipeline

From your project root (where `copilot/` folder exists):

```bash
copilot pipeline init
```

It will ask:

* **Pipeline name** → e.g. `backend-pipeline`
* **Repository provider** → choose `GitHub`
* **GitHub repo URL** → e.g. `https://github.com/ajay/my-backend-app`
* **Branch** → usually `main`

This will generate:

* `copilot/pipeline.yml` → pipeline config
* `copilot/buildspec.yml` → build commands

---

## 3. Example `pipeline.yml`

Here’s a version with staging → prod + manual approval:

```yaml
name: backend-pipeline
version: 1

source:
  provider: GitHub
  properties:
    repository: ajay/my-backend-app   # 👈 replace with your repo
    branch: main

stages:
  - name: test
    requires_approval: false
    env: test
  - name: prod
    requires_approval: true   # 👈 manual approval before prod
    env: prod
```

---

## 4. Buildspec (Docker Build + Push)

Copilot generates a `buildspec.yml` for CodeBuild.
Typical content (you can tweak):

```yaml
version: 0.2
phases:
  install:
    runtime-versions:
      docker: 20
  build:
    commands:
      - echo "Building Docker image..."
      - copilot svc package --env $COPILOT_ENVIRONMENT --output-dir ./infrastructure
      - aws cloudformation package \
          --template-file ./infrastructure/backend.template.yml \
          --s3-bucket $ARTIFACT_BUCKET \
          --output-template-file output.yml
artifacts:
  files:
    - output.yml
```

---

## 5. Bootstrap Pipeline Resources

Run:

```bash
copilot pipeline update
```

This creates:

* CodePipeline
* CodeBuild projects
* IAM roles

---

## 6. Trigger Deployment

Push code to GitHub:

```bash
git add .
git commit -m "Trigger pipeline"
git push origin main
```

Pipeline flow:

* **Build → Deploy to test (`api-test.mydomain.com`)**
* Wait for approval
* **Deploy to prod (`api.mydomain.com`)**

---

## 7. Monitor Pipeline

```bash
copilot pipeline status
```

Or check AWS Console → CodePipeline.

---

✅ Now you have:

* **2 environments** (staging + prod)
* **Custom domains** with HTTPS
* **Automated pipeline** with GitHub → ECS Fargate deploy


