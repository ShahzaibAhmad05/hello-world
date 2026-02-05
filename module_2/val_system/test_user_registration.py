"""
Unit Tests for User Registration System
Tests email validation, password requirements, duplicate checking, and JWT token generation
"""

import unittest
import os
import json
from datetime import datetime, timedelta
import jwt

from user_registration import (
    EmailValidator,
    PasswordValidator,
    UserRegistrationSystem
)
from user_storage import InMemoryUserStore, FileBasedUserStore


class TestEmailValidator(unittest.TestCase):
    """Test email validation functionality"""
    
    def setUp(self):
        self.validator = EmailValidator()
    
    def test_valid_emails(self):
        """Test valid email addresses"""
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "test123@test-domain.com",
            "admin+tag@domain.org",
            "user_name@domain.com"
        ]
        
        for email in valid_emails:
            is_valid, msg = self.validator.validate(email)
            self.assertTrue(is_valid, f"Email {email} should be valid: {msg}")
    
    def test_invalid_emails(self):
        """Test invalid email addresses"""
        invalid_emails = [
            "",  # Empty
            "notanemail",  # No @ symbol
            "@domain.com",  # No local part
            "user@",  # No domain
            "user..name@domain.com",  # Consecutive dots
            "user@domain",  # No TLD
            "user name@domain.com",  # Space in local part
        ]
        
        for email in invalid_emails:
            is_valid, msg = self.validator.validate(email)
            self.assertFalse(is_valid, f"Email '{email}' should be invalid")
    
    def test_email_too_long(self):
        """Test email that exceeds maximum length"""
        long_email = "a" * 250 + "@test.com"
        is_valid, msg = self.validator.validate(long_email)
        self.assertFalse(is_valid)
        self.assertIn("too long", msg)
    
    def test_empty_email(self):
        """Test empty email"""
        is_valid, msg = self.validator.validate("")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", msg)


class TestPasswordValidator(unittest.TestCase):
    """Test password validation functionality"""
    
    def setUp(self):
        self.validator = PasswordValidator()
    
    def test_valid_passwords(self):
        """Test valid passwords"""
        valid_passwords = [
            "Password123!",
            "SecureP@ss1",
            "MyP@ssw0rd",
            "Complex#Pass123"
        ]
        
        for password in valid_passwords:
            is_valid, msg = self.validator.validate(password)
            self.assertTrue(is_valid, f"Password should be valid: {msg}")
    
    def test_password_too_short(self):
        """Test password shorter than minimum length"""
        is_valid, msg = self.validator.validate("Pass1!")
        self.assertFalse(is_valid)
        self.assertIn("at least", msg)
    
    def test_password_no_uppercase(self):
        """Test password without uppercase letter"""
        is_valid, msg = self.validator.validate("password123!")
        self.assertFalse(is_valid)
        self.assertIn("uppercase", msg)
    
    def test_password_no_lowercase(self):
        """Test password without lowercase letter"""
        is_valid, msg = self.validator.validate("PASSWORD123!")
        self.assertFalse(is_valid)
        self.assertIn("lowercase", msg)
    
    def test_password_no_digit(self):
        """Test password without digit"""
        is_valid, msg = self.validator.validate("Password!")
        self.assertFalse(is_valid)
        self.assertIn("digit", msg)
    
    def test_password_no_special_char(self):
        """Test password without special character"""
        is_valid, msg = self.validator.validate("Password123")
        self.assertFalse(is_valid)
        self.assertIn("special character", msg)
    
    def test_empty_password(self):
        """Test empty password"""
        is_valid, msg = self.validator.validate("")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", msg)
    
    def test_password_too_long(self):
        """Test password exceeding maximum length"""
        long_password = "A1!" + "a" * 130
        is_valid, msg = self.validator.validate(long_password)
        self.assertFalse(is_valid)
        self.assertIn("must not exceed", msg)


