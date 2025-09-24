

ECR Repository URI

{
    "repositories": [
        {
            "repositoryArn": "arn:aws:ecr:us-east-1:123456789012:repository/tts-backend",
            "registryId": "123456789012",
            "repositoryName": "tts-backend",
            "repositoryUri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/tts-backend",
            "createdAt": "2025-09-20T22:00:00Z",
            "imageTagMutability": "MUTABLE",
            "imageScanningConfiguration": {"scanOnPush": false}
        }
    ]
}

123456789012.dkr.ecr.us-east-1.amazonaws.com/tts-backend


_______

ECR Log in:

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

Login Succeeded

_____________

aws iam attach-user-policy \
    --user-name tts-cli-user \      
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess

_______________

ilakkuvaselvimanoharan@MacBookPro backend % aws iam list-attached-user-policies --user-name tts-cli-user      

{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonAPIGatewayAdministrator",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
:...skipping...
{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonAPIGatewayAdministrator",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "AmazonS3FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
:...skipping...
{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonAPIGatewayAdministrator",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "AmazonS3FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
        },
:...skipping...
{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonAPIGatewayAdministrator",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "AmazonS3FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
        },
        {
            "PolicyName": "AWSCodeDeployRoleForCloudFormation",
:...skipping...
{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonAPIGatewayAdministrator",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "AmazonS3FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
        },
        {
            "PolicyName": "AWSCodeDeployRoleForCloudFormation",
            "PolicyArn": "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForCloudFormation"
        },
:...skipping...
{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonAPIGatewayAdministrator",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "AmazonS3FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
        },
        {
            "PolicyName": "AWSCodeDeployRoleForCloudFormation",
            "PolicyArn": "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForCloudFormation"
        },
        {
            "PolicyName": "AWSCloudFormationFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess"
        },
:...skipping...
{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonAPIGatewayAdministrator",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "AmazonS3FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
        },
        {
            "PolicyName": "AWSCodeDeployRoleForCloudFormation",
            "PolicyArn": "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForCloudFormation"
        },
        {
            "PolicyName": "AWSCloudFormationFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess"
        },
        {
            "PolicyName": "AWSLambda_FullAccess",
:...skipping...
{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonAPIGatewayAdministrator",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "AmazonS3FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
        },
        {
            "PolicyName": "AWSCodeDeployRoleForCloudFormation",
            "PolicyArn": "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForCloudFormation"
        },
        {
            "PolicyName": "AWSCloudFormationFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess"
        },
        {
            "PolicyName": "AWSLambda_FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
        },
        {
:...skipping...
{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonAPIGatewayAdministrator",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "AmazonS3FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
        },
        {
            "PolicyName": "AWSCodeDeployRoleForCloudFormation",
            "PolicyArn": "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForCloudFormation"
        },
        {
            "PolicyName": "AWSCloudFormationFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess"
        },
        {
            "PolicyName": "AWSLambda_FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
        },
        {
            "PolicyName": "AmazonS3ObjectLambdaExecutionRolePolicy",
            "PolicyArn": "arn:aws:iam::aws:policy/service-role/AmazonS3ObjectLambdaExecutionRolePolicy"
        }
    ]
}
(END)
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
        },
        {
            "PolicyName": "AWSCloudFormationReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationReadOnlyAccess"
        },
        {
            "PolicyName": "AmazonEC2ContainerRegistryFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
        },
        {
            "PolicyName": "IAMFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"
        },
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        {
            "PolicyName": "AmazonS3FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
        },
        {
            "PolicyName": "AWSCodeDeployRoleForCloudFormation",
            "PolicyArn": "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForCloudFormation"
        },
        {
            "PolicyName": "AWSCloudFormationFullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess"
        },
        {
            "PolicyName": "AWSLambda_FullAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
        },
        {
            "PolicyName": "AmazonS3ObjectLambdaExecutionRolePolicy",
            "PolicyArn": "arn:aws:iam::aws:policy/service-role/AmazonS3ObjectLambdaExecutionRolePolicy"
        }
    ]
}

_____________________


ilakkuvaselvimanoharan@MacBookPro backend % aws ecr describe-repositories --repository-names tts-backend --region us-east-1

{
    "repositories": [
        {
            "repositoryArn": "arn:aws:ecr:us-east-1:681916125840:repository/tts-backend",
            "registryId": "681916125840",
            "repositoryName": "tts-backend",
            "repositoryUri": "681916125840.dkr.ecr.us-east-1.amazonaws.com/tts-backend",
            "createdAt": "2025-08-31T22:41:01.272000-05:00",
            "imageTagMutability": "MUTABLE",
            "imageScanningConfiguration": {
                "scanOnPush": false
            },
            "encryptionConfiguration": {
                "encryptionType": "AES256"
            }
        }
    ]
}

_______________________________________________

ilakkuvaselvimanoharan@MacBookPro backend % copilot env ls

dev

__________________________


✔ Deployed service backend.
Recommended follow-up action:
  - Your service is accessible at http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com over the internet

  ______________________________________________

   copilot app ls

tts-next-app
tts-next-fast-aws

______________________________________________

ilakkuvaselvimanoharan@MacBookPro backend % copilot env ls --app tts-next-fast-aws
dev
ilakkuvaselvimanoharan@MacBookPro backend % copilot svc ls --app tts-next-fast-aws

Name                Type
----                ----
backend             Load Balanced Web Service

lakkuvaselvimanoharan@MacBookPro backend % copilot svc show --name backend --app tts-next-fast-aws

About

  Application  tts-next-fast-aws
  Name         backend
  Type         Load Balanced Web Service

Configurations

  Environment  Tasks     CPU (vCPU)  Memory (MiB)  Platform      Port
  -----------  -----     ----------  ------------  --------      ----
  dev          1         0.25        512           LINUX/X86_64  8000

Routes

  Environment  URL
  -----------  ---
  dev          http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com

Internal Service Endpoints

  Endpoint                                  Environment  Type
  --------                                  -----------  ----
  backend.dev.tts-next-fast-aws.local:8000  dev          Service Discovery

Variables

  Name                                Container  Environment  Value
  ----                                ---------  -----------  -----
  COPILOT_APPLICATION_NAME            backend    dev          tts-next-fast-aws
  COPILOT_ENVIRONMENT_NAME              "          "          dev
  COPILOT_LB_DNS                        "          "          tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com
  COPILOT_SERVICE_DISCOVERY_ENDPOINT    "          "          dev.tts-next-fast-aws.local
  COPILOT_SERVICE_NAME                  "          "          backend
  ENV                                   "          "          dev


  _____________________________________________________________

  
