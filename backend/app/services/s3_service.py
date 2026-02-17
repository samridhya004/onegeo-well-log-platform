import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_S3_BUCKET]):
    raise ValueError("AWS configuration missing in .env")

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def upload_file_to_s3(file_obj, filename: str):
    """
    Uploads file-like object to S3 bucket.
    Returns the S3 object URL.
    """
    s3_client.upload_fileobj(
        file_obj,
        AWS_S3_BUCKET,
        filename,
        ExtraArgs={"ContentType": "application/octet-stream"}
    )

    return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"
