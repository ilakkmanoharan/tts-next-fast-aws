You can verify which IAM user your Docker container (or local AWS CLI) is using with a few quick commands. Here’s how:

---

### 1️⃣ Check IAM user via AWS CLI locally

Run:

```bash
aws sts get-caller-identity
```

You’ll get output like:

```json
{
    "UserId": "AIDAEXAMPLEID",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/YourUserName"
}
```

* The **`Arn`** field tells you the IAM user.
* Make sure this matches the user whose keys you’re passing into Docker (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`).

---

### 2️⃣ Check IAM user inside Docker container

You can run a temporary shell in the container:

```bash
docker exec -it tts-backend /bin/sh
```

Then run inside the container:

```bash
aws sts get-caller-identity
```

This will tell you which IAM credentials the container is actually using.

---

### 3️⃣ Verify S3 permissions

Once you know the IAM user:

```bash
aws s3 ls s3://ts-audio-ilakkm-aug31 --region us-east-1
```

* If this works → your IAM user has correct S3 access.
* If you still see `AccessDenied` → you need to attach the correct policy to this user.

---

If you want, I can give you **a one-liner to quickly test the container’s IAM user and S3 access** without manually opening a shell. It’s fast and safe.

Do you want me to do that?

Here’s a quick one-liner to run inside your Docker container (or directly via `docker exec`) that **checks the IAM user and S3 access in one go**:

```bash
docker exec -it tts-backend sh -c 'echo "IAM User:"; aws sts get-caller-identity --query Arn --output text; echo "S3 Access Test:"; aws s3 ls s3://ts-audio-ilakkm-aug31 --region us-east-1'
```

✅ What it does:

1. Prints the **IAM user ARN** the container is using.
2. Attempts to **list the S3 bucket contents** to confirm access.

* If the S3 command works → your IAM user has the correct permissions.
* If it fails with `AccessDenied` → the IAM policy needs to be fixed or the keys are wrong.

---

If you want, I can also give a **shortcut command that updates the IAM policy, restarts the container, and tests S3 in one step**. It’s super convenient for local development.

Do you want me to provide that?



ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % aws sts get-caller-identity

{
    "UserId": "AIDAZ5RK6KKIDWUTTYOL3",
    "Account": "681916125840",
    "Arn": "arn:aws:iam::681916125840:user/tts-cli-user"
}

