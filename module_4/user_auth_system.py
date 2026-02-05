import os
import re
from typing import Optional, Dict, Any
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# filepath: c:\Users\shahz\Projects\hello-world\module_4\user_auth_system.py

"""
User Authentication System

This module provides secure user authentication with password hashing,
user registration, and login functionality following OWASP security guidelines.
"""



class UserAuthSystem:
    """
    Handles user authentication operations including registration and login.
    Uses Argon2 for secure password hashing.
    """

    def __init__(self) -> None:
        """Initialize the authentication system with Argon2 password hasher."""
        self.password_hasher = PasswordHasher()
        self.users_db: Dict[str, Dict[str, Any]] = {}

    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if email is valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_password(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        return True, ""

    def register_user(self, email: str, password: str, username: str) -> tuple[bool, str]:
        """
        Register a new user with email and password.

        Args:
            email: User's email address (sanitized input)
            password: User's password (will be hashed)
            username: User's display name

        Returns:
            Tuple of (success, message)
        """
        # Input sanitization
        email = email.strip().lower()
        username = username.strip()

        # Validate email
        if not self._validate_email(email):
            return False, "Invalid email format"

        # Check if user already exists
        if email in self.users_db:
            return False, "User already exists"

        # Validate password strength
        is_valid, error_msg = self._validate_password(password)
        if not is_valid:
            return False, error_msg

        # Hash password using Argon2
        try:
            hashed_password = self.password_hasher.hash(password)
        except Exception as e:
            return False, f"Error hashing password: {str(e)}"

        # Store user data
        self.users_db[email] = {
            'username': username,
            'password_hash': hashed_password,
            'is_authenticated': False
        }

        return True, "User registered successfully"

    def login_user(self, email: str, password: str) -> tuple[bool, str]:
        """
        Authenticate user with email and password.

        Args:
            email: User's email address
            password: User's password

        Returns:
            Tuple of (success, message)
        """
        email = email.strip().lower()

        # Check if user exists
        if email not in self.users_db:
            # Why: Use generic message to prevent user enumeration attacks
            return False, "Invalid credentials"

        user = self.users_db[email]

        # Verify password
        try:
            self.password_hasher.verify(user['password_hash'], password)
            
            # Check if password needs rehashing (Argon2 best practice)
            if self.password_hasher.check_needs_rehash(user['password_hash']):
                user['password_hash'] = self.password_hasher.hash(password)
            
            user['is_authenticated'] = True
            return True, "Login successful"

        except VerifyMismatchError:
            return False, "Invalid credentials"
        except Exception as e:
            return False, f"Authentication error: {str(e)}"

    def logout_user(self, email: str) -> tuple[bool, str]:
        """
        Logout user by email.

        Args:
            email: User's email address

        Returns:
            Tuple of (success, message)
        """
        email = email.strip().lower()

        if email not in self.users_db:
            return False, "User not found"

        self.users_db[email]['is_authenticated'] = False
        return True, "Logout successful"

    def is_user_authenticated(self, email: str) -> bool:
        """
        Check if user is currently authenticated.

        Args:
            email: User's email address

        Returns:
            True if user is authenticated, False otherwise
        """
        email = email.strip().lower()
        return self.users_db.get(email, {}).get('is_authenticated', False)