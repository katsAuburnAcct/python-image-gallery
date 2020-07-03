import logging
import boto3
from botocore.exceptions import ClientError

BUCKET = 'edu.au.cc.kats-image-gallery'

def upload_file(filePath):
    """
    Function to upload a file to an S3 bucket
    """
    file_name = filePath.replace('uploads/', '')
    print(file_name)
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(filePath, BUCKET, object_name)

    return response

def download_file(file_name):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource('s3')
    output = f"downloads/{file_name}"
    s3.Bucket(BUCKET).download_file(file_name, output)

    return output

def delete_object(imagekey):
    s3= boto3.resource('s3')
    s3.Object(BUCKET, imagekey).delete()


