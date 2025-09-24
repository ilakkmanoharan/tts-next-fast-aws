## 2.2

Here’s a **ready-to-run bash deployment script** for your frontend + CloudFront + backend integration. You just need to place it in your **frontend folder** and run it. It automates build, sync to S3, CloudFront distribution, and backend URL update.

---

### **`deploy-frontend.sh`**

```bash
#!/bin/bash
set -e

###########################
# Configurations
###########################

# S3 bucket
FRONTEND_BUCKET="ilakkmanoharan5840-frontend"

# Optional custom domain (leave empty if not using)
CUSTOM_DOMAIN=""

# Backend ALB URL from Copilot
BACKEND_URL="http://<backend-alb>.us-east-1.elb.amazonaws.com"

# AWS region
REGION="us-east-1"

# Frontend build folder
BUILD_FOLDER="out"

###########################
# Step 1: Update frontend backend URL
###########################

echo "Updating frontend backend URL..."
# For Next.js, assuming .env.local exists
if [ -f ".env.local" ]; then
  sed -i '' "/NEXT_PUBLIC_API_BASE_URL=/d" .env.local
  echo "NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL" >> .env.local
else
  echo "NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL" > .env.local
fi

###########################
# Step 2: Build frontend
###########################

echo "Building frontend..."
npm install
npm run build
npm run export

###########################
# Step 3: Sync frontend to S3
###########################

echo "Syncing frontend to S3 bucket: $FRONTEND_BUCKET"
aws s3 sync $BUILD_FOLDER/ s3://$FRONTEND_BUCKET --delete

###########################
# Step 4: Enable static website hosting
###########################

echo "Enabling static website hosting on S3 bucket..."
aws s3 website s3://$FRONTEND_BUCKET/ --index-document index.html --error-document index.html

###########################
# Step 5: Create CloudFront distribution
###########################

if [ -z "$CUSTOM_DOMAIN" ]; then
  echo "Creating CloudFront distribution without custom domain..."
  DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --origin-domain-name $FRONTEND_BUCKET.s3.amazonaws.com \
    --default-root-object index.html \
    --enabled \
    --query 'Distribution.Id' --output text)
else
  echo "Custom domain detected. Please manually configure ACM and CloudFront."
  DISTRIBUTION_ID=""
fi

echo "Deployment complete!"
if [ -n "$DISTRIBUTION_ID" ]; then
  echo "CloudFront Distribution ID: $DISTRIBUTION_ID"
  echo "URL: https://$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.DomainName' --output text)"
else
  echo "S3 Static website URL: http://$FRONTEND_BUCKET.s3-website-$REGION.amazonaws.com"
fi
```

---

### **Usage Instructions**

1. Save the file as `deploy-frontend.sh` in your frontend folder.
2. Make it executable:

```bash
chmod +x deploy-frontend.sh
```

3. Run the script:

```bash
./deploy-frontend.sh
```

4. After it finishes:

   * Check the S3 website URL if no CloudFront.
   * Check CloudFront distribution if created.

---

This script handles:

* `.env.local` backend URL update
* Frontend build & export
* S3 sync
* Static website hosting
* Optional CloudFront creation

---

You can also **update this script** to automatically **invalidate CloudFront cache** whenever you redeploy, so users always see the latest frontend.

