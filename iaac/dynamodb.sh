#!/bin/bash

TABLE_NAME="dataiesb-logs"

echo "Creating DynamoDB table: $TABLE_NAME"

aws dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions \
        AttributeName=userEmail,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=userEmail,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

echo "Table creation requested. It may take a few seconds to become ACTIVE."

