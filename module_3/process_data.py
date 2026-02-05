
def process_data(data):
    """
    Process a list of data items and return doubled values for active items.
    
    Args:
        data (list): A list of dictionaries, each containing 'status' and 'value' keys.
    
    Returns:
        list: A list of integers representing doubled values of items with 'status' == 'active'.
    
    Example:
        >>> data = [
        ...     {'status': 'active', 'value': 5},
        ...     {'status': 'inactive', 'value': 10},
        ...     {'status': 'active', 'value': 3}
        ... ]
        >>> process_data(data)
        [10, 6]
    """
    result = []
    for item in data:
        try:
            if item.get('status') == 'active':
                result.append(item['value'] * 2)
        except (KeyError, TypeError):
            continue
    return result
