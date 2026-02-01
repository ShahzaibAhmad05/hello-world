"""
Comprehensive Data Validator Module

Provides validation for common data types including emails, phone numbers, URLs,
and support for custom validation rules.
"""

import re
import logging
from typing import Callable, Any, Optional, Dict, List
from urllib.parse import urlparse

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if no handlers exist
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DataValidator:
    """
    A comprehensive data validator supporting multiple validation types
    and custom validation rules.
    """
    
    # Regex patterns for common validations
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Support multiple phone formats: (123) 456-7890, 123-456-7890, 1234567890, +1-123-456-7890
    PHONE_PATTERNS = [
        r'^\+?1?\s*\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',  # US/Canada
        r'^\+?([0-9]{1,3})\s*\(?([0-9]{2,4})\)?[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})$',  # International
    ]
    
    def __init__(self):
        """Initialize the validator with an empty custom rules dictionary."""
        self.custom_rules: Dict[str, Callable[[Any], bool]] = {}
        logger.info("DataValidator instance initialized")
    
    def validate_email(self, email: str, raise_exception: bool = True) -> bool:
        """
        Validate an email address.
        
        Args:
            email: The email address to validate.
            raise_exception: If True, raises ValidationError on invalid input.
                           If False, returns False on invalid input.
        
        Returns:
            True if the email is valid, False otherwise (when raise_exception=False).
        
        Raises:
            ValidationError: If the email is invalid and raise_exception=True.
            TypeError: If email is not a string.
        """
        logger.debug(f"Validating email: {email!r}")
        
        if not isinstance(email, str):
            error_msg = f"Email must be a string, got {type(email).__name__}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        email = email.strip().lower()
        
        if not email:
            error_msg = "Email cannot be empty or whitespace only"
            logger.warning(error_msg)
            if raise_exception:
                raise ValidationError(error_msg)
            return False
        
        if len(email) > 254:  # RFC 5321
            error_msg = f"Email address is too long ({len(email)} characters, max 254 allowed): {email}"
            logger.warning(error_msg)
            if raise_exception:
                raise ValidationError(error_msg)
            return False
        
        if not re.match(self.EMAIL_PATTERN, email):
            error_msg = f"Invalid email format: '{email}'. Email must match pattern: user@domain.com"
            logger.warning(error_msg)
            if raise_exception:
                raise ValidationError(error_msg)
            return False
        
        logger.info(f"Email validation successful: {email}")
        return True
    
    def validate_phone(self, phone: str, raise_exception: bool = True) -> bool:
        """
        Validate a phone number.
        
        Supports multiple formats:
        - (123) 456-7890
        - 123-456-7890
        - 1234567890
        - +1-123-456-7890
        - International formats
        
        Args:
            phone: The phone number to validate.
            raise_exception: If True, raises ValidationError on invalid input.
                           If False, returns False on invalid input.
        
        Returns:
            True if the phone number is valid, False otherwise.
        
        Raises:
            ValidationError: If the phone number is invalid and raise_exception=True.
            TypeError: If phone is not a string.
        """
        logger.debug(f"Validating phone number: {phone!r}")
        
        if not isinstance(phone, str):
            error_msg = f"Phone number must be a string, got {type(phone).__name__}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        phone = phone.strip()
        
        if not phone:
            error_msg = "Phone number cannot be empty or whitespace only"
            logger.warning(error_msg)
            if raise_exception:
                raise ValidationError(error_msg)
            return False
        
        # Try matching against all phone patterns
        for idx, pattern in enumerate(self.PHONE_PATTERNS):
            if re.match(pattern, phone):
                logger.info(f"Phone validation successful (pattern {idx+1}): {phone}")
                return True
        
        error_msg = (f"Invalid phone number format: '{phone}'. "
                    f"Supported formats: (123) 456-7890, 123-456-7890, 1234567890, +1-123-456-7890")
        logger.warning(error_msg)
        if raise_exception:
            raise ValidationError(error_msg)
        return False
    
    def validate_url(self, url: str, require_scheme: bool = True, 
                    allowed_schemes: Optional[List[str]] = None,
                    raise_exception: bool = True) -> bool:
        """
        Validate a URL.
        
        Args:
            url: The URL to validate.
            require_scheme: If True, URL must have a scheme (http://, https://, etc.).
            allowed_schemes: List of allowed schemes. If None, allows common schemes.
            raise_exception: If True, raises ValidationError on invalid input.
        
        Returns:
            True if the URL is valid, False otherwise.
        
        Raises:
            ValidationError: If the URL is invalid and raise_exception=True.
            TypeError: If url is not a string.
        """
        logger.debug(f"Validating URL: {url!r} (require_scheme={require_scheme}, allowed_schemes={allowed_schemes})")
        
        if not isinstance(url, str):
            error_msg = f"URL must be a string, got {type(url).__name__}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        url = url.strip()
        
        if not url:
            error_msg = "URL cannot be empty or whitespace only"
            logger.warning(error_msg)
            if raise_exception:
                raise ValidationError(error_msg)
            return False
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https', 'ftp', 'ftps']
        
        try:
            parsed = urlparse(url)
            logger.debug(f"Parsed URL - scheme: {parsed.scheme!r}, netloc: {parsed.netloc!r}, path: {parsed.path!r}")
            
            # Check if scheme exists
            if require_scheme and not parsed.scheme:
                error_msg = f"URL must include a scheme (e.g., http://, https://): '{url}'"
                logger.warning(error_msg)
                if raise_exception:
                    raise ValidationError(error_msg)
                return False
            
            # Check if scheme is allowed
            if parsed.scheme and parsed.scheme not in allowed_schemes:
                error_msg = (f"URL scheme '{parsed.scheme}' is not allowed. "
                           f"Allowed schemes: {', '.join(allowed_schemes)}")
                logger.warning(error_msg)
                if raise_exception:
                    raise ValidationError(error_msg)
                return False
            
            # Check if netloc (domain) exists
            if require_scheme and not parsed.netloc:
                error_msg = f"URL must include a domain: '{url}'"
                logger.warning(error_msg)
                if raise_exception:
                    raise ValidationError(error_msg)
                return False
            
            # Basic domain validation
            if parsed.netloc:
                domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
                # Extract domain without port
                domain = parsed.netloc.split(':')[0]
                if not re.match(domain_pattern, domain):
                    error_msg = f"Invalid domain in URL: '{domain}'. Domain must contain valid characters and structure."
                    logger.warning(error_msg)
                    if raise_exception:
                        raise ValidationError(error_msg)
                    return False
            
            logger.info(f"URL validation successful: {url}")
            return True
            
        except Exception as e:
            error_msg = f"Invalid URL: '{url}'. Error details: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            if raise_exception:
                raise ValidationError(error_msg)
            return False
    
    def add_custom_rule(self, rule_name: str, validator_func: Callable[[Any], bool]) -> None:
        """
        Add a custom validation rule.
        
        Args:
            rule_name: A unique name for the custom rule.
            validator_func: A callable that takes a value and returns True if valid.
                          Should raise ValidationError with a descriptive message if invalid.
        
        Example:
            def validate_age(value):
                if not isinstance(value, int):
                    raise ValidationError("Age must be an integer")
                if value < 0 or value > 150:
                    raise ValidationError("Age must be between 0 and 150")
                return True
            
            validator = DataValidator()
            validator.add_custom_rule("age", validate_age)
            validator.validate_custom("age", 25)
        """
        logger.debug(f"Adding custom rule: {rule_name!r}")
        
        if not callable(validator_func):
            error_msg = f"validator_func must be callable, got {type(validator_func).__name__}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        if rule_name in self.custom_rules:
            logger.warning(f"Overwriting existing custom rule: {rule_name!r}")
        
        self.custom_rules[rule_name] = validator_func
        logger.info(f"Custom rule '{rule_name}' added successfully. Total custom rules: {len(self.custom_rules)}")
    
    def validate_custom(self, rule_name: str, value: Any, raise_exception: bool = True) -> bool:
        """
        Validate a value using a custom rule.
        
        Args:
            rule_name: The name of the custom rule to use.
            value: The value to validate.
            raise_exception: If True, raises ValidationError on invalid input.
        
        Returns:
            True if the value is valid, False otherwise.
        
        Raises:
            ValidationError: If validation fails and raise_exception=True.
            KeyError: If the rule_name doesn't exist.
        """
        logger.debug(f"Validating with custom rule '{rule_name}': {value!r}")
        
        if rule_name not in self.custom_rules:
            available_rules = ', '.join(self.custom_rules.keys()) if self.custom_rules else 'none'
            error_msg = f"Custom rule '{rule_name}' not found. Available rules: {available_rules}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        try:
            result = self.custom_rules[rule_name](value)
            logger.info(f"Custom rule '{rule_name}' validation successful for value: {value!r}")
            return result
        except ValidationError as e:
            logger.warning(f"Custom rule '{rule_name}' validation failed: {str(e)}")
            if raise_exception:
                raise
            return False
        except Exception as e:
            error_msg = f"Custom validation error for rule '{rule_name}': {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            if raise_exception:
                raise ValidationError(error_msg)
            return False
    
    def validate_multiple(self, data: Dict[str, Any], rules: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Validate multiple fields at once.
        
        Args:
            data: Dictionary of field names to values.
            rules: Dictionary of field names to validation types 
                  ('email', 'phone', 'url', or custom rule name).
        
        Returns:
            Dictionary of field names to error messages. Empty dict if all valid.
        
        Example:
            validator = DataValidator()
            data = {
                'email': 'user@example.com',
                'phone': '123-456-7890',
                'website': 'https://example.com'
            }
            rules = {
                'email': 'email',
                'phone': 'phone',
                'website': 'url'
            }
            errors = validator.validate_multiple(data, rules)
        """
        logger.info(f"Validating multiple fields: {list(rules.keys())}")
        errors = {}
        
        for field, rule_type in rules.items():
            logger.debug(f"Validating field '{field}' with rule '{rule_type}'")
            
            if field not in data:
                error_msg = f"Field '{field}' is missing from data"
                logger.warning(error_msg)
                errors[field] = "Field is missing"
                continue
            
            value = data[field]
            
            try:
                if rule_type == 'email':
                    self.validate_email(value, raise_exception=True)
                elif rule_type == 'phone':
                    self.validate_phone(value, raise_exception=True)
                elif rule_type == 'url':
                    self.validate_url(value, raise_exception=True)
                else:
                    # Try custom rule
                    self.validate_custom(rule_type, value, raise_exception=True)
            except (ValidationError, TypeError, KeyError) as e:
                logger.warning(f"Validation failed for field '{field}': {str(e)}")
                errors[field] = str(e)
        
        if errors:
            logger.warning(f"Multiple field validation completed with {len(errors)} error(s)")
        else:
            logger.info("Multiple field validation completed successfully - all fields valid")
        
        return errors


# Convenience functions for quick validation
def validate_email(email: str) -> bool:
    """Quick email validation. Returns True if valid, False otherwise."""
    validator = DataValidator()
    return validator.validate_email(email, raise_exception=False)


def validate_phone(phone: str) -> bool:
    """Quick phone validation. Returns True if valid, False otherwise."""
    validator = DataValidator()
    return validator.validate_phone(phone, raise_exception=False)


def validate_url(url: str) -> bool:
    """Quick URL validation. Returns True if valid, False otherwise."""
    validator = DataValidator()
    return validator.validate_url(url, raise_exception=False)


# Example usage
if __name__ == "__main__":
    # Set logging level for demo
    logger.setLevel(logging.INFO)
    
    # Create validator instance
    validator = DataValidator()
    
    # Test email validation
    print("=== Email Validation ===")
    test_emails = [
        "user@example.com",
        "invalid.email",
        "test+tag@domain.co.uk",
        ""
    ]
    for email in test_emails:
        is_valid = validator.validate_email(email, raise_exception=False)
        print(f"{email:<30} -> {'Valid' if is_valid else 'Invalid'}")
    
    # Test phone validation
    print("\n=== Phone Validation ===")
    test_phones = [
        "(123) 456-7890",
        "123-456-7890",
        "1234567890",
        "+1-123-456-7890",
        "invalid"
    ]
    for phone in test_phones:
        is_valid = validator.validate_phone(phone, raise_exception=False)
        print(f"{phone:<30} -> {'Valid' if is_valid else 'Invalid'}")
    
    # Test URL validation
    print("\n=== URL Validation ===")
    test_urls = [
        "https://www.example.com",
        "http://example.com/path?query=value",
        "ftp://files.example.com",
        "example.com",
        "invalid url with spaces"
    ]
    for url in test_urls:
        is_valid = validator.validate_url(url, raise_exception=False)
        print(f"{url:<40} -> {'Valid' if is_valid else 'Invalid'}")
    
    # Test custom rule
    print("\n=== Custom Rule Validation ===")
    def validate_age(value):
        if not isinstance(value, int):
            raise ValidationError("Age must be an integer")
        if value < 0 or value > 150:
            raise ValidationError("Age must be between 0 and 150")
        return True
    
    validator.add_custom_rule("age", validate_age)
    
    test_ages = [25, 150, -5, 200, "not a number"]
    for age in test_ages:
        try:
            is_valid = validator.validate_custom("age", age, raise_exception=True)
            print(f"{age:<30} -> Valid")
        except (ValidationError, TypeError) as e:
            print(f"{age:<30} -> Invalid: {e}")
    
    # Test multiple validations
    print("\n=== Multiple Field Validation ===")
    user_data = {
        'email': 'user@example.com',
        'phone': '123-456-7890',
        'website': 'https://example.com',
        'age': 30
    }
    
    validation_rules = {
        'email': 'email',
        'phone': 'phone',
        'website': 'url',
        'age': 'age'
    }
    
    errors = validator.validate_multiple(user_data, validation_rules)
    if errors:
        print("Validation errors found:")
        for field, error in errors.items():
            print(f"  {field}: {error}")
    else:
        print("All fields are valid!")
