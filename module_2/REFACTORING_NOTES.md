### Code Explanation: calc()

The calc() function performs basic arithmetic operations based on the parameter c:

- c = 1: Returns the sum of a and b
- c = 2: Returns the difference of a minus b
- c = 3: Returns the product of a and b
- c = 4: Returns the quotient of a divided by b

**IMPROVEMENT:** The function uses conditional logic to determine which operation to execute. However, this code could be improved by using a dictionary to map operation codes to functions, which would be more maintainable and scalable.


### Code Explaination: proc_data()

Process a list of numbers and return the squares of all even numbers.

Args:
    d (list): A list of integers to process.

Returns:
    list: A list containing the squares of all even numbers from the input list,
            in the order they appear.

Example:
    >>> proc_data([1, 2, 3, 4, 5, 6])
    [4, 16, 36]


### Code Explaination: get_usr()

Retrieve a user record from the database by user ID.

Args:
    id: The user ID to query. Will be converted to string and interpolated into the SQL query.

Returns:
    The result of executing the SQL SELECT query against the database.

Raises:
    NameError: If 'db' is not defined in the current scope.

Note:
    This function is vulnerable to SQL injection attacks due to string concatenation.
    Consider using parameterized queries instead.


