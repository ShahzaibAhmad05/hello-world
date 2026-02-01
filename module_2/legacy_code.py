# Legacy code I will improve with copilot

def calc(a, b, c):
    if c == 1:
        return a + b
    elif c == 2:
        return a - b
    elif c == 3:
        return a * b
    elif c == 4:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

def proc_data(d):
    """
    Process a list of numbers and return the squares of all even numbers.
    
    Args:
        d (list): A list of integers to process.
    
    Returns:
        list: A list containing the squares of all even numbers from the input list,
              in the order they appear.
    
    Example:
        >>> proc_data([1, 2, 3, 4, 5, 6])
        [4, 16, 36]
    """
    r = []
    for i in d:
        if i % 2 == 0:
            r.append(i * i)
    return r

def get_usr(id, db):
    """
    Retrieve a user record from the database by user ID.
    
    Args:
        id: The user ID to query. Will be converted to string and interpolated into the SQL query.
        db: The database connection object.
    
    Returns:
        The result of executing the SQL SELECT query against the database.
    
    Note:
        This function is vulnerable to SQL injection attacks due to string concatenation.
        Consider using parameterized queries instead.
    """
    q = "SELECT * FROM users WHERE id = " + str(id)
    return db.execute(q)
