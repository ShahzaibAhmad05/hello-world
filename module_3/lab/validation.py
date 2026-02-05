"""Context-Rich Input Validation Implementation

Based on context-rich prompt: Comprehensive user registration validation
with client/server-side validation, security, and multi-language support.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import html


@dataclass
class ValidationError:
    field: str
    message: str
    code: str


class ValidationResult:
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.is_valid: bool = True

    def add_error(self, field: str, message: str, code: str):
        self.errors.append(ValidationError(field, message, code))
        self.is_valid = False

    def get_errors_dict(self) -> Dict[str, List[str]]:
        """Group errors by field."""
        errors_dict = {}
        for error in self.errors:
            if error.field not in errors_dict:
                errors_dict[error.field] = []
            errors_dict[error.field].append(error.message)
        return errors_dict


class UserRegistrationValidator:
    """Comprehensive user registration form validation."""

    # Translation dictionary for error messages
    MESSAGES = {
        'en': {
            'email_required': 'Email address is required',
            'email_invalid': 'Please enter a valid email address',
            'email_taken': 'This email address is already registered',
            'password_required': 'Password is required',
            'password_length': 'Password must be at least 8 characters long',
            'password_uppercase': 'Password must contain at least one uppercase letter',
            'password_lowercase': 'Password must contain at least one lowercase letter',
            'password_digit': 'Password must contain at least one digit',
            'password_special': 'Password must contain at least one special character',
            'username_required': 'Username is required',
            'username_taken': 'This username is already taken',
            'username_invalid': 'Username can only contain letters, numbers, and underscores',
            'phone_invalid': 'Please enter a valid US phone number (e.g., 555-123-4567)',
            'age_required': 'Age is required',
            'age_invalid': 'Age must be a number',
            'age_range': 'You must be between 13 and 120 years old',
        },
        'es': {
            'email_required': 'La dirección de correo electrónico es obligatoria',
            'email_invalid': 'Por favor ingrese una dirección de correo electrónico válida',
            'password_required': 'La contraseña es obligatoria',
            'password_length': 'La contraseña debe tener al menos 8 caracteres',
        }
    }

    # Simulated existing users database
    existing_emails = {'existing@example.com', 'test@test.com'}
    existing_usernames = {'existinguser', 'testuser'}

    def __init__(self, language: str = 'en'):
        self.language = language

    def get_message(self, key: str) -> str:
        """Get translated error message."""
        return self.MESSAGES.get(self.language, self.MESSAGES['en']).get(
            key, self.MESSAGES['en'].get(key, 'Validation error')
        )

    def validate_email(self, email: str, result: ValidationResult) -> None:
        """Validate email format and availability."""
        if not email:
            result.add_error('email', self.get_message('email_required'), 'EMAIL_REQUIRED')
            return

        # RFC 5322 simplified regex for email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            result.add_error('email', self.get_message('email_invalid'), 'EMAIL_INVALID')
            return

        # Check availability (real-time check simulation)
        if email.lower() in self.existing_emails:
            result.add_error('email', self.get_message('email_taken'), 'EMAIL_TAKEN')

    def validate_password(self, password: str, result: ValidationResult) -> None:
        """Validate password meets security requirements."""
        if not password:
            result.add_error('password', self.get_message('password_required'), 'PASSWORD_REQUIRED')
            return

        if len(password) < 8:
            result.add_error('password', self.get_message('password_length'), 'PASSWORD_LENGTH')

        if not re.search(r'[A-Z]', password):
            result.add_error('password', self.get_message('password_uppercase'), 'PASSWORD_UPPERCASE')

        if not re.search(r'[a-z]', password):
            result.add_error('password', self.get_message('password_lowercase'), 'PASSWORD_LOWERCASE')

        if not re.search(r'\d', password):
            result.add_error('password', self.get_message('password_digit'), 'PASSWORD_DIGIT')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result.add_error('password', self.get_message('password_special'), 'PASSWORD_SPECIAL')

    def validate_username(self, username: str, result: ValidationResult) -> None:
        """Validate username format and availability."""
        if not username:
            result.add_error('username', self.get_message('username_required'), 'USERNAME_REQUIRED')
            return

        # Username can only contain letters, numbers, underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            result.add_error('username', self.get_message('username_invalid'), 'USERNAME_INVALID')

        # Check availability
        if username.lower() in self.existing_usernames:
            result.add_error('username', self.get_message('username_taken'), 'USERNAME_TAKEN')

    def validate_phone(self, phone: str, result: ValidationResult) -> None:
        """Validate US phone number format."""
        if not phone:
            return  # Phone is optional

        # US phone format: (555) 123-4567, 555-123-4567, 5551234567
        phone_pattern = r'^(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$'
        if not re.match(phone_pattern, phone):
            result.add_error('phone', self.get_message('phone_invalid'), 'PHONE_INVALID')

    def validate_age(self, age: any, result: ValidationResult) -> None:
        """Validate age is within acceptable range."""
        if age is None or age == '':
            result.add_error('age', self.get_message('age_required'), 'AGE_REQUIRED')
            return

        try:
            age_int = int(age)
        except (ValueError, TypeError):
            result.add_error('age', self.get_message('age_invalid'), 'AGE_INVALID')
            return

        if age_int < 13 or age_int > 120:
            result.add_error('age', self.get_message('age_range'), 'AGE_RANGE')

    def sanitize_input(self, text: str) -> str:
        """Sanitize text input to prevent XSS attacks."""
        if not text:
            return text
        # HTML escape to prevent XSS
        return html.escape(text.strip())

    def validate_registration(self, form_data: Dict) -> ValidationResult:
        """
        Validate complete registration form.
        
        Args:
            form_data: Dictionary with user registration data
        
        Returns:
            ValidationResult with any errors found
        """
        result = ValidationResult()

        # Validate each field
        self.validate_email(form_data.get('email', ''), result)
        self.validate_password(form_data.get('password', ''), result)
        self.validate_username(form_data.get('username', ''), result)
        self.validate_phone(form_data.get('phone', ''), result)
        self.validate_age(form_data.get('age'), result)

        return result

    def sanitize_form(self, form_data: Dict) -> Dict:
        """Sanitize all form inputs."""
        return {
            'email': self.sanitize_input(form_data.get('email', '')),
            'username': self.sanitize_input(form_data.get('username', '')),
            'phone': self.sanitize_input(form_data.get('phone', '')),
            'age': form_data.get('age'),
            # Password is not sanitized, only validated
            'password': form_data.get('password', '')
        }


# Example usage
if __name__ == "__main__":
    validator = UserRegistrationValidator(language='en')

    # Test case 1: Invalid data
    print("Test 1: Invalid registration data")
    invalid_data = {
        'email': 'invalid-email',
        'password': 'weak',
        'username': 'test user!',
        'phone': '123',
        'age': 5
    }
    result = validator.validate_registration(invalid_data)
    if not result.is_valid:
        print("Validation errors:")
        for field, messages in result.get_errors_dict().items():
            print(f"  {field}:")
            for msg in messages:
                print(f"    - {msg}")

    # Test case 2: Valid data
    print("\nTest 2: Valid registration data")
    valid_data = {
        'email': 'newuser@example.com',
        'password': 'SecureP@ss123',
        'username': 'newuser123',
        'phone': '555-123-4567',
        'age': 25
    }
    result = validator.validate_registration(valid_data)
    if result.is_valid:
        print("✓ All validations passed!")
        sanitized = validator.sanitize_form(valid_data)
        print(f"Sanitized data: {sanitized}")
