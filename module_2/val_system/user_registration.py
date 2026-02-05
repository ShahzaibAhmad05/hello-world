"""
User Registration System
Provides email validation, password requirements, duplicate checking, and JWT token generation
"""

import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import jwt


class PasswordValidator:
    """Validates password requirements"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        """
        Validate password against requirements:
        - At least 8 characters
        - Contains uppercase letter
        - Contains lowercase letter
        - Contains digit
        - Contains special character
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < PasswordValidator.MIN_LENGTH:
            return False, f"Password must be at least {PasswordValidator.MIN_LENGTH} characters long"
        
        if len(password) > PasswordValidator.MAX_LENGTH:
            return False, f"Password must not exceed {PasswordValidator.MAX_LENGTH} characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
        
        return True, "Password is valid"


class EmailValidator:
    """Validates email addresses"""
    
    # RFC 5322 compliant email regex (simplified)
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    @staticmethod
    def validate(email: str) -> Tuple[bool, str]:
        """
        Validate email address format
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not email:
            return False, "Email cannot be empty"
        
        if len(email) > 254:
            return False, "Email address is too long"
        
        if not EmailValidator.EMAIL_REGEX.match(email):
            return False, "Invalid email format"
        
        # Check for common typos
        local_part, _, domain = email.partition('@')
        
        if not domain:
            return False, "Email must contain @ symbol"
        
        if '..' in email:
            return False, "Email cannot contain consecutive dots"
        
        if not domain.count('.'):
            return False, "Email domain must contain at least one dot"
        
        return True, "Email is valid"


class UserRegistrationSystem:
    """Main user registration system"""
    
    def __init__(self, user_store, jwt_secret: Optional[str] = None):
        """
        Initialize registration system
        
        Args:
            user_store: User storage instance (must implement check_duplicate and save_user methods)
            jwt_secret: Secret key for JWT token generation (auto-generated if not provided)
        """
        self.user_store = user_store
        self.jwt_secret = jwt_secret or secrets.token_urlsafe(32)
        self.email_validator = EmailValidator()
        self.password_validator = PasswordValidator()
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash password using SHA-256 with salt
        
        Args:
            password: Plain text password
            salt: Salt for hashing (generated if not provided)
        
        Returns:
            Tuple[str, str]: (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine password and salt
        salted_password = f"{password}{salt}"
        
        # Hash using SHA-256
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        
        return hashed, salt
    
    def generate_jwt_token(self, user_id: str, email: str, expiry_hours: int = 24) -> str:
        """
        Generate JWT token for authenticated user
        
        Args:
            user_id: Unique user identifier
            email: User email address
            expiry_hours: Token expiry time in hours (default: 24)
        
        Returns:
            str: JWT token
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expiry_hours)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return token
    
    def verify_jwt_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
        
        Returns:
            Tuple[bool, Optional[Dict]]: (is_valid, payload)
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return False, {'error': 'Invalid token'}
    
    def register_user(self, email: str, password: str, username: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Register a new user
        
        Args:
            email: User email address
            password: User password
            username: Optional username
        
        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, jwt_token)
        """
        # Validate email
        email_valid, email_msg = self.email_validator.validate(email)
        if not email_valid:
            return False, f"Email validation failed: {email_msg}", None
        
        # Normalize email to lowercase
        email = email.lower().strip()
        
        # Check for duplicate email
        if self.user_store.check_duplicate(email):
            return False, "Email address already registered", None
        
        # Validate password
        password_valid, password_msg = self.password_validator.validate(password)
        if not password_valid:
            return False, f"Password validation failed: {password_msg}", None
        
        # Hash password
        hashed_password, salt = self._hash_password(password)
        
        # Generate user ID
        user_id = secrets.token_urlsafe(16)
        
        # Create user record
        user_data = {
            'user_id': user_id,
            'email': email,
            'username': username or email.split('@')[0],
            'password_hash': hashed_password,
            'salt': salt,
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True
        }
        
        # Save user
        save_success = self.user_store.save_user(user_data)
        
        if not save_success:
            return False, "Failed to save user to database", None
        
        # Generate JWT token
        jwt_token = self.generate_jwt_token(user_id, email)
        
        return True, f"User registered successfully with email: {email}", jwt_token
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Authenticate existing user
        
        Args:
            email: User email address
            password: User password
        
        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, jwt_token)
        """
        email = email.lower().strip()
        
        # Get user from store
        user_data = self.user_store.get_user_by_email(email)
        
        if not user_data:
            return False, "Invalid email or password", None
        
        # Verify password
        hashed_input, _ = self._hash_password(password, user_data['salt'])
        
        if hashed_input != user_data['password_hash']:
            return False, "Invalid email or password", None
        
        if not user_data.get('is_active', True):
            return False, "Account is deactivated", None
        
        # Generate new JWT token
        jwt_token = self.generate_jwt_token(user_data['user_id'], email)
        
        return True, "Authentication successful", jwt_token
