ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % curl http://localhost:8000/health

{"status":"fail","dependencies":{"s3":"fail (AccessDenied)","polly":"fail (Parameter validation failed:\nUnknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"}}% 

Ah, now we see exactly what’s going wrong — two separate issues inside the container:

---

### **1️⃣ S3 Access Denied**

The health check reports:

```
"s3":"fail (AccessDenied)"
```

This means the AWS credentials are **not authorized** to access the bucket `ts-audio-ilakkm-aug31`. Possible causes:

* The IAM user corresponding to `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` doesn’t have `s3:GetObject`, `s3:PutObject`, and/or `s3:ListBucket` permissions for that bucket.
* The bucket name is misspelled or in a different region.
* The environment variables inside Docker are correct, but the IAM policy doesn’t allow access from your container’s location.

**Quick test inside the container:**

```bash
docker exec -it tts-backend /bin/bash
aws s3 ls s3://ts-audio-ilakkm-aug31
```

If it still says `AccessDenied`, you need to update the IAM policy attached to this user to allow at least:

```json
{
    "Effect": "Allow",
    "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject"
    ],
    "Resource": [
        "arn:aws:s3:::ts-audio-ilakkm-aug31",
        "arn:aws:s3:::ts-audio-ilakkm-aug31/*"
    ]
}
```

---

### **2️⃣ Polly API Parameter Error**

The health check reports:

```
"polly":"fail (Parameter validation failed:\nUnknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"
```

* It looks like your FastAPI health check is calling **AWS Polly’s `describe_voices`** incorrectly.
* The parameter `MaxResults` is **not valid** for the SDK version you’re using.
* You should replace it with valid parameters, e.g., `NextToken` or remove `MaxResults` entirely.

**Example working call in Python (boto3):**

```python
import boto3

polly = boto3.client("polly", region_name="us-east-1")
response = polly.describe_voices(LanguageCode="en-US")  # valid params
print(response)
```

---

✅ **Summary of fixes needed:**

1. Update the IAM user’s S3 permissions to allow your bucket access.
2. Fix the Polly API call in your FastAPI code to remove `MaxResults` and use valid parameters.

---

If you want, I can **write the corrected health check function** for your FastAPI app that will properly test S3 and Polly so the `/health` endpoint returns `"ok"`. This will let you confirm the container is fully functional.

Do you want me to do that?

