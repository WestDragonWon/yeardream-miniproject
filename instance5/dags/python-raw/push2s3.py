import boto3

# Initialize the S3 client
s3_client = boto3.client('s3')

# Define your bucket name and file details
bucket_name = 'team06-mlflow-feature'
file_path = 'data/employees.csv'  # Local file path
s3_key = 'data/employees.csv'        # S3 path where you want to upload

# Upload file to S3
s3_client.upload_file(file_path, bucket_name, s3_key)

print(f'File uploaded to S3://{bucket_name}/{s3_key}')

