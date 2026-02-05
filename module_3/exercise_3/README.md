# Exercise 3: Context Anchors Practice

This exercise helps you practice using GitHub Copilot's context anchors to provide precise context.

## Setup
Two files have been created:
- `user.py` - User model
- `auth.py` - Authentication logic

## Tasks

### Task 1: Explain with File Context
Ask Copilot: **"Explain the User class in #file:user.py"**

This uses the `#file:` anchor to provide specific file context.

### Task 2: Cross-File Understanding
Ask Copilot: **"How does #file:auth.py use #file:user.py?"**

This demonstrates using multiple file anchors to understand relationships.

### Task 3: Selection Context
1. Open `auth.py`
2. Select the `authenticate_user` function (lines 29-43)
3. Ask Copilot: **"Add error handling to #selection"**

This uses the `#selection` anchor to work with specific code.

### Task 4: Terminal Context
1. Run the code (try importing and using the functions)
2. When you get an error in the terminal
3. Ask Copilot: **"Fix this error: #terminal"**

This uses the `#terminal` anchor to debug runtime errors.

## Expected Outcomes
- Learn to use `#file:` for file-specific questions
- Use `#selection` for targeted code modifications
- Use `#terminal` for debugging runtime errors
- Understand how context anchors improve Copilot's responses

## Notes
- The code intentionally has areas that could use error handling
- Try different combinations of context anchors
- Notice how specific context leads to better suggestions
