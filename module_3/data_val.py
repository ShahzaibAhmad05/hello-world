
# EXERCISE 2: zero shot
# Create a function to validate phone numbers
# Support: US format (XXX) XXX-XXXX or XXX-XXX-XXXX
import re
def validate_phone_number(phone):
    """Validate US phone number format."""
    pattern = r'^(\(\d{3}\) \d{3}-\d{4}|\d{3}-\d{3}-\d{4})$'
    return re.match(pattern, phone) is not None


# FEW SHOT EXERCISE
# Create validators following these patterns:

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, email

def validate_zip_code(zip_code):
    """Validate US zip code (5 digits or 5+4 format)."""
    pattern = r'^\d{5}(-\d{4})?$'
    if not re.match(pattern, zip_code):
        return False, "Invalid zip code format"
    return True, zip_code

# Now create validator for phone numbers: (XXX) XXX-XXXX or XXX-XXX-XXXX
def validate_phone_number(phone):
    """Validate US phone number format."""
    pattern = r'^(\(\d{3}\) \d{3}-\d{4}|\d{3}-\d{3}-\d{4})$'
    if not re.match(pattern, phone):
        return False, "Invalid phone number format"
    return True, phone
