# Step-by-step — attach the S3 inline policy to your ECS **task** role

Nice and practical — below I’ll show CLI and Console ways, how to find the task role, how to attach the exact JSON you provided, how to verify, and quick troubleshooting notes.

---

## Prereqs

* AWS CLI installed and configured (`aws --version`, `aws sts get-caller-identity` works).
* Your IAM user/role must have permissions to call `ecs:DescribeTaskDefinition` (or `ecs:DescribeTasks`) and `iam:PutRolePolicy` / `iam:GetRolePolicy`.
* Know either the ECS task definition name/revision (e.g. `my-task:3`) or the running task id + cluster.

---

## 1) Get the ECS task role ARN

**If you have the task definition name/revision:**

```bash
aws ecs describe-task-definition \
  --task-definition <task-def-family[:revision]> \
  --query 'taskDefinition.taskRoleArn' --output text
```

Example output:

```
arn:aws:iam::123456789012:role/ecsTaskRole
```

**If you only have a running task id (get its taskDefinitionArn first):**

```bash
aws ecs describe-tasks --cluster <cluster-name> --tasks <task-id> \
  --query 'tasks[0].taskDefinitionArn' --output text

# then:
aws ecs describe-task-definition --task-definition <taskDefinitionArn> \
  --query 'taskDefinition.taskRoleArn' --output text
```

If the `taskRoleArn` output is `None` or `null` there is no task role configured — see the extra section below on creating one.

---

## 2) Extract the **role name** from the ARN (CLI-friendly)

Bash:

```bash
TASK_ROLE_ARN=$(aws ecs describe-task-definition \
  --task-definition <task-def> --query 'taskDefinition.taskRoleArn' --output text)

ROLE_NAME=${TASK_ROLE_ARN##*/}
echo "$ROLE_NAME"
```

PowerShell:

```powershell
$taskRoleArn = (aws ecs describe-task-definition --task-definition <task-def> --query 'taskDefinition.taskRoleArn' --output text)
$roleName = $taskRoleArn.Split('/')[-1]
$roleName
```

> `put-role-policy` expects the **role name** (not the full ARN). The extraction above returns the text after the final `/`.

---

## 3) Create the policy JSON file (`s3-audio-policy.json`)

Create a file in your shell (example using Bash `cat <<EOF`):

```bash
cat > s3-audio-policy.json <<'JSON'
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
JSON
```

(You can also edit the file with your editor and paste the JSON you supplied.)

---

## 4) Attach the policy to the role (inline policy)

Run:

```bash
aws iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name S3AudioAccess \
  --policy-document file://s3-audio-policy.json
```

Windows PowerShell (if not using the `$ROLE_NAME` var):

```powershell
aws iam put-role-policy --role-name MyEcsTaskRole --policy-name S3AudioAccess --policy-document file://C:\path\to\s3-audio-policy.json
```

This creates an **inline** role policy named `S3AudioAccess` on the role.

---

## 5) Verify the policy is attached

List inline policies on the role:

```bash
aws iam list-role-policies --role-name "$ROLE_NAME" --output text
```

Get the policy document:

```bash
aws iam get-role-policy --role-name "$ROLE_NAME" --policy-name S3AudioAccess --query 'PolicyDocument' --output json
```

You should see the JSON you added.

---

## 6) Test (how to confirm access works from the task)

Preferred (if your container has AWS CLI and ECS Exec enabled):

```bash
aws ecs execute-command \
  --cluster <cluster-name> --task <task-id> --container <container-name> \
  --command "aws s3 ls s3://ts-audio-ilakkm-aug31" --interactive
```

This runs the `aws s3` command inside the container using the task role credentials — a direct test.

If you cannot use ECS Exec:

* Check CloudWatch logs from your application for `AccessDenied` errors when it tries to access that bucket.
* Or deploy a short one-off task that runs `aws s3 ls s3://ts-audio-ilakkm-aug31` (the task uses that role).

---

## Console alternative (UI)

1. Open AWS Console → **IAM** → **Roles** → search role name (extract from ARN if needed).
2. Open the role → **Add inline policy**.
3. Choose the **JSON** tab → paste the `s3-audio-policy.json` contents → **Review policy** → name it `S3AudioAccess` → **Create policy**.

---

## If there is **no** task role on the task definition

You’ll need to create an IAM role with the ECS trust policy and then update/register the task definition to reference that role.

Create a trust policy (`trust.json`):

```json
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Principal":{"Service":"ecs-tasks.amazonaws.com"},
      "Action":"sts:AssumeRole"
    }
  ]
}
```

Create the role:

```bash
aws iam create-role --role-name my-ecs-task-role --assume-role-policy-document file://trust.json
```

Then attach your `s3-audio-policy.json` as shown earlier, and update your ECS task definition (or register a new revision) with `--task-role-arn arn:aws:iam::<acct-id>:role/my-ecs-task-role`.

---

## Troubleshooting & gotchas

* You must have `iam:PutRolePolicy` permission to run `put-role-policy`.
* `taskRoleArn` vs `executionRoleArn`: your app (inside container) uses **taskRoleArn**. `executionRoleArn` is for ECS agent (pulling images, logs).
* If the bucket is in a *different AWS account*, bucket policy must allow access for this role principal.
* If you still see `AccessDenied`, check for Service Control Policies (SCPs) or explicit Deny policies applied higher up in AWS Organizations.
* Inline policy name must be unique per role. If a policy with the same name exists, `put-role-policy` will overwrite it.
* To use managed policies instead, create a managed policy (`create-policy`) and `attach-role-policy` — handy if multiple roles should share the same policy.

---

If you want, I can:

* produce the exact shell snippet (single script) that does steps 1–4 for a given `<task-def>` (Bash + safe checks), or
* show the `aws iam create-policy` + `attach-role-policy` flow instead of inline policy.

Which would you like me to provide now?
