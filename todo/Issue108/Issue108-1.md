ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % aws ecs describe-task-definition \ --task-definition tts-next-fast-aws-dev-backend:7 \ --query 'taskDefinition.taskRoleArn' \ --output text \ --region us-east-1 arn:aws:iam::681916125840:role/tts-next-fast-aws-dev-backend-TaskRole-Z4lBW81EsCnG ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % aws iam put-role-policy \ --role-name tts-next-fast-aws-dev-backend-TaskRole-Z4lBW81EsCnG \ --policy-name S3AudioAccess \ --policy-document file://s3-audio-policy.json Error parsing parameter '--policy-document': Unable to load paramfile file://s3-audio-policy.json: [Errno 2] No such file or directory: 's3-audio-policy.json' ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % ls -l s3-audio-policy.json ls: s3-audio-policy.json: No such file or directory ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % cat > s3-audio-policy.json <<'JSON' { "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Action": [ "s3:ListBucket" ], "Resource": "arn:aws:s3:::ts-audio-ilakkm-aug31" }, { "Effect": "Allow", "Action": [ "s3:GetObject", "s3:PutObject" ], "Resource": "arn:aws:s3:::ts-audio-ilakkm-aug31/*" } ] } JSON ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % ls -l s3-audio-policy.json -rw-r--r--@ 1 ilakkuvaselvimanoharan staff 364 Sep 22 14:28 s3-audio-policy.json ilakkuvaselvimanoharan@MacBookPro tts-next-fast-aws % aws iam put-role-policy \ --role-name tts-next-fast-aws-dev-backend-TaskRole-Z4lBW81EsCnG \ --policy-name S3AudioAccess \ --policy-document file://s3-audio-policy.json



Perfect ✅ — now the command should succeed because the file `s3-audio-policy.json` exists.

At this point:

1. The **inline policy `S3AudioAccess`** is attached to your ECS task role:

   ```
   tts-next-fast-aws-dev-backend-TaskRole-Z4lBW81EsCnG
   ```

2. Your ECS tasks using this role **now have permission** to `ListBucket`, `GetObject`, and `PutObject` on:

   ```
   s3://ts-audio-ilakkm-aug31
   ```

---

### Next step — make ECS pick up the new permissions

IAM permissions are loaded **when the task starts**, so any running task **won’t automatically see the new S3 access**.

✅ Steps:

1. **Stop the running ECS task(s)** (ECS will automatically start new ones with the updated role):

```bash
aws ecs list-tasks --cluster <cluster-name> --service-name <service-name> --output text
aws ecs stop-task --cluster <cluster-name> --task <task-id>
```

2. Or **update the service** to force a new task revision / redeploy.

---

### Test S3 access from inside the container (optional)

Once a new task is running, you can exec into it:

```bash
aws ecs execute-command \
  --cluster <cluster-name> \
  --task <task-id> \
  --container <container-name> \
  --command "aws s3 ls s3://ts-audio-ilakkm-aug31" \
  --interactive
```

If it lists your bucket contents without `AccessDenied`, the IAM policy is working.

---

### Re-check the health endpoint

After new tasks are running:

```bash
curl -i http://<your-elb>/health
```

* S3 should show `"ok"` instead of `"fail"`.
* Polly may still fail if the `MaxResults` parameter is present in your backend — that needs code fix.

---

If you want, I can give a **full step-by-step plan** to redeploy your ECS backend so that **both S3 and Polly health checks pass**, so the `/health` endpoint shows green.

Do you want me to do that?
