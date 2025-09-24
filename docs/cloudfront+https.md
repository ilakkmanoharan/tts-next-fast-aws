Let’s set up **CloudFront + HTTPS** for your S3-hosted frontend so your site is secure and can call your backend over HTTPS. I’ll give **step-by-step commands and explanations**.

---

## **Step 1: Request an SSL certificate via ACM**

CloudFront requires an SSL certificate in **us-east-1** (even if your bucket is in another region).

```bash
aws acm request-certificate \
  --domain-name ilakkmanoharan5840-frontend.com \
  --validation-method DNS \
  --region us-east-1
```

* Replace `ilakkmanoharan5840-frontend.com` with your **custom domain** (if you don’t have one, skip SSL for now; CloudFront gives you a default `cloudfront.net` domain).
* The command returns a **Certificate ARN**, e.g.:

```
arn:aws:acm:us-east-1:681916125840:certificate/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Save this ARN; you’ll need it for CloudFront.

---

## **Step 2: Create CloudFront distribution for S3**

If using your **S3 static site bucket**:

```bash
aws cloudfront create-distribution \
  --origin-domain-name ilakkmanoharan5840-frontend.s3.amazonaws.com \
  --default-root-object index.html \
  --enabled
```

* `--origin-domain-name` → your S3 bucket website endpoint (`s3-website-us-east-1.amazonaws.com`), **not** the ARN.
* This creates a CloudFront distribution with a default HTTPS URL: something like:

```
https://d1234567890abcdef.cloudfront.net
```

> You can use this URL immediately or attach your custom domain later.

---

## **Step 3: Configure CloudFront for custom domain and SSL (optional)**

1. Update the distribution to use your **ACM certificate** and **custom domain**:

```bash
aws cloudfront update-distribution \
  --id <DISTRIBUTION_ID> \
  --distribution-config file://distribution-config.json
```

* `<DISTRIBUTION_ID>` → get from:

```bash
aws cloudfront list-distributions
```

* `distribution-config.json` → a JSON file with updated settings, including:

```json
{
  "Origins": {
    "Items": [
      {
        "Id": "S3-ilakkmanoharan5840-frontend",
        "DomainName": "ilakkmanoharan5840-frontend.s3.amazonaws.com",
        "OriginPath": "",
        "CustomHeaders": {
          "Quantity": 0
        },
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ],
    "Quantity": 1
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-ilakkmanoharan5840-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": { "Forward": "none" }
    }
  },
  "ViewerCertificate": {
    "ACMCertificateArn": "arn:aws:acm:us-east-1:681916125840:certificate/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  },
  "Enabled": true
}
```

* Replace `ACMCertificateArn` with your actual ARN.
* `ViewerProtocolPolicy: redirect-to-https` ensures HTTP → HTTPS automatically.

---

## **Step 4: Update frontend to use CloudFront URL**

1. Replace your backend ALB URL if you want frontend → backend calls over HTTPS (CloudFront handles HTTPS for frontend, backend must allow CORS if using different domain):

```env
NEXT_PUBLIC_API_BASE_URL=http://backend-xxxxxxx.us-east-1.elb.amazonaws.com
```

* You may later change it to **HTTPS** if backend has HTTPS enabled.

2. Rebuild and deploy frontend:

```bash
npm run build
npm run export
aws s3 sync out/ s3://ilakkmanoharan5840-frontend --delete
```

---

## **Step 5: Test**

* Open your CloudFront URL (or custom domain) in a browser:

```
https://d1234567890abcdef.cloudfront.net
```

* Verify:

  * Site loads over HTTPS
  * API calls reach backend correctly

---

✅ **Optional enhancements:**

* Add **CloudFront caching** or invalidation for updates:

```bash
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*"
```

* Set **CORS on backend** to allow frontend CloudFront domain.

---

You can create a **ready-to-use script with all commands**: S3 bucket sync + CloudFront setup + ACM SSL + backend URL update so you can deploy everything **in one go**.

