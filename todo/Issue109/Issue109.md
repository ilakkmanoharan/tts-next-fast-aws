ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % curl -i http://tts-ne-Publi-Y8hrIb4Sm9QW-1868692897.us-east-1.elb.amazonaws.com/health

HTTP/1.1 500 Internal Server Error
Date: Mon, 22 Sep 2025 20:26:38 GMT
Content-Type: application/json
Content-Length: 270
Connection: keep-alive
server: uvicorn

{"status":"fail","dependencies":{"s3":"fail (AccessDenied) - check IAM task role and bucket name","polly":"fail (Parameter validation failed:\nUnknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"}}%  

The health check shows two clear issues causing the `500 Internal Server Error`:

1. **S3 Access Denied**

   ```
   "s3":"fail (AccessDenied) - check IAM task role and bucket name"
   ```

   This indicates that the ECS task’s IAM role does **not have proper permissions** to access the S3 bucket. Likely causes:

   * The ECS task role is missing `s3:GetObject` or `s3:PutObject` (depending on what your service does).
   * The bucket name in the environment/config is incorrect.
   * The bucket policy explicitly denies access to the role.

2. **Polly Parameter Validation Error**

   ```
   "polly":"fail (Parameter validation failed:
   Unknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"
   ```

   This means your backend is calling Amazon Polly with a parameter `MaxResults` that Polly does **not support** in that API call. You need to:

   * Remove `MaxResults` from the API call.
   * Ensure you are calling the correct Polly API method and using only its supported parameters.

✅ **Next steps**:

* Update the ECS task role to include correct S3 permissions.
* Verify the S3 bucket name in your environment variables or config.
* Fix the Polly API call by removing the unsupported `MaxResults` parameter.

If you want, I can write the **exact IAM policy snippet** your ECS task role needs for S3 and show how to correct the Polly call. Do you want me to do that?
