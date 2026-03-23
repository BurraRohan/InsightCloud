"""
config.py — Centralized configuration for InsightCloud.
Reads from .env file. Toggles between local mode and AWS mode.
Toggles between Gemini, Groq (local testing — FREE) and Bedrock (AWS production).
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── App Settings ───────────────────────────────────────────
APP_NAME = "InsightCloud"
APP_VERSION = "1.0.0"
SECRET_KEY = os.getenv("SECRET_KEY", "insightcloud-dev-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

# ─── Storage Mode: "local" or "s3" ─────────────────────────
STORAGE_MODE = os.getenv("STORAGE_MODE", "local")

# ─── AI Mode: "gemini", "groq" (free local) or "bedrock" (AWS prod) ─
AI_MODE = os.getenv("AI_MODE", "gemini")

# ─── Local Storage ─────────────────────────────────────────
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# ─── AWS Settings ──────────────────────────────────────────
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "insightcloud-uploads")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# ─── AWS Bedrock (used when AI_MODE=bedrock) ───────────────
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "mistral.ministral-3-8b-instruct")

# ─── Google Gemini (used when AI_MODE=gemini — FREE) ───────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ─── Groq (used when AI_MODE=groq — FREE, no credit card) ──
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ─── Database ──────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./insightcloud.db")


def is_aws_mode() -> bool:
    """Check if running in AWS/S3 mode."""
    return STORAGE_MODE.lower() == "s3"


def is_bedrock_mode() -> bool:
    """Check if using AWS Bedrock for AI."""
    return AI_MODE.lower() == "bedrock"


def is_groq_mode() -> bool:
    """Check if using Groq for AI."""
    return AI_MODE.lower() == "groq"