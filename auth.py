"""
auth.py — JWT authentication logic for InsightCloud.
Handles user signup, login, token generation, and verification.
Uses passlib for password hashing and python-jose for JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config import SECRET_KEY, ALGORITHM, TOKEN_EXPIRY_HOURS
from models import User

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password: The plain-text password to hash.

    Returns:
        The bcrypt-hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a hashed password.

    Args:
        plain: The plain-text password to verify.
        hashed: The bcrypt-hashed password to compare against.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain, hashed)


def create_token(data: dict) -> str:
    """
    Create a JWT access token with an expiry time.

    Args:
        data: Dictionary of claims to encode in the token (e.g., {"sub": email}).

    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.

    Args:
        token: The JWT token string to verify.

    Returns:
        The decoded payload dictionary if valid, None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def signup_user(email: str, full_name: str, password: str, role: str, db: Session) -> dict:
    """
    Register a new user in the database.

    Args:
        email: User's email address (must be unique).
        full_name: User's display name.
        password: Plain-text password (will be hashed before storage).
        role: User role — one of 'analyst', 'admin', 'viewer'.
        db: SQLAlchemy database session.

    Returns:
        Dictionary with JWT token and user info.

    Raises:
        ValueError: If a user with the given email already exists.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValueError("An account with this email already exists.")

    # Create new user with hashed password
    new_user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        role=role.lower()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    token = create_token({"sub": new_user.email, "role": new_user.role})

    return {
        "token": token,
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role
        }
    }


def login_user(email: str, password: str, db: Session) -> dict:
    """
    Authenticate a user with email and password.

    Args:
        email: User's email address.
        password: Plain-text password to verify.
        db: SQLAlchemy database session.

    Returns:
        Dictionary with JWT token and user info.

    Raises:
        ValueError: If credentials are invalid.
    """
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Invalid email or password.")

    # Verify password
    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password.")

    # Generate JWT token
    token = create_token({"sub": user.email, "role": user.role})

    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }
