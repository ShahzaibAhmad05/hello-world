"""Context-Rich API Endpoint Implementation

Based on context-rich prompt: RESTful API endpoint for task management
with validation, authentication, CORS, and comprehensive error handling.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from datetime import datetime
import jwt
import logging
from typing import Dict, Optional
from enum import Enum


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Simulated database
tasks_db = []
users_db = {1: "John Doe", 2: "Jane Smith"}
task_id_counter = 1


def require_auth(f):
    """JWT authentication decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
            return jsonify({'error': 'Authorization token required'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = data.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def validate_task_input(data: Dict) -> tuple[Optional[Dict], Optional[str]]:
    """Validate task input data.
    
    Returns:
        Tuple of (validated_data, error_message)
    """
    errors = []

    # Validate title (required, max 100 chars)
    title = data.get('title', '').strip()
    if not title:
        errors.append("Title is required")
    elif len(title) > 100:
        errors.append("Title must not exceed 100 characters")

    # Validate description (optional, max 500 chars)
    description = data.get('description', '').strip()
    if description and len(description) > 500:
        errors.append("Description must not exceed 500 characters")

    # Validate due_date (optional, ISO format)
    due_date = data.get('due_date')
    if due_date:
        try:
            datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            errors.append("Invalid due_date format. Use ISO 8601 format")

    # Validate priority (enum)
    priority = data.get('priority', 'medium').lower()
    valid_priorities = [p.value for p in Priority]
    if priority not in valid_priorities:
        errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")

    # Validate assigned_user_id (must exist)
    assigned_user_id = data.get('assigned_user_id')
    if assigned_user_id is not None:
        if not isinstance(assigned_user_id, int):
            errors.append("assigned_user_id must be an integer")
        elif assigned_user_id not in users_db:
            errors.append(f"User with ID {assigned_user_id} does not exist")

    if errors:
        return None, "; ".join(errors)

    return {
        'title': title,
        'description': description,
        'due_date': due_date,
        'priority': priority,
        'assigned_user_id': assigned_user_id
    }, None


@app.route('/api/tasks', methods=['POST'])
@require_auth
def create_task():
    """
    Create a new task.
    
    Request Body (JSON):
        - title (str, required, max 100 chars)
        - description (str, optional, max 500 chars)
        - due_date (str, optional, ISO 8601 format)
        - priority (str, optional, one of: low/medium/high)
        - assigned_user_id (int, optional, must exist in users table)
    
    Returns:
        201: Task created successfully
        400: Validation error
        401: Unauthorized
        500: Server error
    """
    global task_id_counter
    
    # Log request
    logger.info(f"Task creation request from user {request.user_id} at {datetime.utcnow()}")
    
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Validate input
        validated_data, error = validate_task_input(data)
        if error:
            logger.warning(f"Validation error: {error}")
            return jsonify({'error': error}), 400
        
        # Create task
        task = {
            'id': task_id_counter,
            'title': validated_data['title'],
            'description': validated_data['description'],
            'due_date': validated_data['due_date'],
            'priority': validated_data['priority'],
            'assigned_user_id': validated_data['assigned_user_id'],
            'created_by': request.user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        tasks_db.append(task)
        task_id_counter += 1
        
        logger.info(f"Task {task['id']} created successfully")
        
        # Return created task with 201 status
        return jsonify({
            'message': 'Task created successfully',
            'task': task
        }), 201
    
    except Exception as e:
        logger.error(f"Server error during task creation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/tasks', methods=['GET'])
@require_auth
def get_tasks():
    """Get all tasks for authenticated user."""
    logger.info(f"Task list request from user {request.user_id}")
    return jsonify({'tasks': tasks_db}), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200


if __name__ == '__main__':
    # Generate a sample JWT token for testing
    test_token = jwt.encode(
        {'user_id': 1, 'exp': datetime.utcnow().timestamp() + 3600},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    print(f"Test token: {test_token}")
    print("\nExample curl command:")
    print(f'curl -X POST http://localhost:5000/api/tasks \\')
    print(f'  -H "Authorization: Bearer {test_token}" \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"title": "Test Task", "priority": "high", "assigned_user_id": 1}}\'')
    
    app.run(debug=True, port=5000)
