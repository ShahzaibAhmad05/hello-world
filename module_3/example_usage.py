"""
Example usage of the authentication system.
"""
from database import db
from auth import login, register_user, logout


def main():
    """Demonstrate authentication system usage."""
    
    # Initialize database
    print("Initializing database...")
    db.create_tables()
    session = db.get_session()
    
    print("\n" + "="*60)
    print("USER REGISTRATION")
    print("="*60)
    
    # Register a new user
    success, message, user = register_user(
        session,
        username="alice",
        email="alice@example.com",
        password="SecurePassword123!"
    )
    print(f"Registration: {message}")
    
    # Try to register with same username (should fail)
    success, message, user = register_user(
        session,
        username="alice",
        email="alice2@example.com",
        password="AnotherPassword!"
    )
    print(f"Duplicate username: {message}")
    
    print("\n" + "="*60)
    print("USER LOGIN")
    print("="*60)
    
    # Successful login
    success, message, user = login(session, "alice", "SecurePassword123!")
    print(f"Login attempt: {message}")
    if success:
        print(f"Logged in as: {user}")
    
    # Failed login (wrong password)
    success, message, user = login(session, "alice", "WrongPassword")
    print(f"\nWrong password: {message}")
    
    print("\n" + "="*60)
    print("RATE LIMITING DEMONSTRATION")
    print("="*60)
    
    # Demonstrate rate limiting (5 failed attempts)
    print("Attempting 6 failed logins to trigger rate limiting...")
    for i in range(6):
        success, message, user = login(session, "alice", "WrongPassword")
        print(f"Attempt {i+1}: {message}")
    
    # Try to login after being locked out
    print("\nTrying to login while locked out...")
    success, message, user = login(session, "alice", "SecurePassword123!")
    print(f"Login attempt: {message}")
    
    print("\n" + "="*60)
    print("SUCCESSFUL LOGIN AFTER LOCKOUT")
    print("="*60)
    print("(In real scenario, wait 15 minutes or reset the rate limiter)")
    
    # Reset rate limiter for demonstration
    from auth import rate_limiter
    rate_limiter.reset_attempts("alice")
    
    success, message, user = login(session, "alice", "SecurePassword123!")
    print(f"Login after reset: {message}")
    
    if success:
        # Logout
        success, message = logout(user)
        print(f"Logout: {message}")
    
    # Cleanup
    db.close_session()
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)


if __name__ == "__main__":
    main()
