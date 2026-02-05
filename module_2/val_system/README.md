# User Registration System

A comprehensive user registration system with email validation, password requirements, duplicate email checking, and JWT token generation.

## Features

- **Email Validation**: RFC 5322 compliant email validation with common error checking
- **Password Requirements**: 
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character
- **Duplicate Email Checking**: Case-insensitive email duplicate detection
- **JWT Token Generation**: Secure token generation with configurable expiry
- **User Storage**: Both in-memory and file-based storage options
- **User Authentication**: Password hashing with salt and authentication support

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Registration Example

```python
from user_registration import UserRegistrationSystem
from user_storage import InMemoryUserStore

# Create storage and registration system
store = InMemoryUserStore()
system = UserRegistrationSystem(store)

# Register a new user
success, message, jwt_token = system.register_user(
    email="user@example.com",
    password="SecurePass123!",
    username="myusername"  # Optional
)

if success:
    print(f"Registration successful! Token: {jwt_token}")
else:
    print(f"Registration failed: {message}")
```

### Authentication Example

```python
# Authenticate existing user
success, message, jwt_token = system.authenticate_user(
    email="user@example.com",
    password="SecurePass123!"
)

if success:
    print(f"Authentication successful! Token: {jwt_token}")
    
    # Verify the token
    is_valid, payload = system.verify_jwt_token(jwt_token)
    if is_valid:
        print(f"User ID: {payload['user_id']}")
        print(f"Email: {payload['email']}")
else:
    print(f"Authentication failed: {message}")
```

### Using File-Based Storage

```python
from user_storage import FileBasedUserStore

# Use file-based storage for persistence
store = FileBasedUserStore("users.json")
system = UserRegistrationSystem(store)

# Users will be persisted to the file
success, message, token = system.register_user(
    "user@example.com",
    "SecurePass123!"
)
```

### Custom JWT Secret

```python
# Provide your own JWT secret key
system = UserRegistrationSystem(
    store,
    jwt_secret="your-super-secret-key-here"
)
```

## Running Tests

Run the comprehensive unit test suite:

```bash
# Run all tests
python test_user_registration.py

# Or using pytest
pytest test_user_registration.py -v

# With coverage report
pytest test_user_registration.py --cov=. --cov-report=html
```

## API Reference

### EmailValidator

- `validate(email: str) -> Tuple[bool, str]`: Validates email format

### PasswordValidator

- `validate(password: str) -> Tuple[bool, str]`: Validates password requirements

### UserRegistrationSystem

- `register_user(email, password, username=None) -> Tuple[bool, str, Optional[str]]`: Register new user
- `authenticate_user(email, password) -> Tuple[bool, str, Optional[str]]`: Authenticate existing user
- `generate_jwt_token(user_id, email, expiry_hours=24) -> str`: Generate JWT token
- `verify_jwt_token(token) -> Tuple[bool, Optional[Dict]]`: Verify and decode JWT token

### InMemoryUserStore / FileBasedUserStore

- `check_duplicate(email) -> bool`: Check if email exists
- `save_user(user_data) -> bool`: Save user data
- `get_user_by_email(email) -> Optional[Dict]`: Retrieve user by email
- `get_user_by_id(user_id) -> Optional[Dict]`: Retrieve user by ID
- `delete_user(email) -> bool`: Delete user
- `get_user_count() -> int`: Get total number of users
- `clear_all()`: Clear all users

## Security Notes

- Passwords are hashed using SHA-256 with unique salts
- JWT tokens have configurable expiry times
- Email addresses are normalized to lowercase for consistency
- User data includes creation timestamps and active status flags

## License

This is a learning project for educational purposes.
