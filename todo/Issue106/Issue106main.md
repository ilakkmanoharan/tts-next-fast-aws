Got it 👍 Let’s confirm whether the **500 error is coming from your container**.

Since you’re using Copilot, the easiest way is to tail your app logs while you curl the ALB:

```bash
copilot svc logs --name backend --env dev --follow
```

Then, in another terminal, run:

```bash
curl -i http://tts-ne-Publi-Y8hrIb4Sm9QW-1868692897.us-east-1.elb.amazonaws.com/health
```

👉 If the 500 is coming from **inside your app**, you’ll see the Python/FastAPI error stack trace or log line appear in the Copilot log output at the same time.

This will tell us **exactly why `/health` is failing** (missing dependency, DB connection issue, S3 issue, etc).

Do you want me to also give you the **direct ECS log fetch command** (using `aws logs tail`) in case you prefer bypassing Copilot?



ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % curl -i http://tts-ne-Publi-Y8hrIb4Sm9QW-1868692897.us-east-1.elb.amazonaws.com/health

HTTP/1.1 500 Internal Server Error
Date: Mon, 22 Sep 2025 18:48:50 GMT
Content-Type: application/json
Content-Length: 270
Connection: keep-alive
server: uvicorn

{"status":"fail","dependencies":{"s3":"fail (AccessDenied) - check IAM task role and bucket name","polly":"fail (Parameter validation failed:\nUnknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"}}%      

Perfect ✅ — that log output is gold. Now we know exactly why `/health` is failing:

1. **S3** → `fail (AccessDenied)`

   * Your ECS **task role** does **not** yet have permission for your bucket `ts-audio-ilakkm-aug31`.
   * Fix: Attach a policy with `s3:ListBucket` and `s3:GetObject` (and probably `s3:PutObject` if you write audio).

2. **Polly** → `fail (Parameter validation failed: Unknown parameter in input: "MaxResults")`

   * Your health check code is calling `describe_voices` with `MaxResults`.
   * `describe_voices` does **not support `MaxResults`** (it uses `NextToken` for pagination).
   * Fix: Remove `MaxResults` from that API call.

---

### ✅ Next Actions

#### Step 1: Fix IAM Task Role

Once we grab the ECS task role name (from `aws ecs describe-task-definition`), attach this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::ts-audio-ilakkm-aug31"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::ts-audio-ilakkm-aug31/*"
    }
  ]
}
```

Attach with:

```bash
aws iam put-role-policy \
  --role-name <your-task-role-name> \
  --policy-name S3AudioAccess \
  --policy-document file://s3-audio-policy.json
```

---

#### Step 2: Fix Polly Health Check

In your health check code, update this line:

```python
# Wrong
polly.describe_voices(MaxResults=5)
```

to:

```python
# Correct
polly.describe_voices()
```

---

👉 Do you want me to walk you through **finding your ECS Task Role ARN** (so we can apply the S3 fix right now), or do you want to **patch the Polly code first** and redeploy?
