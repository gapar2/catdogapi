#!/bin/sh

S3_BUCKET="custom-labels-console-us-east-1-1bea3ee6af"

# We unzip the data
unzip animals10.zip 

# and we upload to S3, one prefix per category
cd raw-img/
aws s3 sync . s3://$S3_BUCKET/animals10_catdog/
