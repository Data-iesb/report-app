#!/bin/bash

BUCKET="dataiesb"
REGION="us-east-1"

# Enable website hosting
aws s3 website s3://$BUCKET/ \
  --index-document index.html \
  --error-document error.html

echo "✅ Website hosting enabled."

# Unblock public access protection
aws s3api put-public-access-block --bucket $BUCKET --public-access-block-configuration '{
  "BlockPublicAcls": false,
  "IgnorePublicAcls": false,
  "BlockPublicPolicy": false,
  "RestrictPublicBuckets": false
}'

echo "✅ Public access block disabled."

# Now apply the public bucket policy
aws s3api put-bucket-policy --bucket $BUCKET --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::'$BUCKET'/*"
  }]
}'

# Set CORS configuration
aws s3api put-bucket-cors --bucket $BUCKET --cors-configuration '{
  "CORSRules": [{
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "POST", "PUT", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": [],
    "MaxAgeSeconds": 3000
  }]
}'

echo "✅ CORS configuration applied."

# Output public website URL
echo "🌐 Public website is available at:"
echo "http://$BUCKET.s3-website-$REGION.amazonaws.com"

