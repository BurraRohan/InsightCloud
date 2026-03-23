"""
s3_utils.py — AWS S3 helper functions for InsightCloud.
Used when STORAGE_MODE is "s3". All S3 operations are isolated here
so the rest of the app doesn't need to know about AWS SDK details.
"""

import io
from typing import Optional

import boto3
import pandas as pd
from botocore.exceptions import ClientError, NoCredentialsError

from config import AWS_REGION, AWS_S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def get_s3_client():
    """
    Create and return a boto3 S3 client.

    Uses explicit credentials if provided (for local development),
    otherwise falls back to IAM role credentials (recommended for EC2 production).

    Returns:
        boto3 S3 client instance.
    """
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        # Local development — use explicit credentials from .env
        return boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    else:
        # Production on EC2 — use IAM role (more secure, no keys needed)
        return boto3.client("s3", region_name=AWS_REGION)


def upload_to_s3(file_bytes: bytes, filename: str, content_type: str = "text/csv") -> dict:
    """
    Upload a file to the S3 bucket.

    Args:
        file_bytes: Raw file content as bytes.
        filename: Name of the file to store.
        content_type: MIME type of the file (default: text/csv).

    Returns:
        Dictionary with success status, S3 key, and bucket name.
    """
    s3 = get_s3_client()
    key = f"uploads/{filename}"  # Store under uploads/ prefix in bucket

    try:
        s3.put_object(
            Bucket=AWS_S3_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
            ServerSideEncryption="AES256"  # Encrypt at rest
        )
        return {"success": True, "key": key, "bucket": AWS_S3_BUCKET}
    except (ClientError, NoCredentialsError) as e:
        return {"success": False, "error": str(e)}


def download_from_s3(filename: str) -> Optional[bytes]:
    """
    Download a file from S3 and return as bytes.

    Args:
        filename: Name of the file to download.

    Returns:
        File content as bytes, or None if not found.
    """
    s3 = get_s3_client()
    key = f"uploads/{filename}"

    try:
        response = s3.get_object(Bucket=AWS_S3_BUCKET, Key=key)
        return response["Body"].read()
    except ClientError:
        return None


def list_s3_files() -> list:
    """
    List all CSV files in the S3 uploads/ prefix.

    Returns:
        List of dictionaries with filename, size_kb, and last_modified.
    """
    s3 = get_s3_client()

    try:
        response = s3.list_objects_v2(Bucket=AWS_S3_BUCKET, Prefix="uploads/")

        if "Contents" not in response:
            return []

        files = []
        for obj in response["Contents"]:
            filename = obj["Key"].replace("uploads/", "")
            if filename and filename.endswith(".csv"):
                files.append({
                    "filename": filename,
                    "size_kb": round(obj["Size"] / 1024, 1),
                    "last_modified": obj["LastModified"].strftime("%Y-%m-%d %H:%M")
                })
        return files
    except (ClientError, NoCredentialsError):
        return []


def delete_from_s3(filename: str) -> bool:
    """
    Delete a file from S3.

    Args:
        filename: Name of the file to delete.

    Returns:
        True if deletion was successful, False otherwise.
    """
    s3 = get_s3_client()
    key = f"uploads/{filename}"

    try:
        s3.delete_object(Bucket=AWS_S3_BUCKET, Key=key)
        return True
    except ClientError:
        return False


def get_s3_file_as_dataframe(filename: str) -> Optional[pd.DataFrame]:
    """
    Download a CSV from S3 and return as a pandas DataFrame.

    Args:
        filename: Name of the CSV file to load.

    Returns:
        pandas DataFrame, or None if download failed.
    """
    file_bytes = download_from_s3(filename)
    if file_bytes is None:
        return None
    return pd.read_csv(io.BytesIO(file_bytes))
