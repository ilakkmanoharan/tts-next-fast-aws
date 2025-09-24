@app.get("/health")
async def health_check():
    status = {"s3": "ok", "polly": "ok"}
    http_status = 200

    try:
        s3.list_objects_v2(Bucket=BUCKET, MaxKeys=1)
    except s3.exceptions.ClientError as e:
        logger.error("S3 health check failed", exc_info=True)
        status["s3"] = f"fail ({e.response['Error']['Code']})"
        http_status = 500

    try:
        polly.describe_voices(MaxResults=1)
    except Exception as e:
        logger.error("Polly health check failed", exc_info=True)
        status["polly"] = f"fail ({str(e)})"
        http_status = 500

    return JSONResponse(
        {"status": "ok" if http_status == 200 else "fail", "dependencies": status},
        status_code=http_status
    )



Ah — now we’ve found the cause of the connection reset. Your `/health` endpoint **calls AWS S3 and Polly**:

```python
s3.list_objects_v2(Bucket=BUCKET, MaxKeys=1)
polly.describe_voices(MaxResults=1)
```

If the container **does not have AWS credentials** or the `BUCKET` environment variable is not set correctly, these calls **raise exceptions that aren’t always caught cleanly by FastAPI**, which can result in the “connection reset by peer” behavior when `curl` hits `/health`.

---

### How to fix / debug

#### 1️⃣ Check that the container has AWS credentials

Inside the container:

```bash
docker exec -it tts-backend bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
aws s3 ls
aws polly describe-voices --max-items 1
```

* If these fail, FastAPI’s health check will fail too.

---

#### 2️⃣ Make sure `BUCKET` is set

```bash
echo $BUCKET
```

* If `BUCKET` is empty or incorrect, `s3.list_objects_v2` will throw an exception.

---

#### 3️⃣ Make the health check safe

Wrap the AWS calls with better exception handling so the endpoint **never crashes**, e.g.:

```python
from botocore.exceptions import ClientError

@app.get("/health")
async def health_check():
    status = {"s3": "ok", "polly": "ok"}
    http_status = 200

    try:
        s3.list_objects_v2(Bucket=BUCKET, MaxKeys=1)
    except ClientError as e:
        logger.exception("S3 health check failed")
        status["s3"] = f"fail ({e.response['Error']['Code']})"
        http_status = 500
    except Exception as e:
        logger.exception("Unexpected S3 error")
        status["s3"] = f"fail ({str(e)})"
        http_status = 500

    try:
        polly.describe_voices(MaxResults=1)
    except Exception as e:
        logger.exception("Polly health check failed")
        status["polly"] = f"fail ({str(e)})")
        http_status = 500

    return JSONResponse(
        {"status": "ok" if http_status == 200 else "fail", "dependencies": status},
        status_code=http_status
    )
```

This ensures any exception is logged and returned properly, **without resetting the connection**.

---

#### 4️⃣ Quick local test

If you want to test FastAPI without needing AWS credentials yet, you can **temporarily comment out the AWS calls**:

```python
# s3.list_objects_v2(Bucket=BUCKET, MaxKeys=1)
# polly.describe_voices(MaxResults=1)
```

Then `curl http://localhost:8000/health` should return a normal JSON.

---

I can write a **fully safe `/health` endpoint for Docker**, which logs AWS errors and never crashes, so you can immediately test `/voices` and `/generate-audio` safely.

Do you want me to do that?



__________________________


1️⃣ Check that the container has AWS credentials
Inside the container:
docker exec -it tts-backend bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
aws s3 ls
aws polly describe-voices --max-items 1
If these fail, FastAPI’s health check will fail too.


Yes — run them **step by step** inside the container. This will let you confirm whether your container actually has valid AWS credentials and can reach S3 and Polly. Here’s the order I recommend:

---

### 1️⃣ Enter the container shell

```bash
docker exec -it tts-backend bash
```

---

### 2️⃣ Check if AWS environment variables are set

```bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

* If these print empty, your container does **not** have credentials, and calls to S3/Polly will fail.

---

### 3️⃣ Test S3 access

```bash
aws s3 ls
```

* This lists buckets. If it fails with “AccessDenied” or “Unable to locate credentials”, then your FastAPI health check cannot reach S3.

---

### 4️⃣ Test Polly access

```bash
aws polly describe-voices --max-items 1
```

* If this fails, it confirms your container cannot talk to Polly.

---

Once you run these step by step, you’ll know if the issue is **missing AWS credentials** or something else in the container.

If you want, I can tell you **exactly how to pass AWS credentials into the container so `/health` works**. Do you want me to do that?

