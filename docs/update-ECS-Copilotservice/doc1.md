Perfect! Here’s a **full checklist** to deploy your new `tts-backend:latest` image to ECS (via Copilot / CloudFormation) and verify everything is healthy. I’ve broken it into **clear steps**:

---

## **1️⃣ Update ECS / Copilot Service to Use the New Image**

### **Option A: Copilot**

1. Open your terminal in the project folder.
2. Update the backend service to use the latest image in ECR:

```bash
# Ensure you are in your backend directory
copilot svc deploy --name backend --env prod
```

> Copilot automatically uses the `latest` tag from your ECR repo if your `manifest.yml` specifies it. Otherwise, update the `image` field in `copilot/backend/manifest.yml`:

```yaml
image:
  location: 681916125840.dkr.ecr.us-east-1.amazonaws.com/tts-backend:latest
```

3. Deploy the service:

```bash
copilot svc deploy --name backend --env prod
```

---

### **Option B: ECS / CloudFormation Direct**

If you’re managing ECS directly via CloudFormation:

1. Update your ECS Task Definition JSON to point to the new image:

```json
"containerDefinitions": [
  {
    "name": "tts-backend",
    "image": "681916125840.dkr.ecr.us-east-1.amazonaws.com/tts-backend:latest",
    ...
  }
]
```

2. Update the ECS service to use the **new revision**:

```bash
aws ecs update-service \
    --cluster tts-cluster \
    --service tts-backend-service \
    --force-new-deployment
```

---

## **2️⃣ Verify the ECS Task is Running the New Image**

1. Check running tasks:

```bash
aws ecs list-tasks --cluster tts-cluster --service-name tts-backend-service
```

2. Describe tasks to see the image:

```bash
aws ecs describe-tasks --cluster tts-cluster --tasks <task-arn>
```

Look for `image` in the container definitions—it should match:

```
681916125840.dkr.ecr.us-east-1.amazonaws.com/tts-backend:latest
```

---

## **3️⃣ Verify Health / Logs**

1. Check ECS task health:

```bash
aws ecs describe-services --cluster tts-cluster --services tts-backend-service
```

Look for `"runningCount"` matching `"desiredCount"` and `"healthStatus": "HEALTHY"`.

2. Stream logs (CloudWatch):

```bash
aws logs tail /ecs/tts-backend --follow
```

Look for errors or confirmation that your app started successfully.

---

## **4️⃣ Verify Frontend Connectivity**

1. Make sure your frontend `.env` is pointing to the correct backend URL:

```env
NEXT_PUBLIC_BACKEND_URL=https://<your-backend-endpoint>
```

2. Test frontend requests:

```bash
curl -I https://<frontend-url>/api/health
```

Should return **200 OK** (or your health endpoint response).

---

## **5️⃣ Optional: Clean up old images in ECR**

Keep your repo tidy:

```bash
aws ecr list-images --repository-name tts-backend --query 'imageIds[?imageTag!=`latest`]' --output json | \
  xargs -n1 -I {} aws ecr batch-delete-image --repository-name tts-backend --image-ids {}
```

---

✅ Following this checklist should:

* Deploy the new image.
* Replace old running tasks.
* Avoid 403 errors (because your image is now in the correct AWS account).
* Ensure the backend is healthy and reachable from your frontend.

---

I can also create a **single “deploy & verify” bash script** that automates all of these steps—including ECS deployment, health check, and CloudWatch logs—so you can run it in one command.

Do you want me to make that script?
