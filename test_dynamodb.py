#!/usr/bin/env python3
import boto3
import json

# Configuration
DYNAMODB_TABLE = "dataiesb-reports"
AWS_REGION = "us-east-1"

def test_dynamodb_connection():
    try:
        # Create DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        print(f"Testing connection to DynamoDB table: {DYNAMODB_TABLE}")
        print(f"Region: {AWS_REGION}")
        
        # Test table description
        response = table.meta.client.describe_table(TableName=DYNAMODB_TABLE)
        print(f"✅ Table exists and is accessible")
        print(f"Table status: {response['Table']['TableStatus']}")
        print(f"Item count: {response['Table']['ItemCount']}")
        
        # Test scan operation
        print("\n🔍 Testing scan operation...")
        response = table.scan(Limit=5)  # Limit to 5 items for testing
        
        if 'Items' in response:
            print(f"✅ Scan successful! Found {len(response['Items'])} items")
            
            # Show structure of first item (without sensitive data)
            if response['Items']:
                first_item = response['Items'][0]
                print(f"Sample item keys: {list(first_item.keys())}")
                
                # Check if required fields exist
                required_fields = ['report_id', 'titulo', 'descricao', 'autor', 'deletado', 'user_email', 'created_at', 'updated_at', 'id_s3']
                missing_fields = [field for field in required_fields if field not in first_item]
                
                if missing_fields:
                    print(f"⚠️  Missing fields in items: {missing_fields}")
                else:
                    print("✅ All required fields present in items")
        else:
            print("⚠️  No items found in table")
            
    except Exception as e:
        print(f"❌ Error testing DynamoDB connection: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Check if it's a permissions issue
        if "AccessDenied" in str(e) or "UnauthorizedOperation" in str(e):
            print("🔐 This appears to be a permissions issue. Check IAM policies.")
        elif "ResourceNotFoundException" in str(e):
            print("🔍 Table not found. Check table name and region.")
        elif "EndpointConnectionError" in str(e):
            print("🌐 Network connectivity issue. Check internet connection and region.")

if __name__ == "__main__":
    test_dynamodb_connection()
