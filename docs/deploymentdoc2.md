AWS **Copilot CLI** makes ECS + Fargate deployment much simpler.

---

## 1. Install & Configure

```bash
# Install Copilot
brew install aws/tap/copilot-cli

# Verify
copilot --version

# Configure AWS credentials
aws configure
```

---

## 2. Initialize Your App

From your backend project folder (where your `Dockerfile` lives):

```bash
copilot init
```

It will ask:

* **App name** → e.g., `my-backend-app`
* **Workload type** → `Load Balanced Web Service`
* **Service name** → `backend`
* **Dockerfile** → just hit enter if `Dockerfile` is in current folder
* **Port** → `8000`

This will automatically:

* Create an **ECR repo**
* Build & push Docker image
* Create **ECS cluster** with Fargate
* Deploy the service behind an **Application Load Balancer**
* Open port 8000 (and also expose through ALB on port 80)

---

## 3. Deploy

```bash
copilot deploy
```

This command:

* Builds your Docker image
* Pushes it to ECR
* Registers ECS task definition
* Deploys on ECS Fargate
* Creates ALB with a public endpoint

At the end, it will output a URL like:

```
https://backend.my-backend-app.awsapprunner.com
```

You can open this in the browser.

---

## 4. (Optional) Custom Domain with Route53

If you own a domain:

```bash
copilot svc deploy --env prod --domain mydomain.com
```

Copilot will:

* Configure Route53 records
* Create ACM certificate
* Map your ECS service to `https://backend.mydomain.com`

---

## 5. Other Useful Commands

```bash
# Show service status
copilot svc status

# View logs
copilot svc logs

# Delete everything
copilot app delete
```

---

⚡️ Copilot takes care of all the painful parts (task def, SG, networking, load balancer).
Instead of 30+ AWS CLI commands, you get it done with **2–3 commands**.

