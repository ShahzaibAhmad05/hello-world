# Prompt: "Function to validate email format and check if exists in database using SQLAlchemy"
# Copilot will suggest:
# - regex pattern matching for email validation
# - SQLAlchemy query to check database
# - proper error handling
import re
from models import User # type: ignore

def validate_and_check_email(email):
    """Validate email format and check if exists in database."""
    # Regex pattern for validating an email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Validate email format
    if not re.match(email_pattern, email):
        return False, "Invalid email format."
    
    # Check if email exists in the database
    user = User.query.filter_by(email=email).first()
    if user:
        return True, "Email exists in the database."
    else:
        return False, "Email does not exist in the database."
