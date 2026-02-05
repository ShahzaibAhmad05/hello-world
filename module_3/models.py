"""
User model with SQLAlchemy and password hashing using bcrypt.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import bcrypt

Base = declarative_base()


class User(Base):
    """
    User model for authentication system.
    
    Attributes:
        id: Primary key
        username: Unique username
        email: Unique email address
        password_hash: Bcrypt hashed password
        created_at: Account creation timestamp
        is_active: Account status flag
        failed_login_attempts: Track failed login attempts for rate limiting
        last_failed_login: Timestamp of last failed login attempt
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_failed_login = Column(DateTime, nullable=True)
    
    def __init__(self, username, email, password):
        """
        Initialize a new user with hashed password.
        
        Args:
            username: Unique username
            email: User's email address
            password: Plain text password (will be hashed)
        """
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """
        Hash and set the user's password using bcrypt.
        
        Args:
            password: Plain text password to hash
        """
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def increment_failed_attempts(self):
        """Increment failed login attempt counter."""
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.utcnow()
    
    def reset_failed_attempts(self):
        """Reset failed login attempt counter after successful login."""
        self.failed_login_attempts = 0
        self.last_failed_login = None
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
