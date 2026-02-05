# Authentication System

A complete user authentication system with password hashing, rate limiting, and brute force protection.

## Features

✅ **User Model** - SQLAlchemy-based User model with all necessary fields  
✅ **Password Hashing** - Bcrypt with 12 salt rounds for secure password storage  
✅ **Login/Registration** - Complete authentication flow with validation  
✅ **Rate Limiting** - Prevents brute force attacks (5 attempts, 15-minute lockout)  
✅ **Failed Attempt Tracking** - Monitors and resets login attempts  
✅ **Input Validation** - Username/password length requirements  

## Components

### 1. [models.py](models.py)
**User Model with SQLAlchemy and bcrypt**
- Fields: id, username, email, password_hash, created_at, is_active
- Password hashing with `set_password()` and `check_password()`
- Failed login attempt tracking
- Bcrypt salt rounds: 12 (good balance of security/performance)

### 2. [auth.py](auth.py)
**Authentication Logic with Rate Limiting**
- `login()` - Verify credentials with rate limiting protection
- `register_user()` - Create new user accounts with validation
- `logout()` - Clean up user sessions
- `RateLimiter` class - Prevents brute force attacks

### 3. [database.py](database.py)
**Database Configuration**
- SQLAlchemy engine and session management
- Connection pooling
- Table creation/management

### 4. [example_usage.py](example_usage.py)
**Demonstration Script**
- Shows registration, login, and rate limiting in action
- Example code for integration

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from database import db
from auth import login, register_user

# Initialize database
db.create_tables()
session = db.get_session()

# Register a user
success, message, user = register_user(
    session, 
    username="alice",
    email="alice@example.com", 
    password="SecurePass123!"
)

# Login
success, message, user = login(session, "alice", "SecurePass123!")
if success:
    print(f"Welcome, {user.username}!")
```

## Security Features

### Password Hashing
- **Algorithm**: bcrypt
- **Salt rounds**: 12
- **One-way hashing**: Passwords cannot be decrypted

### Rate Limiting
- **Max attempts**: 5 failed logins
- **Lockout duration**: 15 minutes
- **Username enumeration protection**: Same error message for invalid username/password
- **Brute force delay**: 0.5s delay on failed attempts

### Input Validation
- Username: minimum 3 characters
- Password: minimum 8 characters
- Email: unique constraint
- Username: unique constraint

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    last_failed_login DATETIME
);
```

## Run the Demo

```bash
python example_usage.py
```

## API Reference

### User Model

```python
user = User(username, email, password)
user.set_password(password)          # Hash and store password
user.check_password(password)        # Verify password → bool
user.increment_failed_attempts()     # Track failed logins
user.reset_failed_attempts()         # Clear failed logins
```

### Authentication Functions

```python
# Returns: (success: bool, message: str, user: User|None)
login(db_session, username, password)
register_user(db_session, username, email, password)
logout(user)  # Returns: (success: bool, message: str)
```

### Rate Limiter

```python
rate_limiter.is_locked_out(username)      # → (bool, seconds_remaining)
rate_limiter.record_failed_attempt(username)
rate_limiter.reset_attempts(username)
```

## Configuration

Customize in [auth.py](auth.py):
```python
rate_limiter = RateLimiter(
    max_attempts=5,                    # Failed login threshold
    lockout_duration_minutes=15        # Lockout period
)
```

Customize in [models.py](models.py):
```python
salt = bcrypt.gensalt(rounds=12)      # Increase for more security
```

## Production Considerations

1. **Database**: Switch from SQLite to PostgreSQL/MySQL
2. **Session Management**: Add JWT tokens or session cookies
3. **Email Verification**: Add email confirmation workflow
4. **Password Reset**: Implement secure password reset flow
5. **2FA**: Add two-factor authentication
6. **Logging**: Add audit logs for security events
7. **HTTPS**: Always use HTTPS in production
8. **Environment Variables**: Store secrets in env vars

## License

MIT
