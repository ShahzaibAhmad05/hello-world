"""
Example usage of the User Registration System
Demonstrates registration, authentication, and JWT token verification
"""

from user_registration import UserRegistrationSystem
from user_storage import InMemoryUserStore, FileBasedUserStore


def example_basic_registration():
    """Basic registration example"""
    print("\n=== Basic Registration Example ===")
    
    # Create in-memory storage and registration system
    store = InMemoryUserStore()
    system = UserRegistrationSystem(store)
    
    # Register a new user
    success, message, jwt_token = system.register_user(
        email="alice@example.com",
        password="SecurePass123!",
        username="alice"
    )
    
    print(f"Registration: {message}")
    if success:
        print(f"JWT Token: {jwt_token[:50]}...")
        
        # Verify the token
        is_valid, payload = system.verify_jwt_token(jwt_token)
        if is_valid:
            print(f"Token verified! User ID: {payload['user_id']}")


def example_validation_errors():
    """Demonstrate validation errors"""
    print("\n=== Validation Error Examples ===")
    
    store = InMemoryUserStore()
    system = UserRegistrationSystem(store)
    
    # Invalid email
    success, message, _ = system.register_user("invalid-email", "SecurePass123!")
    print(f"Invalid email: {message}")
    
    # Weak password (no special character)
    success, message, _ = system.register_user("user@example.com", "Password123")
    print(f"Weak password: {message}")
    
    # Password too short
    success, message, _ = system.register_user("user@example.com", "Pass1!")
    print(f"Short password: {message}")


def example_duplicate_detection():
    """Demonstrate duplicate email detection"""
    print("\n=== Duplicate Email Detection ===")
    
    store = InMemoryUserStore()
    system = UserRegistrationSystem(store)
    
    # Register first user
    success, message, _ = system.register_user("bob@example.com", "SecurePass123!")
    print(f"First registration: {message}")
    
    # Try to register with same email
    success, message, _ = system.register_user("bob@example.com", "AnotherPass456!")
    print(f"Duplicate attempt: {message}")
    
    # Try with different case
    success, message, _ = system.register_user("BOB@EXAMPLE.COM", "YetAnother789!")
    print(f"Case variation: {message}")


def example_authentication():
    """Demonstrate user authentication"""
    print("\n=== Authentication Example ===")
    
    store = InMemoryUserStore()
    system = UserRegistrationSystem(store)
    
    # Register user
    email = "charlie@example.com"
    password = "SecurePass123!"
    
    success, message, reg_token = system.register_user(email, password)
    print(f"Registration: {message}")
    
    # Authenticate with correct password
    success, message, auth_token = system.authenticate_user(email, password)
    print(f"Correct password: {message}")
    
    # Authenticate with wrong password
    success, message, _ = system.authenticate_user(email, "WrongPass123!")
    print(f"Wrong password: {message}")
    
    # Verify both tokens work
    if reg_token and auth_token:
        is_valid1, _ = system.verify_jwt_token(reg_token)
        is_valid2, _ = system.verify_jwt_token(auth_token)
        print(f"Registration token valid: {is_valid1}")
        print(f"Authentication token valid: {is_valid2}")


def example_file_based_storage():
    """Demonstrate file-based storage"""
    print("\n=== File-Based Storage Example ===")
    
    # Use file-based storage
    store = FileBasedUserStore("demo_users.json")
    system = UserRegistrationSystem(store)
    
    # Register users
    system.register_user("user1@example.com", "SecurePass123!", username="user1")
    system.register_user("user2@example.com", "SecurePass456!", username="user2")
    
    print(f"Total users in file: {store.get_user_count()}")
    
    # Create new instance to demonstrate persistence
    new_store = FileBasedUserStore("demo_users.json")
    print(f"Users after reload: {new_store.get_user_count()}")
    
    # Get all users
    users = new_store.get_all_users()
    print("Registered users:")
    for user in users:
        print(f"  - {user['username']} ({user['email']})")
    
    # Clean up
    import os
    new_store.clear_all()
    if os.path.exists("demo_users.json"):
        os.remove("demo_users.json")


def example_custom_jwt_expiry():
    """Demonstrate custom JWT token expiry"""
    print("\n=== Custom JWT Expiry Example ===")
    
    store = InMemoryUserStore()
    system = UserRegistrationSystem(store, jwt_secret="my-custom-secret")
    
    # Generate token with 1 hour expiry
    token_1h = system.generate_jwt_token("user123", "user@example.com", expiry_hours=1)
    
    # Generate token with 7 days expiry
    token_7d = system.generate_jwt_token("user123", "user@example.com", expiry_hours=168)
    
    # Verify both tokens
    is_valid_1h, payload_1h = system.verify_jwt_token(token_1h)
    is_valid_7d, payload_7d = system.verify_jwt_token(token_7d)
    
    print(f"1-hour token valid: {is_valid_1h}")
    print(f"7-day token valid: {is_valid_7d}")
    
    if is_valid_1h:
        from datetime import datetime
        exp_time = datetime.fromtimestamp(payload_1h['exp'])
        print(f"1-hour token expires at: {exp_time}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("User Registration System - Usage Examples")
    print("=" * 60)
    
    example_basic_registration()
    example_validation_errors()
    example_duplicate_detection()
    example_authentication()
    example_file_based_storage()
    example_custom_jwt_expiry()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
