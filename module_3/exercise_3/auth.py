"""
Authentication logic for user management.
"""

import hashlib
from user import User

# In-memory user storage (for practice purposes)
users_db = {}


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, email, password):
    """
    Register a new user in the system.
    
    Args:
        username (str): Desired username
        email (str): User's email address
        password (str): Plain text password
    
    Returns:
        User: The newly created user object
    """
    # This function needs error handling for duplicate usernames
    password_hash = hash_password(password)
    user = User(username, email, password_hash)
    users_db[username] = user
    return user


def authenticate_user(username, password):
    """
    Authenticate a user with username and password.
    
    Args:
        username (str): Username to authenticate
        password (str): Password to verify
    
    Returns:
        User or None: User object if authenticated, None otherwise
    """
    user = users_db.get(username)
    password_hash = hash_password(password)
    
    if user.password_hash == password_hash and user.is_active:
        return user
    return None


def get_user(username):
    """
    Retrieve a user by username.
    
    Args:
        username (str): Username to look up
    
    Returns:
        User or None: User object if found, None otherwise
    """
    return users_db.get(username)


def delete_user(username):
    """
    Delete a user from the system.
    
    Args:
        username (str): Username to delete
    
    Returns:
        bool: True if deleted, False if user not found
    """
    if username in users_db:
        del users_db[username]
        return True
    return False
