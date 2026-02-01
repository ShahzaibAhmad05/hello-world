- Use parameterized Queries
- Type Checking
- Range and Format Validation
- Using Pydantic for complex validation

### Examples

def get_usr(id, db):
    """
    Retrieve a user record from the database by user ID.
    
    Args:
        id: The user ID to query.
        db: The database connection object.
    
    Returns:
        The result of executing the SQL SELECT query against the database.
    """
    q = "SELECT * FROM users WHERE id = ?"
    return db.execute(q, (id,))


def process_data(user_id: int, email: str) -> None:
    if not isinstance(user_id, int):
        raise TypeError("user_id must be an integer")
    if not isinstance(email, str):
        raise TypeError("email must be a string")


def validate_age(age: int) -> bool:
    if not 0 <= age <= 150:
        raise ValueError("Age must be between 0 and 150")
    return True

import re
def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return True


from pydantic import BaseModel, EmailStr, field_validator

class User(BaseModel):
    id: int
    email: EmailStr
    age: int
    
    @field_validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v


import html

def sanitize_input(user_input: str) -> str:
    return html.escape(user_input.strip())

