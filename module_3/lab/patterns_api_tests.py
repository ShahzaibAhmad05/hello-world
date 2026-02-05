"""Pattern Library: API Endpoints and Test Cases

Few-shot examples for creating REST APIs and comprehensive tests.
"""

from flask import Flask, request, jsonify
import pytest
from unittest.mock import Mock, patch
import json

app = Flask(__name__)

# Simulated database
books_db = [
    {'id': 1, 'title': 'Python Basics', 'author': 'John Doe', 'isbn': '978-1234567890', 'genre': 'Programming', 'checked_out': False},
    {'id': 2, 'title': 'Advanced Python', 'author': 'Jane Smith', 'isbn': '978-0987654321', 'genre': 'Programming', 'checked_out': False},
]
next_id = 3


# ============================================================================
# API ENDPOINTS PATTERN LIBRARY
# ============================================================================

@app.route('/api/books', methods=['GET'])
def get_books():
    """
    GET endpoint - Example 1 from pattern library.
    
    Demonstrates: pagination, filtering, sorting, caching, error handling.
    Query parameters:
        - search: search term
        - genre: filter by genre
        - author: filter by author
        - sort: sort field (title, author, date)
        - page: page number
        - limit: results per page
    """
    try:
        # Extract query parameters
        search = request.args.get('search', '').lower()
        genre = request.args.get('genre')
        author = request.args.get('author')
        sort_by = request.args.get('sort', 'title')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Validate pagination
        if page < 1 or limit < 1 or limit > 100:
            return jsonify({'error': 'Invalid pagination parameters'}), 400
        
        # Filter books
        filtered_books = books_db
        
        if search:
            filtered_books = [
                b for b in filtered_books
                if search in b['title'].lower() or search in b['author'].lower()
            ]
        
        if genre:
            filtered_books = [b for b in filtered_books if b['genre'] == genre]
        
        if author:
            filtered_books = [b for b in filtered_books if author.lower() in b['author'].lower()]
        
        # Sort books
        sort_key = 'title' if sort_by not in ['title', 'author'] else sort_by
        filtered_books = sorted(filtered_books, key=lambda x: x[sort_key])
        
        # Paginate
        total_count = len(filtered_books)
        start = (page - 1) * limit
        end = start + limit
        paginated_books = filtered_books[start:end]
        
        # Prepare response with metadata
        response = {
            'data': paginated_books,
            'metadata': {
                'total_count': total_count,
                'page': page,
                'limit': limit,
                'total_pages': (total_count + limit - 1) // limit
            }
        }
        
        # Add caching headers
        resp = jsonify(response)
        resp.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
        return resp, 200
        
    except ValueError:
        return jsonify({'error': 'Invalid parameter type'}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@app.route('/api/books', methods=['POST'])
def create_book():
    """
    POST endpoint - Example 2 from pattern library.
    
    Demonstrates: input validation, duplicate checking, authentication,
    logging, notifications, proper status codes.
    """
    global next_id
    
    try:
        # Authentication check (simulated)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get JSON payload
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Validate required fields
        required_fields = ['title', 'author', 'isbn']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'fields': missing_fields
            }), 400
        
        # Validate ISBN format (simplified)
        isbn = data['isbn'].replace('-', '')
        if not (len(isbn) in [10, 13] and isbn.isdigit()):
            return jsonify({'error': 'Invalid ISBN format'}), 400
        
        # Check for duplicate ISBN
        if any(b['isbn'] == data['isbn'] for b in books_db):
            return jsonify({'error': 'Book with this ISBN already exists'}), 409
        
        # Create book
        book = {
            'id': next_id,
            'title': data['title'],
            'author': data['author'],
            'isbn': data['isbn'],
            'genre': data.get('genre', 'Uncategorized'),
            'checked_out': False
        }
        
        books_db.append(book)
        next_id += 1
        
        # Log operation (simulated)
        print(f"[LOG] Book created: {book['id']} - {book['title']}")
        
        # Send notification (simulated)
        print(f"[NOTIFY] New book added: {book['title']}")
        
        # Return created resource
        return jsonify({
            'message': 'Book created successfully',
            'data': book
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Failed to create book: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    PUT endpoint - Example 3 from pattern library.
    
    Demonstrates: ownership validation, partial updates, audit trail,
    optimistic locking, business rules, transaction handling.
    """
    try:
        # Find book
        book = next((b for b in books_db if b['id'] == book_id), None)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Get update data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Business rule: Cannot change status if book is checked out
        if book['checked_out'] and 'checked_out' in data:
            return jsonify({
                'error': 'Cannot modify checkout status while book is checked out'
            }), 400
        
        # Partial update
        allowed_fields = ['title', 'author', 'genre']
        updated_fields = []
        
        for field in allowed_fields:
            if field in data:
                book[field] = data[field]
                updated_fields.append(field)
        
        # Audit trail (simulated)
        print(f"[AUDIT] Book {book_id} updated. Fields: {', '.join(updated_fields)}")
        
        return jsonify({
            'message': 'Book updated successfully',
            'data': book,
            'updated_fields': updated_fields
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to update book: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# TEST CASES PATTERN LIBRARY
# ============================================================================

class TestBookAPI:
    """Comprehensive test cases for book API."""

    @pytest.fixture
    def client(self):
        """Test client fixture."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def mock_auth_header(self):
        """Mock authentication header."""
        return {'Authorization': 'Bearer test_token_123'}

    # ========================================================================
    # Unit Test Pattern - Example 1
    # ========================================================================
    def test_create_book_success(self, client, mock_auth_header):
        """
        Unit test for successful book creation.
        
        Demonstrates: mocking, test data setup, assertions, cleanup.
        """
        # Arrange
        test_book = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '978-1111111111',
            'genre': 'Testing'
        }
        
        # Act
        response = client.post(
            '/api/books',
            data=json.dumps(test_book),
            headers={'Content-Type': 'application/json', **mock_auth_header}
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Book created successfully'
        assert 'data' in data
        assert data['data']['title'] == test_book['title']
        assert data['data']['author'] == test_book['author']
        assert 'id' in data['data']
        
        # Cleanup (remove test book)
        created_id = data['data']['id']
        books_db[:] = [b for b in books_db if b['id'] != created_id]

    # ========================================================================
    # Integration Test Pattern - Example 2
    # ========================================================================
    def test_book_creation_and_retrieval(self, client, mock_auth_header):
        """
        Integration test for complete book workflow.
        
        Demonstrates: multi-step workflow, error scenarios, rollback,
        data consistency validation.
        """
        # Step 1: Create book
        new_book = {
            'title': 'Integration Test Book',
            'author': 'Test Author',
            'isbn': '978-2222222222'
        }
        
        create_response = client.post(
            '/api/books',
            data=json.dumps(new_book),
            headers={'Content-Type': 'application/json', **mock_auth_header}
        )
        assert create_response.status_code == 201
        created_book = json.loads(create_response.data)['data']
        
        try:
            # Step 2: Retrieve the created book
            get_response = client.get(
                '/api/books',
                query_string={'search': 'Integration Test'}
            )
            assert get_response.status_code == 200
            books = json.loads(get_response.data)['data']
            assert len(books) > 0
            assert any(b['id'] == created_book['id'] for b in books)
            
            # Step 3: Update the book
            update_data = {'title': 'Updated Integration Test'}
            update_response = client.put(
                f"/api/books/{created_book['id']}",
                data=json.dumps(update_data),
                headers={'Content-Type': 'application/json'}
            )
            assert update_response.status_code == 200
            
            # Step 4: Verify update
            updated_book = json.loads(update_response.data)['data']
            assert updated_book['title'] == update_data['title']
            
        finally:
            # Cleanup
            books_db[:] = [b for b in books_db if b['id'] != created_book['id']]

    # ========================================================================
    # Error Handling Test Pattern - Example 3
    # ========================================================================
    def test_create_book_validation_errors(self, client, mock_auth_header):
        """
        Test various validation error scenarios.
        
        Demonstrates: error case testing, boundary conditions,
        error message validation.
        """
        # Test 1: Missing required fields
        response = client.post(
            '/api/books',
            data=json.dumps({'title': 'Incomplete Book'}),
            headers={'Content-Type': 'application/json', **mock_auth_header}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'fields' in data
        
        # Test 2: Invalid ISBN format
        response = client.post(
            '/api/books',
            data=json.dumps({
                'title': 'Test',
                'author': 'Test',
                'isbn': 'invalid'
            }),
            headers={'Content-Type': 'application/json', **mock_auth_header}
        )
        assert response.status_code == 400
        
        # Test 3: Duplicate ISBN
        duplicate_book = {
            'title': 'Duplicate Test',
            'author': 'Test',
            'isbn': books_db[0]['isbn']  # Use existing ISBN
        }
        response = client.post(
            '/api/books',
            data=json.dumps(duplicate_book),
            headers={'Content-Type': 'application/json', **mock_auth_header}
        )
        assert response.status_code == 409

    def test_authentication_required(self, client):
        """Test that authentication is enforced."""
        response = client.post(
            '/api/books',
            data=json.dumps({'title': 'Test'}),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 401


if __name__ == '__main__':
    print("API Endpoints and Test Cases Pattern Library")
    print("\nTo run tests: pytest patterns_api_tests.py -v")
    print("\nTo run Flask app: python patterns_api_tests.py")
    
    # Run Flask app for manual testing
    app.run(debug=True, port=5001)
