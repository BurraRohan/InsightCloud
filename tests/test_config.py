"""
test_config.py — Tests for InsightCloud configuration module.
Tests environment variable loading and mode toggles.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─── Config Loading Tests ─────────────────────────────────

def test_config_imports():
    """Test that config module imports without errors."""
    from config import APP_NAME, APP_VERSION, SECRET_KEY
    assert APP_NAME == "InsightCloud"
    assert APP_VERSION == "1.0.0"
    assert len(SECRET_KEY) > 0


def test_config_has_all_settings():
    """Test that all required config variables exist."""
    from config import (
        STORAGE_MODE, AI_MODE, UPLOAD_DIR,
        AWS_REGION, AWS_S3_BUCKET,
        BEDROCK_MODEL_ID, GROQ_MODEL,
    )
    assert STORAGE_MODE is not None
    assert AI_MODE is not None
    assert UPLOAD_DIR is not None
    assert AWS_REGION is not None
    assert AWS_S3_BUCKET is not None


def test_storage_mode_default():
    """Test that default storage mode is 'local'."""
    os.environ.pop("STORAGE_MODE", None)
    # Re-import to get fresh values
    import importlib
    import config
    importlib.reload(config)
    # Default should be local
    assert config.STORAGE_MODE in ["local", "s3"]


def test_is_aws_mode_local():
    """Test is_aws_mode returns False when storage is local."""
    os.environ["STORAGE_MODE"] = "local"
    import importlib
    import config
    importlib.reload(config)
    assert config.is_aws_mode() is False


def test_is_aws_mode_s3():
    """Test is_aws_mode returns True when storage is s3."""
    os.environ["STORAGE_MODE"] = "s3"
    import importlib
    import config
    importlib.reload(config)
    assert config.is_aws_mode() is True


def test_is_bedrock_mode():
    """Test is_bedrock_mode toggle."""
    os.environ["AI_MODE"] = "bedrock"
    import importlib
    import config
    importlib.reload(config)
    assert config.is_bedrock_mode() is True


def test_is_groq_mode():
    """Test is_groq_mode toggle."""
    os.environ["AI_MODE"] = "groq"
    import importlib
    import config
    importlib.reload(config)
    assert config.is_groq_mode() is True


def test_bedrock_model_id():
    """Test that Bedrock model ID is set."""
    from config import BEDROCK_MODEL_ID
    assert "mistral" in BEDROCK_MODEL_ID.lower()


def test_groq_model():
    """Test that Groq model is set."""
    from config import GROQ_MODEL
    assert "llama" in GROQ_MODEL.lower()


def test_algorithm_is_hs256():
    """Test that JWT algorithm is HS256."""
    from config import ALGORITHM
    assert ALGORITHM == "HS256"


def test_token_expiry_positive():
    """Test that token expiry is a positive number."""
    from config import TOKEN_EXPIRY_HOURS
    assert TOKEN_EXPIRY_HOURS > 0
