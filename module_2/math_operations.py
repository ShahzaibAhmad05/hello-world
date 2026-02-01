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
    