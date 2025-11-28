from storages.backends.s3boto3 import S3Boto3Storage #This allow django to store files in Amazon s3
from django.conf import settings

class PrivateMediaStorage(S3Boto3Storage):
    default_acl = 'private'  #only authorized users or backend can access the file
    location = 'private'  #All files will be stored in the private/ folder inside S3 bucket
    file_overwrite = False #Prevents overwriting files if a file with the same name is uploaded( S3 will automatically add a unique suffix to the new file )
    querystring_auth = True  # Enables pre-signed URLs for access
    bucket_name = settings.AWS_BUCKET_NAME  # Tell Django which S3 bucket to use

class PublicMediaStorage(S3Boto3Storage):
    # default_acl = 'public-read'
    location = 'public'
    file_overwrite = False
    bucket_name = settings.AWS_BUCKET_NAME
    default_acl=None