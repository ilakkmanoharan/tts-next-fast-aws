ilakkuvaselvimanoharan@MacBookPro backend % curl -i http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com/health
HTTP/1.1 500 Internal Server Error
Date: Sun, 21 Sep 2025 03:12:13 GMT
Content-Type: application/json
Content-Length: 270
Connection: keep-alive
server: uvicorn

{"status":"fail","dependencies":{"s3":"fail (AccessDenied) - check IAM task role and bucket name","polly":"fail (Parameter validation failed:\nUnknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"}}%                     
ilakkuvaselvimanoharan@MacBookPro backend % 

From the `curl` output, your backend health check is failing with **500 Internal Server Error**, and the JSON response shows two main issues:

---

### 1️⃣ S3 access failure

```json
"s3":"fail (AccessDenied) - check IAM task role and bucket name"
```

**Cause:** Your ECS task (or EC2 instance, if not using Fargate) does not have permission to access the S3 bucket, or the bucket name in your config is wrong.

**Fixes:**

* Make sure your **IAM task role** has at least the following permissions for your bucket:

```json
{
    "Effect": "Allow",
    "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
    ],
    "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
    ]
}
```

* Verify that the **bucket name in your backend config** matches exactly (including case and region).
* If using AWS SDK v3 or boto3, check that the region is set correctly.

---

### 2️⃣ Polly API failure

```json
"polly":"fail (Parameter validation failed:\nUnknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"
```

**Cause:** Your backend is calling AWS Polly with a **parameter `MaxResults`** that Polly does not accept for that API operation.

**Fixes:**

* Check which Polly method you are calling. For example:

  * `DescribeVoices` supports `Engine`, `LanguageCode`, `IncludeAdditionalLanguageCodes`, `NextToken`.
  * `MaxResults` is **not valid** in some SDK versions or API operations.
* Remove `MaxResults` or replace it with `NextToken` for pagination if needed.

---

### ✅ Next steps

1. Update the **IAM task role** to grant proper S3 permissions.
2. Verify **S3 bucket name** in config.
3. Fix the Polly API call to remove or replace unsupported parameters.
4. Redeploy your backend and retry:

```bash
curl -i http://<ELB-DNS>/health
```

 curl -i http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com/health


---

If you want, I can **write the exact IAM policy and the corrected Polly call** for your backend so that your `/health` endpoint passes. This will likely fix the 500 error immediately.

Do you want me to do that?
