# EXERCISE 1
# Function to add two numbers
def add(a, b):
    """
    Add two numbers and return the sum.
    
    Args:
        a: The first number to add.
        b: The second number to add.
    
    Returns:
        The sum of a and b.
    """
    return a + b

# This was my expected implementation
def add(a: int, b: int) -> int:
    """
    Add two integers and return the sum.
    
    Simple function to add two numbers with type annotations.
    
    Args:
        a (int): The first integer to add.
        b (int): The second integer to add.
    
    Returns:
        int: The sum of a and b.
    """
    return a + b


# EXERCISE 2
# sort function
def sort_numbers(numbers):
    """
    Sort a list of numbers in ascending order.
    
    Args:
        numbers: A list of numbers to sort.
    
    Returns:
        A new sorted list in ascending order.
    """
    return sorted(numbers)

# Function to sort a list of numbers
def sort_numbers(numbers: list) -> list:
    """
    Sort a list of numbers in ascending order.
    
    Function to sort a list of numbers using Python's built-in sorted() function.
    
    Args:
        numbers (list): A list of numbers to sort.
    
    Returns:
        list: A new sorted list in ascending order.
    """
    return sorted(numbers)

# Function to sort a list of numbers in ascending order
# Uses bubble sort algorithm
# Parameters: numbers (list of integers)
# Returns: sorted list
def bubble_sort(numbers: list) -> list:
    """
    Sort a list of numbers using the bubble sort algorithm.
    
    Implements the bubble sort algorithm which repeatedly steps through the list,
    compares adjacent elements, and swaps them if they are in the wrong order.
    The pass through the list is repeated until the list is sorted.
    
    Time Complexity: O(n^2) in worst and average cases
    Space Complexity: O(1) - sorts in place
    
    Args:
        numbers (list): A list of integers to sort.
    
    Returns:
        list: The sorted list in ascending order (modified in place).
    
    Example:
        >>> bubble_sort([64, 34, 25, 12, 22])
        [12, 22, 25, 34, 64]
    """
    n = len(numbers)
    # Outer loop: traverse through all elements
    for i in range(n):
        # Inner loop: compare adjacent elements
        # Last i elements are already in place after i iterations
        for j in range(0, n-i-1):
            # Swap if the element found is greater than the next element
            if numbers[j] > numbers[j+1]:
                numbers[j], numbers[j+1] = numbers[j+1], numbers[j]
    return numbers


# EXERCISE 3
import re

def validate_email(email):
    """
    Validate whether an email address has a valid format.
    
    Uses regular expression pattern matching to verify that the email address
    follows the standard email format: username@domain.extension
    
    Pattern validation rules:
    - Username: alphanumeric characters, dots, underscores, percent, plus, or hyphens
    - Domain: alphanumeric characters, dots, or hyphens
    - Extension: at least 2 alphabetic characters
    
    Args:
        email: The email address string to validate.
    
    Returns:
        bool: True if the email format is valid, False otherwise.
    
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    # Check if email format is valid using regex pattern
    # Pattern breakdown:
    # ^[a-zA-Z0-9._%+-]+ - Start with one or more valid username characters
    # @ - Literal @ symbol
    # [a-zA-Z0-9.-]+ - Domain name with valid characters
    # \. - Literal dot before extension
    # [a-zA-Z]{2,}$ - Extension with at least 2 letters at the end
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # YES, IT WILL USE THE RE IMPORT ABOVE
    if re.match(pattern, email):
        return True
    return False
