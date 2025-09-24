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

---

### 🔴 Problem 2: Polly Parameter Validation

```
"polly":"fail (Parameter validation failed:
Unknown parameter in input: \"MaxResults\" ..."
```

The error is that your code is passing `MaxResults` to a Polly API call that doesn’t accept it.

✅ Fix:

* Likely you are calling `describe_voices` with `MaxResults`:

  ```python
  polly.describe_voices(MaxResults=10)
  ```

  But Polly’s boto3 API **does not support `MaxResults`**. The valid parameters are:

  * `Engine`
  * `LanguageCode`
  * `IncludeAdditionalLanguageCodes`
  * `NextToken`

So remove or replace `MaxResults`. For example:

```python
polly.describe_voices(LanguageCode="en-US")
```

---

### ✅ Next Steps

1. Update your ECS task role to include proper **S3 permissions**.
2. Fix your backend code to remove the invalid `MaxResults` parameter from Polly calls.
3. Redeploy → test `/health` again.

---

Do you want me to **write the exact IAM JSON policy** for your ECS task role and show the corrected **Polly boto3 snippet** you can paste into your backend code?

