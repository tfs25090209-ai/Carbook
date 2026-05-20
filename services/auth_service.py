"""Authentication service for user management."""

import logging
from typing import Optional, Dict, Tuple
from database import db
from utils.auth import AuthUtils

logger = logging.getLogger(__name__)


class AuthService:
    """Service for user authentication and registration."""

    @staticmethod
    def register(
        username: str,
        email: str,
        password: str,
        full_name: str,
        phone: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Register a new user."""
        # Validate inputs
        valid, error = AuthUtils.validate_username(username)
        if not valid:
            return False, error

        if not AuthUtils.validate_email(email):
            return False, "Invalid email format"

        valid, error = AuthUtils.validate_password(password)
        if not valid:
            return False, error

        if phone and not AuthUtils.validate_phone(phone):
            return False, "Invalid phone number format"

        # Check if username already exists
        existing = db.fetch_one(
            "SELECT id FROM users WHERE username = %s",
            (username,)
        )
        if existing:
            return False, "Username already taken"

        # Check if email already exists
        existing = db.fetch_one(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )
        if existing:
            return False, "Email already registered"

        # Hash password and insert user
        password_hash = AuthUtils.hash_password(password)

        user_id = db.insert("users", {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "phone": phone,
            "role": "customer"
        })

        if user_id:
            logger.info(f"User registered: {username}")
            return True, "Registration successful"

        return False, "Registration failed"

    @staticmethod
    def login(identifier: str, password: str) -> Tuple[bool, str]:
        """Authenticate a user by username or email."""
        if not identifier or not password:
            return False, "Username/email and password are required"

        # Find user by username or email so demo accounts can use email login.
        user = db.fetch_one(
            "SELECT * FROM users "
            "WHERE (username = %s OR email = %s) AND is_active = TRUE",
            (identifier, identifier)
        )

        if not user:
            return False, "Invalid username or password"

        # Verify password
        if not AuthUtils.verify_password(password, user["password_hash"]):
            return False, "Invalid username or password"

        # Check if user is active
        if not user["is_active"]:
            return False, "Account is disabled"

        logger.info(f"User logged in: {user['username']}")
        return True, user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Get user details by ID."""
        return db.fetch_one(
            "SELECT id, username, email, full_name, phone, role, created_at "
            "FROM users WHERE id = %s",
            (user_id,)
        )
