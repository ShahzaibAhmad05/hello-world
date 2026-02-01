# EXERCISE 1
# Complete these classes and methods

def fibonacci(n):
    """Return the nth Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    

class Stack:
    """A simple stack implementation."""
    
    def __init__(self):
        self.items = []
    
    def push(self, item):
        """Push an item onto the stack."""
        self.items.append(item)
    
    def pop(self):
        """Pop an item off the stack. Raises IndexError if the stack is empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self.items.pop()
    
    def peek(self):
        """Return the top item of the stack without removing it. Raises IndexError if the stack is empty."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self.items[-1]
    
    def is_empty(self):
        """Return True if the stack is empty, False otherwise."""
        return len(self.items) == 0
    
    def size(self):
        """Return the number of items in the stack."""
        return len(self.items)
    

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even_squares = [x**2 for x in numbers if x % 2 == 0]


# EXERCISE 2
# Function to check if a string is a valid password
# Requirements: 8+ chars, 1 uppercase, 1 lowercase, 1 number
def is_valid_password(password):
    """Check if the given password is valid based on defined criteria."""
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit


# EXERCISE 3
def decorator_with_args(prefix):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"{prefix}: Calling {func.__name__}")
            result = func(*args, **kwargs)
            print(f"{prefix}: Done")
            return result
        return wrapper
    return decorator

@decorator_with_args("LOG")
def greet(name):
    return f"Hello, {name}!"


# EXERCISE 4
def calculate_discount(price, discount_percent):
    discount_amount = price * (discount_percent / 100)  # Convert percentage to decimal
    final_price = price - discount_amount
    return final_price

# Test:
print(calculate_discount(100, 20))  # Should return 80, but returns?


# EXERCISE 5
def process(data):
    return [d['name'] for d in data if d['status'] == 'active' and d['age'] >= 18 and d['verified']]
