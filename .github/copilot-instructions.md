My Development Preferences
Code Style:

Use strict typing where possible (Type Hints in Python, strict types in TypeScript).

Prefer modular, functional components over monolithic classes.

Follow PEP8 for Python and Google C++ Style Guide for C++.

Use clean, descriptive naming conventions (e.g., is_user_authenticated instead of check).

Testing:

Every new feature must include unit tests (Pytest for Python, JUnit for Java).

Maintain a minimum of 80% code coverage.

Use mocks for external API calls and database layers.

Documentation:

Use JSDoc for JavaScript/TS or Docstrings for Python.

Include a brief "Why" in complex logic blocks, not just "What."

Generate README snippets for new environment variables or setup steps.

Security:

Never hardcode secrets; use environment variables.

Implement OWASP Top 10 mitigations (e.g., input sanitization, CSRF protection).

Use Argon2 or bcrypt for password hashing with appropriate salt rounds.
