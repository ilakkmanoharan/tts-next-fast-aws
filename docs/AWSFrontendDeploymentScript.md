##### 2.1

Here’s a **ready-to-use deployment script** for your frontend + CloudFront + optional SSL setup, along with backend integration. I’ll break it into sections and you can run them step by step from your **frontend folder**.

---

# **AWS Frontend Deployment Script for ilakkmanoharan5840-frontend**

### **Step 0: Set environment variables**

```bash
# Frontend S3 bucket
FRONTEND_BUCKET="ilakkmanoharan5840-frontend"

# Optional custom domain (skip if you don’t have one)
CUSTOM_DOMAIN="ilakkmanoharan5840-frontend.com"

# Backend ALB URL (from Copilot deployment)
BACKEND_URL="http://<backend-alb>.us-east-1.elb.amazonaws.com"

# AWS region
REGION="us-east-1"
```

---

### **Step 1: Build frontend**

```bash
# If using Next.js
npm run build
npm run export  # Generates 'out/' folder
```

---

### **Step 2: Sync frontend to S3**

```bash
aws s3 sync out/ s3://$FRONTEND_BUCKET --delete
```

---

### **Step 3: Enable static website hosting**

```bash
aws s3 website s3://$FRONTEND_BUCKET/ --index-document index.html --error-document index.html
```

* You can now access: `http://$FRONTEND_BUCKET.s3-website-$REGION.amazonaws.com`

---

### **Step 4: Request SSL certificate (optional if using custom domain)**

```bash
aws acm request-certificate \
  --domain-name $CUSTOM_DOMAIN \
  --validation-method DNS \
  --region $REGION
```

* Save the returned `Certificate ARN` (we’ll use it in CloudFront).

---

### **Step 5: Create CloudFront distribution**

#### **5a: Without custom domain**

```bash
aws cloudfront create-distribution \
  --origin-domain-name $FRONTEND_BUCKET.s3.amazonaws.com \
  --default-root-object index.html \
  --enabled
```

#### **5b: With custom domain (HTTPS)**

1. Create JSON config `distribution-config.json`:

```json
{
  "Origins": {
    "Items": [
      {
        "Id": "S3-ilakkmanoharan5840-frontend",
        "DomainName": "ilakkmanoharan5840-frontend.s3.amazonaws.com",
        "OriginPath": "",
        "S3OriginConfig": { "OriginAccessIdentity": "" }
      }
    ],
    "Quantity": 1
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-ilakkmanoharan5840-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": { "Quantity": 2, "Items": ["GET", "HEAD"] },
    "ForwardedValues": { "QueryString": false, "Cookies": { "Forward": "none" } }
  },
  "ViewerCertificate": {
    "ACMCertificateArn": "arn:aws:acm:us-east-1:681916125840:certificate/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  },
  "Enabled": true
}
```

2. Create distribution using:

```bash
aws cloudfront create-distribution --distribution-config file://distribution-config.json
```

---

### **Step 6: Update frontend to call backend**

1. Open your frontend `.env` or `config.js` and set:

```env
NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL
```

* Example:

```env
NEXT_PUBLIC_API_BASE_URL=http://backend-xxxxxxx.us-east-1.elb.amazonaws.com
```

2. Rebuild and sync again if updated:

```bash
npm run build
npm run export
aws s3 sync out/ s3://$FRONTEND_BUCKET --delete
```

---

### **Step 7: (Optional) Invalidate CloudFront cache**

```bash
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*"
```

* `<DISTRIBUTION_ID>` → get from:

```bash
aws cloudfront list-distributions
```

---

### ✅ **Step 8: Test**

* Visit CloudFront URL (or custom domain) and check:

  * Frontend loads correctly
  * API calls reach your backend

---

You can **write a single bash script** that automatically:

1. Builds frontend
2. Syncs to S3
3. Creates/updates CloudFront
4. Updates backend URL in `.env`

so that you just run **one command** to deploy.


