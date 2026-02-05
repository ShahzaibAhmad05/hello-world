"""
User Storage System
Provides in-memory and file-based storage for user data
"""

import json
import os
from typing import Dict, Optional, List
from threading import Lock


class InMemoryUserStore:
    """In-memory user storage for testing and development"""
    
    def __init__(self):
        self.users = {}  # email -> user_data mapping
        self.users_by_id = {}  # user_id -> user_data mapping
        self.lock = Lock()
    
    def check_duplicate(self, email: str) -> bool:
        """
        Check if email already exists
        
        Args:
            email: Email address to check
        
        Returns:
            bool: True if email exists, False otherwise
        """
        with self.lock:
            return email.lower() in self.users
    
    def save_user(self, user_data: Dict) -> bool:
        """
        Save user to storage
        
        Args:
            user_data: User data dictionary
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.lock:
                email = user_data['email'].lower()
                user_id = user_data['user_id']
                
                self.users[email] = user_data
                self.users_by_id[user_id] = user_data
                
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email address
        
        Args:
            email: Email address
        
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        with self.lock:
            return self.users.get(email.lower())
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get user by user ID
        
        Args:
            user_id: User ID
        
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        with self.lock:
            return self.users_by_id.get(user_id)
    
    def get_all_users(self) -> List[Dict]:
        """
        Get all users
        
        Returns:
            List[Dict]: List of all user data
        """
        with self.lock:
            return list(self.users.values())
    
    def delete_user(self, email: str) -> bool:
        """
        Delete user by email
        
        Args:
            email: Email address
        
        Returns:
            bool: True if deleted, False if not found
        """
        with self.lock:
            email = email.lower()
            user_data = self.users.get(email)
            
            if user_data:
                user_id = user_data['user_id']
                del self.users[email]
                del self.users_by_id[user_id]
                return True
            
            return False
    
    def clear_all(self):
        """Clear all users from storage"""
        with self.lock:
            self.users.clear()
            self.users_by_id.clear()
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        with self.lock:
            return len(self.users)


class FileBasedUserStore:
    """File-based user storage for persistence"""
    
    def __init__(self, file_path: str = "users.json"):
        """
        Initialize file-based storage
        
        Args:
            file_path: Path to JSON file for storage
        """
        self.file_path = file_path
        self.lock = Lock()
        self._initialize_file()
    
    def _initialize_file(self):
        """Initialize storage file if it doesn't exist"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({'users': {}, 'users_by_id': {}}, f)
    
    def _load_data(self) -> Dict:
        """Load data from file"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            return {'users': {}, 'users_by_id': {}}
    
    def _save_data(self, data: Dict) -> bool:
        """Save data to file"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def check_duplicate(self, email: str) -> bool:
        """
        Check if email already exists
        
        Args:
            email: Email address to check
        
        Returns:
            bool: True if email exists, False otherwise
        """
        with self.lock:
            data = self._load_data()
            return email.lower() in data.get('users', {})
    
    def save_user(self, user_data: Dict) -> bool:
        """
        Save user to storage
        
        Args:
            user_data: User data dictionary
        
        Returns:
            bool: True if successful, False otherwise
        """
        with self.lock:
            data = self._load_data()
            
            email = user_data['email'].lower()
            user_id = user_data['user_id']
            
            data['users'][email] = user_data
            data['users_by_id'][user_id] = user_data
            
            return self._save_data(data)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email address
        
        Args:
            email: Email address
        
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        with self.lock:
            data = self._load_data()
            return data.get('users', {}).get(email.lower())
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get user by user ID
        
        Args:
            user_id: User ID
        
        Returns:
            Optional[Dict]: User data if found, None otherwise
        """
        with self.lock:
            data = self._load_data()
            return data.get('users_by_id', {}).get(user_id)
    
    def get_all_users(self) -> List[Dict]:
        """
        Get all users
        
        Returns:
            List[Dict]: List of all user data
        """
        with self.lock:
            data = self._load_data()
            return list(data.get('users', {}).values())
    
    def delete_user(self, email: str) -> bool:
        """
        Delete user by email
        
        Args:
            email: Email address
        
        Returns:
            bool: True if deleted, False if not found
        """
        with self.lock:
            data = self._load_data()
            email = email.lower()
            
            user_data = data.get('users', {}).get(email)
            
            if user_data:
                user_id = user_data['user_id']
                del data['users'][email]
                del data['users_by_id'][user_id]
                return self._save_data(data)
            
            return False
    
    def clear_all(self):
        """Clear all users from storage"""
        with self.lock:
            self._save_data({'users': {}, 'users_by_id': {}})
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        with self.lock:
            data = self._load_data()
            return len(data.get('users', {}))
