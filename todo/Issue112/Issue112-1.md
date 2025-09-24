1️⃣ FastAPI backend cannot reach S3
Make sure the Python code uses boto3 correctly and is reading the environment variables.
Example check in Python:
import boto3

s3 = boto3.client('s3')
try:
    s3.list_objects_v2(Bucket='ts-audio-ilakkm-aug31')
    print("S3 access: OK")
except Exception as e:
    print("S3 access failed:", e)
If this works inside the container, your health check code might be misconfigured.

Absolutely — let’s go **step by step** to test if your FastAPI backend can reach S3 from inside the container using `boto3`. This will isolate whether the problem is the container setup or your health check code.

---

## **Step 1: Open a shell inside the running container**

Run:

```bash
docker exec -it tts-backend /bin/sh
```

You are now inside the container.

---

## **Step 2: Check if Python and boto3 are installed**

```bash
python3 --version
python3 -m pip show boto3
```

* If Python is installed, you’ll see the version.
* If boto3 is installed, you’ll see its version and location.

**If boto3 is not installed**, run:

```bash
python3 -m pip install boto3
```

---

## **Step 3: Create a test Python script**

You can either run interactively or create a file. Let’s create a file:

```bash
echo 'import boto3

s3 = boto3.client("s3")
try:
    response = s3.list_objects_v2(Bucket="ts-audio-ilakkm-aug31")
    if "Contents" in response:
        print("S3 access: OK, found objects:")
        for obj in response["Contents"]:
            print(" -", obj["Key"])
    else:
        print("S3 access: OK, but bucket is empty")
except Exception as e:
    print("S3 access failed:", e)
' > test_s3.py
```

---

## **Step 4: Run the script inside the container**

```bash
python3 test_s3.py
```

* **Expected output if credentials are correct and bucket exists:**

```
S3 access: OK, found objects:
 - _next/
 - 0586022e-d355-4320-8799-730a144d0cfe.mp3
 - ...
```

* **If it fails**, you’ll see the exact error message (like `AccessDenied` or `NoSuchBucket`).

---

## **Step 5: Interpret results**

1. **If the script succeeds** → your environment variables and credentials are correct. The problem is **likely in your FastAPI health check code**.
2. **If the script fails** → check the error. Common causes inside Docker:

   * AWS credentials not being passed correctly (`env` shows they are OK in your case, so unlikely).
   * Region mismatch (`us-east-1` vs another).
   * Typo in bucket name.

---

If you want, I can also give you a **ready-to-use modified `/health` endpoint** for FastAPI that prints **both Polly and S3 status** with exact error messages, so you can see immediately what fails inside the container.

Do you want me to do that?
