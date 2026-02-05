# URL Shortener Service Tests

This directory contains comprehensive tests for the URL shortener service.

## Test Structure

### `conftest.py`
- Contains pytest fixtures used across all test files
- Sets up test application with in-memory SQLite database
- Provides sample data for testing

### `test_utils_models.py`
- Tests utility functions (URL validation, encoding, etc.)
- Tests database models (URL and Click models)
- Tests model relationships and methods

### `test_api.py`  
- Tests all API endpoints
- Tests request/response handling
- Tests error conditions and edge cases
- Tests authentication and validation

### `test_integration.py`
- End-to-end integration tests
- Tests complete workflows
- Tests system behavior under load
- Tests error handling across components

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_api.py
```

### Run specific test
```bash
pytest tests/test_api.py::TestAPI::test_shorten_url_valid
```

### Run with verbose output
```bash
pytest -v
```

## Test Coverage

The tests cover:
- ✅ All API endpoints (POST /shorten, GET /<short_code>, etc.)
- ✅ URL validation and normalization
- ✅ Database models and relationships
- ✅ Click tracking and analytics
- ✅ Error handling and edge cases
- ✅ URL expiration functionality
- ✅ Pagination and listing
- ✅ Complete user workflows
- ✅ Concurrent operations
- ✅ Performance under load

## Test Data

Tests use realistic but safe test data:
- Valid URLs from well-known domains
- Various URL formats and edge cases  
- Different user agents and referrers
- Expired and active URLs
- Large datasets for pagination testing

## Mocking

Tests use:
- In-memory SQLite database for isolation
- Flask test client for HTTP requests
- Pytest fixtures for consistent test setup
- Time manipulation for expiration testing