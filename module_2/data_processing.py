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
