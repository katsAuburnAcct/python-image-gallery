import logging
import boto3
import os
from botocore.exceptions import ClientError


S3_IMAGE_BUCKET = os.environ.get('S3_IMAGE_BUCKET')
BUCKET = 'edu.au.cc.kats-image-gallery'

if S3_IMAGE_BUCKET:
    BUCKET = S3_IMAGE_BUCKET
    print('S3_IMAGE_BUCKET in if statement')
    print(S3_IMAGE_BUCKET)
# BUCKET = 'edu.au.cc.kats-image-gallery'

def upload_file(filePath):
    """
    Function to upload a file to an S3 bucket
    """
    file_name = filePath.replace('gallery/ui/uploads/', '')
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(filePath, BUCKET, object_name)

    return response

def download_file(file_name):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource('s3')
    output = f"gallery/ui/downloads/{file_name}"
    s3.Bucket(BUCKET).download_file(file_name, output)

    return output

def delete_object(imagekey):
    s3= boto3.resource('s3')
    s3.Object(BUCKET, imagekey).delete()


