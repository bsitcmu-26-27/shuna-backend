# storage.py
import os
import uuid
import boto3
import config
from bottle import redirect, response, HTTPError

s3 = boto3.client(
    "s3",
    endpoint_url=config.endpoint_url,
    aws_access_key_id=config.aws_access_key_id,
    aws_secret_access_key=config.aws_secret_access_key,
    region_name=config.region_name,
    config=boto3.session.Config(s3={"addressing_style": "path"}),  # Neon requires path-style
)
BUCKET = config.BUCKET

def upload_image(image_bytes: bytes, content_type: str) -> str:
    key = f"{uuid.uuid4()}.webp"
    s3.put_object(Bucket=BUCKET, Key=key, Body=image_bytes, ContentType=content_type)
    return key

def image_url(key: str) -> str:
    return f"{os.environ['NEON_S3_ENDPOINT']}/{BUCKET}/{key}"

def file_serve(filename):
        try:
                presigned_url = s3.generate_presigned_url(
                        'get_object',
                        Params={"Bucket": BUCKET, 'Key': filename},
                        ExpiresIn=3600
                        )
                #redirect(presigned_url, code=302)
                print(presigned_url)
                return presigned_url
        except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchKey':
                        return HTTPError(404, "File not found")
                elif e.response['Error']['Code'] == 'AccessDenied':
                        return HTTPError(403, "Access denied")
                else:
                        return HTTPError(500, "Internal server error")


