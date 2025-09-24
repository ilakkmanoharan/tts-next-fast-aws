ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % curl -i http://tts-ne-Publi-Y8hrIb4Sm9QW-1868692897.us-east-1.elb.amazonaws.com/health

HTTP/1.1 500 Internal Server Error
Date: Mon, 22 Sep 2025 19:30:54 GMT
Content-Type: application/json
Content-Length: 270
Connection: keep-alive
server: uvicorn

{"status":"fail","dependencies":{"s3":"fail (AccessDenied) - check IAM task role and bucket name","polly":"fail (Parameter validation failed:\nUnknown parameter in input: \"MaxResults\", must be one of: Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken)"}}%    


Ah — now the **health check output gives us clear clues**. Let’s break it down:

---

### 1️⃣ S3: `fail (AccessDenied) - check IAM task role and bucket name)`

Even though we attached the policy, this indicates **your ECS task cannot access the S3 bucket**.

Possible causes:

1. **Bucket name mismatch**

   * Your policy allows `ts-audio-ilakkm-aug31`.
   * Double-check your backend is actually trying to access **exactly this bucket**.

2. **Policy not attached correctly / task not using updated role**

   * Did you deploy a **new task revision** after attaching the IAM policy?
   * ECS tasks **only get the role permissions at start time**. If the task is still running an old revision, the updated policy won’t take effect.

3. **Region mismatch**

   * Make sure the S3 bucket is in the **same region** your ECS task is running.

✅ Fix:

* Stop the running ECS task and let ECS start a **new task** with the updated role.
* Or update the service to use a **new revision** of the task definition.

---

### 2️⃣ Polly: `(Parameter validation failed: Unknown parameter in input: "MaxResults")`

* Your backend is passing `MaxResults` to the Polly API, which doesn’t accept it.
* Correct parameters for `polly.synthesizeSpeech` (or `listVoices`) are:

  ```
  Engine, LanguageCode, IncludeAdditionalLanguageCodes, NextToken
  ```
* Remove `MaxResults` from your backend request to Polly.

---

### ✅ Next steps to fix health endpoint

1. **S3 fix**

   * Verify the bucket name matches exactly what’s in your policy.
   * Restart ECS tasks / redeploy service to pick up the updated IAM role.
   * Optional test: exec into a container and run:

   ```bash
   aws s3 ls s3://ts-audio-ilakkm-aug31
   ```

2. **Polly fix**

   * Edit your backend code to remove `MaxResults` from Polly API calls.
   * Deploy a new container revision.

3. **Re-test**

   ```bash
   curl -i http://<your-elb>/health
   ```

   You should see:

   ```json
   {"status":"ok","dependencies":{"s3":"ok","polly":"ok"}}
   ```

---

If you want, I can write a **step-by-step ECS redeploy plan** that:

* Ensures the task uses the updated IAM role
* Fixes S3 access immediately
* Prepares Polly calls to pass validation

Do you want me to do that?
