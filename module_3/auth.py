"""
Authentication functions with rate limiting and credential verification.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from models import User
import time


class RateLimiter:
    """
    Rate limiter to prevent brute force attacks.
    
    Tracks login attempts by username/IP and enforces cooldown periods.
    """
    
    def __init__(self, max_attempts=5, lockout_duration_minutes=15):
        """
        Initialize rate limiter.
        
        Args:
            max_attempts: Maximum login attempts before lockout
            lockout_duration_minutes: How long to lock out after max attempts
        """
        self.max_attempts = max_attempts
        self.lockout_duration = timedelta(minutes=lockout_duration_minutes)
        self.attempt_cache = {}  # {username: {'attempts': int, 'locked_until': datetime}}
    
    def is_locked_out(self, username: str) -> Tuple[bool, Optional[int]]:
        """
        Check if a username is currently locked out.
        
        Args:
            username: Username to check
            
        Returns:
            Tuple of (is_locked, seconds_remaining)
        """
        if username not in self.attempt_cache:
            return False, None
        
        cache_entry = self.attempt_cache[username]
        locked_until = cache_entry.get('locked_until')
        
        if locked_until and datetime.utcnow() < locked_until:
            seconds_remaining = int((locked_until - datetime.utcnow()).total_seconds())
            return True, seconds_remaining
        
        # Lockout expired, clean up
        if locked_until and datetime.utcnow() >= locked_until:
            del self.attempt_cache[username]
            return False, None
        
        return False, None
    
    def record_failed_attempt(self, username: str):
        """
        Record a failed login attempt.
        
        Args:
            username: Username that failed to login
        """
        if username not in self.attempt_cache:
            self.attempt_cache[username] = {'attempts': 0, 'locked_until': None}
        
        self.attempt_cache[username]['attempts'] += 1
        
        if self.attempt_cache[username]['attempts'] >= self.max_attempts:
            self.attempt_cache[username]['locked_until'] = (
                datetime.utcnow() + self.lockout_duration
            )
    
    def reset_attempts(self, username: str):
        """
        Reset failed attempts after successful login.
        
        Args:
            username: Username to reset
        """
        if username in self.attempt_cache:
            del self.attempt_cache[username]


# Global rate limiter instance
rate_limiter = RateLimiter(max_attempts=5, lockout_duration_minutes=15)


def login(db_session: Session, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
    """
    Authenticate user credentials with rate limiting.
    
    Args:
        db_session: SQLAlchemy database session
        username: Username to authenticate
        password: Password to verify
        
    Returns:
        Tuple of (success, message, user_object)
        - success: True if login successful, False otherwise
        - message: Human-readable result message
        - user_object: User instance if successful, None otherwise
    """
    # Check rate limiting first
    is_locked, seconds_remaining = rate_limiter.is_locked_out(username)
    if is_locked:
        minutes = seconds_remaining // 60
        seconds = seconds_remaining % 60
        return (
            False,
            f"Account temporarily locked. Try again in {minutes}m {seconds}s.",
            None
        )
    
    # Query user from database
    user = db_session.query(User).filter_by(username=username).first()
    
    if not user:
        # Record failed attempt even if user doesn't exist (prevent enumeration)
        rate_limiter.record_failed_attempt(username)
        time.sleep(0.5)  # Slight delay to slow down brute force
        return False, "Invalid username or password.", None
    
    # Check if account is active
    if not user.is_active:
        return False, "Account is disabled. Contact support.", None
    
    # Verify password
    if not user.check_password(password):
        # Record failed attempt
        rate_limiter.record_failed_attempt(username)
        user.increment_failed_attempts()
        db_session.commit()
        time.sleep(0.5)  # Slight delay to slow down brute force
        return False, "Invalid username or password.", None
    
    # Successful login
    rate_limiter.reset_attempts(username)
    user.reset_failed_attempts()
    db_session.commit()
    
    return True, "Login successful!", user


def register_user(db_session: Session, username: str, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
    """
    Register a new user account.
    
    Args:
        db_session: SQLAlchemy database session
        username: Desired username
        email: User's email address
        password: Plain text password (will be hashed)
        
    Returns:
        Tuple of (success, message, user_object)
    """
    # Validate inputs
    if len(username) < 3:
        return False, "Username must be at least 3 characters long.", None
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long.", None
    
    # Check if username already exists
    existing_user = db_session.query(User).filter_by(username=username).first()
    if existing_user:
        return False, "Username already taken.", None
    
    # Check if email already exists
    existing_email = db_session.query(User).filter_by(email=email).first()
    if existing_email:
        return False, "Email already registered.", None
    
    # Create new user
    try:
        new_user = User(username=username, email=email, password=password)
        db_session.add(new_user)
        db_session.commit()
        return True, "User registered successfully!", new_user
    except Exception as e:
        db_session.rollback()
        return False, f"Registration failed: {str(e)}", None


def logout(user: User) -> Tuple[bool, str]:
    """
    Logout user (placeholder for session cleanup).
    
    Args:
        user: User object to logout
        
    Returns:
        Tuple of (success, message)
    """
    # In a full implementation, this would clear session tokens, etc.
    return True, f"User {user.username} logged out successfully."
