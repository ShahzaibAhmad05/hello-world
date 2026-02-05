def find_max(numbers):
    """Find maximum number in list."""
    # Generate edge case tests with Copilot
    if not numbers:
        return None
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

def test_find_max():
    assert find_max([1, 2, 3, 4, 5]) == 5
    assert find_max([-1, -2, -3, -4, -5]) == -1
    assert find_max([0, 0, 0, 0]) == 0
    assert find_max([5]) == 5
    assert find_max([]) is None
    assert find_max([3, 1, 4, 1, 5, 9, 2, 6, 5]) == 9
    assert find_max([-10, -20, -30, -5]) == -5
    assert find_max([1.5, 2.5, 0.5]) == 2.5
    