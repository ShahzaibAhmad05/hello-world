def is_valid_password(password):
    """Check if password meets requirements."""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True

# Use Copilot to generate comprehensive tests
def test_is_valid_password():
    assert is_valid_password("Password1") == True
    assert is_valid_password("pass") == False
    assert is_valid_password("password") == False
    assert is_valid_password("PASSWORD") == False
    assert is_valid_password("Passw1") == False
    assert is_valid_password("Passw@rd1") == True
    assert is_valid_password("12345678") == False