class TestInMemoryUserStore(unittest.TestCase):
    """Test in-memory user storage"""
    
    def setUp(self):
        self.store = InMemoryUserStore()
    
    def tearDown(self):
        self.store.clear_all()
    
    def test_check_duplicate_nonexistent(self):
        """Test checking for non-existent email"""
        self.assertFalse(self.store.check_duplicate("test@example.com"))
    
    def test_save_and_check_duplicate(self):
        """Test saving user and checking for duplicate"""
        user_data = {
            'user_id': 'test123',
            'email': 'test@example.com',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        
        self.assertTrue(self.store.save_user(user_data))
        self.assertTrue(self.store.check_duplicate("test@example.com"))
        self.assertTrue(self.store.check_duplicate("TEST@EXAMPLE.COM"))  # Case insensitive
    
    def test_get_user_by_email(self):
        """Test retrieving user by email"""
        user_data = {
            'user_id': 'test123',
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        
        self.store.save_user(user_data)
        retrieved = self.store.get_user_by_email("test@example.com")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['user_id'], 'test123')
        self.assertEqual(retrieved['username'], 'testuser')
    
    def test_get_user_by_id(self):
        """Test retrieving user by ID"""
        user_data = {
            'user_id': 'test123',
            'email': 'test@example.com',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        
        self.store.save_user(user_data)
        retrieved = self.store.get_user_by_id("test123")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['email'], 'test@example.com')
    
    def test_delete_user(self):
        """Test deleting user"""
        user_data = {
            'user_id': 'test123',
            'email': 'test@example.com',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        
        self.store.save_user(user_data)
        self.assertTrue(self.store.delete_user("test@example.com"))
        self.assertFalse(self.store.check_duplicate("test@example.com"))
    
    def test_get_user_count(self):
        """Test getting user count"""
        self.assertEqual(self.store.get_user_count(), 0)
        
        user1 = {'user_id': '1', 'email': 'user1@test.com', 'password_hash': 'h', 'salt': 's'}
        user2 = {'user_id': '2', 'email': 'user2@test.com', 'password_hash': 'h', 'salt': 's'}
        
        self.store.save_user(user1)
        self.assertEqual(self.store.get_user_count(), 1)
        
        self.store.save_user(user2)
        self.assertEqual(self.store.get_user_count(), 2)


class TestUserRegistrationSystem(unittest.TestCase):
    """Test user registration system"""
    
    def setUp(self):
        self.store = InMemoryUserStore()
        self.system = UserRegistrationSystem(self.store, jwt_secret="test_secret_key")
    
    def tearDown(self):
        self.store.clear_all()
    
    def test_successful_registration(self):
        """Test successful user registration"""
        success, msg, token = self.system.register_user(
            "newuser@example.com",
            "SecurePass123!"
        )
        
        self.assertTrue(success)
        self.assertIn("successfully", msg)
        self.assertIsNotNone(token)
        
        # Verify user is stored
        self.assertTrue(self.store.check_duplicate("newuser@example.com"))
    
    def test_registration_invalid_email(self):
        """Test registration with invalid email"""
        success, msg, token = self.system.register_user(
            "invalid-email",
            "SecurePass123!"
        )
        
        self.assertFalse(success)
        self.assertIn("Email validation failed", msg)
        self.assertIsNone(token)
    
    def test_registration_weak_password(self):
        """Test registration with weak password"""
        success, msg, token = self.system.register_user(
            "user@example.com",
            "weak"
        )
        
        self.assertFalse(success)
        self.assertIn("Password validation failed", msg)
        self.assertIsNone(token)
    
    def test_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # Register first user
        self.system.register_user("user@example.com", "SecurePass123!")
        
        # Try to register with same email
        success, msg, token = self.system.register_user(
            "user@example.com",
            "AnotherPass123!"
        )
        
        self.assertFalse(success)
        self.assertIn("already registered", msg)
        self.assertIsNone(token)
    
    def test_registration_case_insensitive_email(self):
        """Test that email checking is case-insensitive"""
        self.system.register_user("User@Example.com", "SecurePass123!")
        
        success, msg, token = self.system.register_user(
            "user@example.com",
            "AnotherPass123!"
        )
        
        self.assertFalse(success)
        self.assertIn("already registered", msg)
    
    def test_jwt_token_generation(self):
        """Test JWT token generation"""
        token = self.system.generate_jwt_token("user123", "user@example.com")
        
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        
        # Verify token can be decoded
        is_valid, payload = self.system.verify_jwt_token(token)
        self.assertTrue(is_valid)
        self.assertEqual(payload['user_id'], "user123")
        self.assertEqual(payload['email'], "user@example.com")
    
    def test_jwt_token_expiry(self):
        """Test JWT token with custom expiry"""
        # Create token that expires in 0 hours (immediately)
        token = self.system.generate_jwt_token("user123", "user@example.com", expiry_hours=0)
        
        # Token should be expired
        import time
        time.sleep(1)  # Wait a second
        
        is_valid, payload = self.system.verify_jwt_token(token)
        self.assertFalse(is_valid)
        self.assertIn("error", payload)
    
    def test_password_hashing(self):
        """Test password hashing"""
        password = "MyPassword123!"
        hash1, salt1 = self.system._hash_password(password)
        hash2, salt2 = self.system._hash_password(password)
        
        # Different salts should produce different hashes
        self.assertNotEqual(hash1, hash2)
        self.assertNotEqual(salt1, salt2)
        
        # Same password and salt should produce same hash
        hash3, _ = self.system._hash_password(password, salt1)
        self.assertEqual(hash1, hash3)
    
    def test_authentication_success(self):
        """Test successful authentication"""
        email = "user@example.com"
        password = "SecurePass123!"
        
        # Register user
        self.system.register_user(email, password)
        
        # Authenticate
        success, msg, token = self.system.authenticate_user(email, password)
        
        self.assertTrue(success)
        self.assertIn("successful", msg)
        self.assertIsNotNone(token)
    
    def test_authentication_wrong_password(self):
        """Test authentication with wrong password"""
        email = "user@example.com"
        password = "SecurePass123!"
        
        # Register user
        self.system.register_user(email, password)
        
        # Try to authenticate with wrong password
        success, msg, token = self.system.authenticate_user(email, "WrongPass123!")
        
        self.assertFalse(success)
        self.assertIn("Invalid", msg)
        self.assertIsNone(token)
    
    def test_authentication_nonexistent_user(self):
        """Test authentication with non-existent user"""
        success, msg, token = self.system.authenticate_user(
            "nonexistent@example.com",
            "SecurePass123!"
        )
        
        self.assertFalse(success)
        self.assertIn("Invalid", msg)
        self.assertIsNone(token)
    
    def test_registration_with_username(self):
        """Test registration with custom username"""
        success, msg, token = self.system.register_user(
            "user@example.com",
            "SecurePass123!",
            username="customuser"
        )
        
        self.assertTrue(success)
        
        user = self.store.get_user_by_email("user@example.com")
        self.assertEqual(user['username'], "customuser")
    
    def test_registration_auto_username(self):
        """Test registration with auto-generated username from email"""
        success, msg, token = self.system.register_user(
            "testuser@example.com",
            "SecurePass123!"
        )
        
        self.assertTrue(success)
        
        user = self.store.get_user_by_email("testuser@example.com")
        self.assertEqual(user['username'], "testuser")


class TestFileBasedUserStore(unittest.TestCase):
    """Test file-based user storage"""
    
    def setUp(self):
        self.test_file = "test_users.json"
        self.store = FileBasedUserStore(self.test_file)
    
    def tearDown(self):
        self.store.clear_all()
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_file_creation(self):
        """Test that storage file is created"""
        self.assertTrue(os.path.exists(self.test_file))
    
    def test_save_and_retrieve_user(self):
        """Test saving and retrieving user from file"""
        user_data = {
            'user_id': 'test123',
            'email': 'test@example.com',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        
        self.assertTrue(self.store.save_user(user_data))
        
        # Create new store instance to test persistence
        new_store = FileBasedUserStore(self.test_file)
        retrieved = new_store.get_user_by_email("test@example.com")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['user_id'], 'test123')
    
    def test_persistence_across_instances(self):
        """Test that data persists across store instances"""
        user_data = {
            'user_id': 'test123',
            'email': 'test@example.com',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        
        self.store.save_user(user_data)
        
        # Create new instance
        new_store = FileBasedUserStore(self.test_file)
        self.assertTrue(new_store.check_duplicate("test@example.com"))
        self.assertEqual(new_store.get_user_count(), 1)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
