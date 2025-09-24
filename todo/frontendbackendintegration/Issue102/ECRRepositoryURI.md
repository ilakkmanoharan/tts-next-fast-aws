ECR repository URI

Got it — let’s find your **ECR repository URI** step by step. There are two main ways: **AWS Console** and **AWS CLI**.

---

## **Option 1 — AWS Management Console**

1. Go to the **AWS Management Console**.
2. Navigate to **Elastic Container Registry (ECR)**.
3. Click **Repositories** in the left menu.
4. Find your repository (e.g., `tts-backend`).
5. Click the repository name — you will see the **URI** at the top, which looks like:

```
123456789012.dkr.ecr.us-east-1.amazonaws.com/tts-backend
```

> The format is: `<account-id>.dkr.ecr.<region>.amazonaws.com/<repository-name>`

---

## **Option 2 — AWS CLI**

If you know the repository name (`tts-backend`), run:

```bash
aws ecr describe-repositories --repository-names tts-backend --region us-east-1
```

You’ll get JSON output like:

```json
{
    "repositories": [
        {
            "repositoryArn": "arn:aws:ecr:us-east-1:123456789012:repository/tts-backend",
            "registryId": "123456789012",
            "repositoryName": "tts-backend",
            "repositoryUri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/tts-backend",
            ...
        }
    ]
}
```

* Copy the **`repositoryUri`** value — this is what Docker needs to tag and push the image.

---

Once you have the URI, the next step is:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <repository-uri without repo name>
```

For example:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

---

I can write you the **full sequence of commands** from tagging the image → pushing → updating ECS service, all ready to run.

Do you want me to do that?
