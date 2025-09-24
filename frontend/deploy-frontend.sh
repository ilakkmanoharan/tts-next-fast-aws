#!/bin/bash
set -e

########################################
# Configuration - Update these values
########################################

# Replace with your actual backend ALB URL
BACKEND_ALB_URL="http://tts-ne-Publi-j6NoWpqH34EH-112063658.us-east-1.elb.amazonaws.com"

# S3 bucket name for frontend
FRONTEND_BUCKET="ilakkmanoharan5840-frontend"

# AWS region of your bucket
REGION="us-east-1"

# Optional: Custom domain for CloudFront (leave empty if not using)
CUSTOM_DOMAIN=""

########################################
# Step 1: Update frontend environment
########################################

echo "Setting backend URL in .env.local..."
echo "NEXT_PUBLIC_BACKEND_URL=$BACKEND_ALB_URL" > .env.local

########################################
# Step 2: Build frontend
########################################

echo "Installing dependencies..."
npm install

echo "Building frontend..."
npm run build

########################################
# Step 3: Upload to S3
########################################

echo "Syncing build output to S3 bucket $FRONTEND_BUCKET..."
aws s3 sync out/ s3://$FRONTEND_BUCKET --delete

# Enable static website hosting
aws s3 website s3://$FRONTEND_BUCKET/ --index-document index.html --error-document index.html

########################################
# Step 4: Create CloudFront distribution (if no custom domain)
########################################

if [ -z "$CUSTOM_DOMAIN" ]; then
    echo "Creating CloudFront distribution without custom domain..."

    # Create a temporary JSON file for the distribution config
    DIST_CONFIG=$(mktemp)
    cat > $DIST_CONFIG <<EOL
{
    "CallerReference": "$(date +%s)",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "$FRONTEND_BUCKET",
                "DomainName": "$FRONTEND_BUCKET.s3.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "$FRONTEND_BUCKET",
        "ViewerProtocolPolicy": "allow-all",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0
    },
    "Comment": "CloudFront distribution for $FRONTEND_BUCKET",
    "Enabled": true,
    "DefaultRootObject": "index.html"
}
EOL

    DISTRIBUTION_ID=$(aws cloudfront create-distribution \
        --distribution-config file://$DIST_CONFIG \
        --query 'Distribution.Id' --output text)

    rm -f $DIST_CONFIG
    echo "CloudFront distribution created: $DISTRIBUTION_ID"

    # Wait 30s for initialization
    sleep 30
else
    echo "Custom domain detected. Please manually configure ACM and CloudFront."
    DISTRIBUTION_ID=""
fi

########################################
# Step 5: Invalidate CloudFront cache
########################################

if [ -n "$DISTRIBUTION_ID" ]; then
    echo "Invalidating CloudFront cache..."
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id $DISTRIBUTION_ID \
        --paths "/*" \
        --query 'Invalidation.Id' --output text)
    echo "Invalidation submitted: $INVALIDATION_ID"
fi

########################################
# Step 6: Finish
########################################

echo "Deployment complete!"
if [ -n "$DISTRIBUTION_ID" ]; then
    DOMAIN_NAME=$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.DomainName' --output text)
    echo "CloudFront Distribution ID: $DISTRIBUTION_ID"
    echo "URL: https://$DOMAIN_NAME"
else
    echo "S3 Static website URL: http://$FRONTEND_BUCKET.s3-website-$REGION.amazonaws.com"
fi
