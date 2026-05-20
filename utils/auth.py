"""Authentication utilities for Car Booking System."""

import hashlib
import secrets
import re
from typing import Optional, Dict, Tuple
from functools import wraps


class AuthUtils:
    """Utility class for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}${hash_obj.hexdigest()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify a password against a stored hash."""
        try:
            salt, hash_value = stored_hash.split("$")
            hash_obj = hashlib.sha256((password + salt).encode())
            return hash_obj.hexdigest() == hash_value
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """Validate username (3-20 chars, alphanumeric + underscore)."""
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 20:
            return False, "Username must be at most 20 characters"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, ""

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password (min 6 chars)."""
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return True  # Optional field
        pattern = r'^\+?[0-9]{10,15}$'
        return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))


class Session:
    """Session manager for authenticated users."""

    _current_user: Optional[Dict] = None

    @classmethod
    def login(cls, user: Dict) -> None:
        """Set the current logged-in user."""
        cls._current_user = user

    @classmethod
    def logout(cls) -> None:
        """Clear the current user session."""
        cls._current_user = None

    @classmethod
    def get_current_user(cls) -> Optional[Dict]:
        """Get the current logged-in user."""
        return cls._current_user

    @classmethod
    def is_logged_in(cls) -> bool:
        """Check if a user is logged in."""
        return cls._current_user is not None

    @classmethod
    def get_user_id(cls) -> Optional[int]:
        """Get the current user's ID."""
        return cls._current_user.get("id") if cls._current_user else None

    @classmethod
    def get_username(cls) -> Optional[str]:
        """Get the current user's username."""
        return cls._current_user.get("username") if cls._current_user else None

    @classmethod
    def is_admin(cls) -> bool:
        """Check if current user is an admin."""
        return cls._current_user.get("role") == "admin" if cls._current_user else False

    @classmethod
    def is_customer(cls) -> bool:
        """Check if current user is a customer."""
        return cls._current_user.get("role") == "customer" if cls._current_user else False

    @classmethod
    def get_role(cls) -> Optional[str]:
        """Get the current user's role."""
        return cls._current_user.get("role") if cls._current_user else None

    @classmethod
    def has_role(cls, role: str) -> bool:
        """Check if current user has a specific role."""
        return cls.get_role() == role


def require_admin(func):
    """Decorator to require admin role for a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not Session.is_admin():
            raise PermissionError("Admin access required")
        return func(*args, **kwargs)
    return wrapper


def require_role(required_role: str):
    """Decorator factory to require a specific role."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not Session.has_role(required_role):
                raise PermissionError(f"Access requires {required_role} role")
            return func(*args, **kwargs)
        return wrapper
    return decorator