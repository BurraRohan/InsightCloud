"""
test_auth.py — Tests for InsightCloud authentication module.
Tests password hashing, JWT tokens, signup, and login.
"""

import pytest
import os
import sys

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import hash_password, verify_password, create_token, verify_token, signup_user, login_user
from database import init_db, SessionLocal, Base, engine
from models import User


# ─── Setup & Teardown ──────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a database session for tests."""
    session = SessionLocal()
    yield session
    session.close()


# ─── Password Hashing Tests ───────────────────────────────

def test_hash_password_returns_string():
    """Test that hash_password returns a string."""
    hashed = hash_password("test123")
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_hash_password_not_plain_text():
    """Test that hashed password is NOT the same as plain text."""
    password = "mypassword"
    hashed = hash_password(password)
    assert hashed != password


def test_hash_password_different_each_time():
    """Test that hashing the same password twice gives different results (salt)."""
    hashed1 = hash_password("samepassword")
    hashed2 = hash_password("samepassword")
    assert hashed1 != hashed2


def test_verify_password_correct():
    """Test that correct password verification returns True."""
    password = "testpass123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test that wrong password verification returns False."""
    hashed = hash_password("correctpassword")
    assert verify_password("wrongpassword", hashed) is False


# ─── JWT Token Tests ──────────────────────────────────────

def test_create_token_returns_string():
    """Test that create_token returns a JWT string."""
    token = create_token({"sub": "test@test.com", "role": "analyst"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token_valid():
    """Test that a valid token can be decoded."""
    data = {"sub": "test@test.com", "role": "analyst"}
    token = create_token(data)
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test@test.com"
    assert payload["role"] == "analyst"


def test_verify_token_invalid():
    """Test that an invalid token returns None."""
    result = verify_token("this.is.not.a.valid.token")
    assert result is None


def test_verify_token_has_expiry():
    """Test that token payload contains expiry claim."""
    token = create_token({"sub": "test@test.com"})
    payload = verify_token(token)
    assert "exp" in payload


# ─── Signup Tests ─────────────────────────────────────────

def test_signup_creates_user(db):
    """Test that signup creates a new user and returns token."""
    result = signup_user("new@test.com", "Test User", "password123", "analyst", db)
    assert "token" in result
    assert result["user"]["email"] == "new@test.com"
    assert result["user"]["full_name"] == "Test User"
    assert result["user"]["role"] == "analyst"


def test_signup_hashes_password(db):
    """Test that signup stores hashed password, not plain text."""
    signup_user("hash@test.com", "Hash Test", "mypassword", "analyst", db)
    user = db.query(User).filter(User.email == "hash@test.com").first()
    assert user.hashed_password != "mypassword"


def test_signup_duplicate_email_raises_error(db):
    """Test that signing up with existing email raises ValueError."""
    signup_user("dup@test.com", "User One", "pass1", "analyst", db)
    with pytest.raises(ValueError, match="already exists"):
        signup_user("dup@test.com", "User Two", "pass2", "analyst", db)


def test_signup_role_is_lowercase(db):
    """Test that role is stored in lowercase."""
    result = signup_user("role@test.com", "Role Test", "pass", "Admin", db)
    assert result["user"]["role"] == "admin"


# ─── Login Tests ──────────────────────────────────────────

def test_login_valid_credentials(db):
    """Test that login works with correct credentials."""
    signup_user("login@test.com", "Login User", "correctpass", "analyst", db)
    result = login_user("login@test.com", "correctpass", db)
    assert "token" in result
    assert result["user"]["email"] == "login@test.com"


def test_login_wrong_password(db):
    """Test that login fails with wrong password."""
    signup_user("wrong@test.com", "Wrong Pass", "rightpass", "analyst", db)
    with pytest.raises(ValueError, match="Invalid email or password"):
        login_user("wrong@test.com", "wrongpass", db)


def test_login_nonexistent_email(db):
    """Test that login fails with non-existent email."""
    with pytest.raises(ValueError, match="Invalid email or password"):
        login_user("nobody@test.com", "anypass", db)


def test_login_returns_correct_role(db):
    """Test that login returns the correct user role."""
    signup_user("admin@test.com", "Admin User", "adminpass", "admin", db)
    result = login_user("admin@test.com", "adminpass", db)
    assert result["user"]["role"] == "admin"
