import os
import uuid

import boto3

S3_BUCKET_NAME = 'nkb-backend-ccbp-media-static'
S3_REGION_NAME = 'ap-south-1'
S3_UPLOAD_FOLDER = 'ccbp_beta/media/content_loading/uploads/'


def upload_to_s3(cred, file_path):
    """Upload a file to S3 using the provided credentials."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=cred['aws_access_key_id'],
        aws_secret_access_key=cred['aws_secret_access_key'],
        aws_session_token=cred['aws_session_token'],
        region_name='ap-south-1'
    )

    # Generate a unique file name using UUID
    file_name = os.path.basename(file_path)
    unique_file_name = f"{uuid.uuid4()}_{file_name}"
    s3_key = f"{S3_UPLOAD_FOLDER}{unique_file_name}"

    try:
        print(f"Uploading file {file_path} to S3 bucket at {s3_key}")
        s3_client.upload_file(file_path, 'nkb-backend-ccbp-media-static', s3_key, ExtraArgs={'ACL': 'public-read'})
        s3_file_url = f"https://nkb-backend-ccbp-media-static.s3.ap-south-1.amazonaws.com/{s3_key}"
        print(f"File uploaded successfully to: {s3_file_url}")
        return s3_file_url
    except Exception as e:
        print(f"Failed to upload to S3: {e}")
        return None
