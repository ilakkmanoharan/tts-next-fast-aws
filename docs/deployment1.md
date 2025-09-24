To deploy your backend (running on port 8000) to **AWS ECS using Fargate**

---

## 1. Prerequisites

Make sure you have these installed:

```bash
# AWS CLI v2
brew install awscli

# Docker
brew install --cask docker
open /Applications/Docker.app   # start Docker desktop

# AWS Copilot CLI (optional but easier for ECS Fargate)
brew install aws/tap/copilot-cli
```

Configure AWS credentials:

```bash
aws configure
# enter Access Key, Secret Key, region (ex: us-east-1), output format (json)
```

---

## 2. Build and Tag Docker Image

Inside your backend project folder:

```bash
# Build docker image
docker build -t my-backend-app .

# Tag it for ECR (replace ACCOUNT_ID and REGION)
aws sts get-caller-identity --query Account --output text
# suppose ACCOUNT_ID=123456789012, REGION=us-east-1

docker tag my-backend-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-backend-app:latest
```

---

## 3. Create ECR Repository and Push Image

```bash
# Create ECR repo
aws ecr create-repository --repository-name my-backend-app

# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Push image
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-backend-app:latest
```

---

## 4. Create ECS Cluster (Fargate)

```bash
aws ecs create-cluster --cluster-name my-backend-cluster
```

---

## 5. Create Task Definition

Create a file `task-def.json` in VS Code:

```json
{
  "family": "my-backend-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "my-backend-container",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-backend-app:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true
    }
  ]
}
```

Register task definition:

```bash
aws ecs register-task-definition --cli-input-json file://task-def.json
```

---

## 6. Create Security Group (Allow 8000)

```bash
# Create SG
aws ec2 create-security-group --group-name backend-sg --description "Allow 8000" --vpc-id vpc-xxxxxxx

# Authorize inbound TCP 8000
aws ec2 authorize-security-group-ingress \
  --group-name backend-sg \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0
```

---

## 7. Run ECS Service with Fargate

```bash
aws ecs create-service \
  --cluster my-backend-cluster \
  --service-name backend-service \
  --task-definition my-backend-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxx],securityGroups=[sg-xxxxxx],assignPublicIp=ENABLED}"
```

---

## 8. Get Public IP

```bash
aws ecs list-tasks --cluster my-backend-cluster
# get TASK_ARN

aws ecs describe-tasks --cluster my-backend-cluster --tasks TASK_ARN
# find ENI ID (networkInterfaceId)

aws ec2 describe-network-interfaces --network-interface-ids eni-xxxxxx \
  --query 'NetworkInterfaces[0].Association.PublicIp' --output text
```

Now open in browser:

```
http://<PUBLIC_IP>:8000
```

---

## 9. (Optional) Connect CloudFront / Route53

* **CloudFront** → Create distribution pointing to the public load balancer/endpoint.
* **Route53** → Register domain and map to CloudFront or ECS service’s load balancer DNS name.

