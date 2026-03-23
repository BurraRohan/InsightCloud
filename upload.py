"""
upload.py — CSV upload, validation, and storage for InsightCloud.
Supports DUAL MODE: local file system and AWS S3.
Reads STORAGE_MODE from config to decide which storage backend to use.
"""

import io
import os
from typing import Optional, Tuple

import pandas as pd

from config import UPLOAD_DIR, is_aws_mode
from s3_utils import upload_to_s3, list_s3_files, get_s3_file_as_dataframe


def ensure_upload_dir() -> None:
    """
    Create the local uploads/ directory if it doesn't exist.
    Only needed in local storage mode.
    """
    if not is_aws_mode():
        os.makedirs(UPLOAD_DIR, exist_ok=True)


def validate_csv(uploaded_file) -> Tuple[bool, str]:
    """
    Validate that an uploaded file is a proper, readable CSV.

    Checks:
        1. File extension must be .csv
        2. File size must be under 50MB
        3. File must be readable by pandas

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        Tuple of (is_valid: bool, message: str).
    """
    # Check file extension
    if not uploaded_file.name.lower().endswith(".csv"):
        return False, "Invalid file type. Please upload a CSV file (.csv)."

    # Check file size (50MB limit)
    max_size = 50 * 1024 * 1024  # 50MB in bytes
    if uploaded_file.size > max_size:
        return False, f"File too large ({uploaded_file.size / (1024*1024):.1f}MB). Maximum size is 50MB."

    # Try reading the CSV to verify it's valid
    try:
        pd.read_csv(uploaded_file)
        uploaded_file.seek(0)  # Reset file pointer after reading
        return True, "Valid CSV file."
    except Exception as e:
        uploaded_file.seek(0)  # Reset file pointer even on error
        return False, f"Unable to read CSV file: {str(e)}"


def save_file(uploaded_file) -> dict:
    """
    Save an uploaded CSV file to local storage OR S3 based on config.

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        Dictionary with upload result including filename, row/column counts,
        column names, file size, and storage location.
    """
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name

    try:
        if is_aws_mode():
            # Upload to AWS S3
            result = upload_to_s3(file_bytes, filename)
            if not result["success"]:
                return {"success": False, "error": result["error"]}
        else:
            # Save to local file system
            ensure_upload_dir()
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(file_bytes)

        # Parse CSV to get metadata
        df = pd.read_csv(io.BytesIO(file_bytes))
        return {
            "success": True,
            "filename": filename,
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": list(df.columns),
            "size_kb": round(len(file_bytes) / 1024, 1),
            "storage": "s3" if is_aws_mode() else "local"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files() -> list:
    """
    List all uploaded CSV files from local storage OR S3.

    Returns:
        List of dictionaries with filename and size info.
    """
    if is_aws_mode():
        return list_s3_files()
    else:
        if not os.path.exists(UPLOAD_DIR):
            return []
        files = []
        for f in os.listdir(UPLOAD_DIR):
            if f.endswith(".csv"):
                filepath = os.path.join(UPLOAD_DIR, f)
                files.append({
                    "filename": f,
                    "size_kb": round(os.path.getsize(filepath) / 1024, 1)
                })
        return files


def load_file_as_df(filename: str) -> Optional[pd.DataFrame]:
    """
    Load a CSV file as a pandas DataFrame from local storage OR S3.

    Args:
        filename: Name of the CSV file to load.

    Returns:
        pandas DataFrame, or None if file not found.
    """
    if is_aws_mode():
        return get_s3_file_as_dataframe(filename)
    else:
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        return None
