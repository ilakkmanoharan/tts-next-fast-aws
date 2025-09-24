ilakkuvaselvimanoharan@MacBookPro backend % curl -i http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com/health

HTTP/1.1 500 Internal Server Error
Date: Sun, 21 Sep 2025 02:03:48 GMT
Content-Type: application/json
Content-Length: 118
Connection: keep-alive
server: uvicorn

{"status":"fail","dependency":"s3","error":"An error occurred (403) when calling the HeadBucket operation: Forbidden"}% 

Ah — now we’ve pinpointed the issue. Your backend **can reach AWS S3**, but it’s hitting a **403 Forbidden** when trying to access the bucket.

### What this means:

* Your backend is deployed correctly and the service is live. ✅
* The `500 Internal Server Error` comes from your app trying to access S3.
* The error:

```
An error occurred (403) when calling the HeadBucket operation: Forbidden
```

indicates that **the IAM role or credentials your ECS task uses do not have permission** to access the S3 bucket.

---

### How to fix it:

1. **Check which IAM role your backend ECS task is using**:

```bash
copilot svc show --name backend --app tts-next-fast-aws
```

Look for `Task Role ARN`. That role needs **S3 permissions**.

2. **Attach a policy to allow S3 access**, for example:

```json
{
    "Effect": "Allow",
    "Action": [
        "s3:HeadBucket",
        "s3:GetObject",
        "s3:PutObject"
    ],
    "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
    ]
}
```

* Replace `your-bucket-name` with the actual bucket name your backend is using.

3. **Redeploy the service** after updating the IAM role:

```bash
copilot svc deploy --name backend --env dev
```

---

💡 Quick sanity check: You can also test the role locally using AWS CLI:

```bash
aws s3 ls s3://your-bucket-name --profile <task-role-profile>
```

If it fails with 403 locally, the IAM policy needs adjustment.

---

I can draft the **exact IAM policy snippet for your Copilot backend ECS task** so that it will fix this 403 S3 error. Do you want me to do that?
