Thanks — looking at your FastAPI code, the `403 Forbidden` on `/health` comes from **S3 access**. Here’s a detailed analysis and steps to fix it:

---

### **1️⃣ Why the error occurs**

Your `/health` endpoint does this:

```python
s3.head_bucket(Bucket=BUCKET)
```

* `head_bucket` requires **permission to access the bucket itself**.
* In your ECS task, the **task role** must have permissions like:

```json
{
  "Effect": "Allow",
  "Action": ["s3:ListBucket"],
  "Resource": ["arn:aws:s3:::ts-audio-ilakkm-aug31"]
}
```

* To read/write objects:

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": ["arn:aws:s3:::ts-audio-ilakkm-aug31/*"]
}
```

You already tried `s3:HeadBucket` — **this action does not exist**. AWS suggests `s3:ListBucket` instead.

---

### **2️⃣ Correct policy for ECS task role**

Attach this to `tts-next-fast-aws-dev-backend-TaskRole-Z4lBW81EsCnG`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::ts-audio-ilakkm-aug31"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": ["arn:aws:s3:::ts-audio-ilakkm-aug31/*"]
    }
  ]
}
```

* Policy Name: `BackendS3AccessPolicy`
* Save, attach, and **redeploy the backend**.

---

### **3️⃣ Redeploy backend with Copilot**

```bash
copilot svc deploy --name backend --env dev
```

* Wait until the task is running.
* Verify task role is attached correctly:

```bash
copilot svc show --name backend --app tts-next-fast-aws
```

Check under `Task Role`.

---

### **4️⃣ Test `/health`**

```bash
curl -i http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com/health
```

✅ Expected response:

```json
{
  "status": "ok"
}
```

* If it still fails, check logs:

```bash
copilot svc logs --name backend --env dev --follow
```

---

### **5️⃣ Additional checks**

1. **Bucket name matches exactly** (`AWS_S3_BUCKET=ts-audio-ilakkm-aug31`).
2. **No bucket policies blocking the ECS task role**.

---

If you want, I can **rewrite your FastAPI `/health` endpoint** to handle S3 correctly **with the correct permissions**, so it stops returning 500 even if permissions are misconfigured.

Do you want me to do that?
