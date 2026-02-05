"""
User model for authentication system.
"""

class User:
    """
    Represents a user in the system.
    
    Attributes:
        username (str): The user's unique username
        email (str): The user's email address
        password_hash (str): Hashed password for security
        is_active (bool): Whether the user account is active
        created_at (str): Timestamp of account creation
    """
    
    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = True
        self.created_at = None
    
    def activate(self):
        """Activate the user account."""
        self.is_active = True
    
    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False
    
    def update_email(self, new_email):
        """Update user's email address."""
        self.email = new_email
    
    def __repr__(self):
        return f"User(username='{self.username}', email='{self.email}', active={self.is_active})"
