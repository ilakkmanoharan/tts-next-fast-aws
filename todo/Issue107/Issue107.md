ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % curl -i http://tts-ne-Publi-Y8hrIb4Sm9QW-1868692897.us-east-1.elb.amazonaws.com/health HTTP/1.1 500 Internal Server Error Date: Mon, 22 Sep 2025 18:48:50 GMT Content-Type: application/json Content-Length: 270 Connection: keep-alive server: uvicorn {"status":"fail","dependencies":{"s3":"fail (AccessDenied) - check IAM task role and bucket name","polly":"fail (Parameter validation failed:\nUnknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"}}%

Perfect ✅ — that log output is gold. Now we know exactly why /health is failing:
S3 → fail (AccessDenied)
Your ECS task role does not yet have permission for your bucket ts-audio-ilakkm-aug31.
Fix: Attach a policy with s3:ListBucket and s3:GetObject (and probably s3:PutObject if you write audio).

✅ Next Actions
Step 1: Fix IAM Task Role
Once we grab the ECS task role name (from aws ecs describe-task-definition), attach this policy:
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
Attach with:
aws iam put-role-policy \
  --role-name <your-task-role-name> \
  --policy-name S3AudioAccess \
  --policy-document file://s3-audio-policy.json