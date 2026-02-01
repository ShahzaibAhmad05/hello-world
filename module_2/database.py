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
