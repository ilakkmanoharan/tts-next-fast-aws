ilakkuvaselvimanoharan@MacBookPro backend % curl -i http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com/health
HTTP/1.1 500 Internal Server Error
Date: Sun, 21 Sep 2025 21:28:10 GMT
Content-Type: application/json
Content-Length: 270
Connection: keep-alive
server: uvicorn

{"status":"fail","dependencies":{"s3":"fail (AccessDenied) - check IAM task role and bucket name","polly":"fail (Parameter validation failed:\nUnknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"}}%  

Got it — your `/health` check is failing because **both S3 and Polly are misconfigured**. Let’s break this down:

---

### 🔴 Problem 1: S3 AccessDenied

```
"s3":"fail (AccessDenied) - check IAM task role and bucket name"
```

This means your ECS task/container can’t read/write to the S3 bucket.

✅ Fix:

1. **Verify the bucket name** in your backend config (e.g., environment variable `S3_BUCKET_NAME`).
2. **Check ECS task role IAM permissions**:
   The role needs something like:

   ```json
   {
     "Effect": "Allow",
     "Action": [
       "s3:PutObject",
       "s3:GetObject",
       "s3:ListBucket"
     ],
     "Resource": [
       "arn:aws:s3:::your-bucket-name",
       "arn:aws:s3:::your-bucket-name/*"
     ]
   }
   ```

   Make sure the **task execution role** (not just your local IAM user) has this policy attached.

   ___________

   Perfect — you’re already on the right track. Let’s tighten this up so your `/health` check stops failing on **S3**.

---

### ✅ Step 1: Confirm which bucket your code is checking

From what you shared:

```python
BUCKET = os.getenv("AWS_S3_BUCKET", "my-bucket")
```

So if `AWS_S3_BUCKET` is **not set** in the ECS task definition → it defaults to `"my-bucket"`, which definitely won’t exist.

🔍 Check:

* In **ECS → Task Definitions → Environment variables**, ensure you have:

  ```
  AWS_S3_BUCKET=ts-audio-ilakkm-aug31
  ```
* In `.env.local` / `.env` (for local dev), make sure the same bucket name is there.

---

### ✅ Step 2: IAM Role Permissions

The ECS **task role** (not execution role) must allow access to that bucket.

Attach a policy like this:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ts-audio-ilakkm-aug31",
        "arn:aws:s3:::ts-audio-ilakkm-aug31/*"
      ]
    }
  ]
}
```

---

### ✅ Step 3: Bucket Policy (if set)

If you also applied a bucket policy, make sure it **doesn’t block the ECS task role**. For example:

```json
{
  "Effect": "Allow",
  "Principal": {
    "AWS": "arn:aws:iam::<account-id>:role/<ecs-task-role-name>"
  },
  "Action": "s3:*",
  "Resource": [
    "arn:aws:s3:::ts-audio-ilakkm-aug31",
    "arn:aws:s3:::ts-audio-ilakkm-aug31/*"
  ]
}
```

---

### ✅ Step 4: Double-check `/health` code

If your health check looks like:

```python
s3 = boto3.client("s3", region_name=settings.AWS_REGION)
s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
```

Then:

* `settings.S3_BUCKET_NAME` **must match** `ts-audio-ilakkm-aug31`.
* The IAM role must allow at least `s3:ListBucket`.

---

### 🔑 Summary

* Make sure **ECS env var** → `AWS_S3_BUCKET=ts-audio-ilakkm-aug31`.
* Confirm **task role** has `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`.
* Ensure no restrictive **bucket policy** is blocking ECS role.

---

👉 Do you want me to **show you the exact Copilot command** to update the ECS service’s env var so it always sets `AWS_S3_BUCKET=ts-audio-ilakkm-aug31` in dev/prod?


________________