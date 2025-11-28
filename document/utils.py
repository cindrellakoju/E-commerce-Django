# utils.py
import boto3
from django.conf import settings
from botocore.client import Config

def private_profile_upload_to(instance, filename):
    # instance.id is the user ID
    return f'{instance.id}/profile/{filename}'

def public_upload_to(instance, filename):
    return f'{instance.id}/items/{filename}'


def generate_presigned_url(key,public, expiration=3600):
    """
    Generate a pre-signed URL to access a private S3 file.

    :param key: Path of the file in S3 (e.g., 'private/42/profile/avatar.png')
    :param expiration: URL valid duration in seconds (default 1 hour)
    :return: Pre-signed URL string
    """
    if public:
        s3_key = f'public/{key}' 
    else:
        s3_key = f'private/{key}' 
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        config=Config(signature_version='s3v4')
    )

    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': settings.AWS_BUCKET_NAME,
            'Key': s3_key
        },
        ExpiresIn=expiration
    )

    return url
