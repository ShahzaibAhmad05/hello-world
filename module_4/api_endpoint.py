from typing import List, Optional, Dict, Any
from datetime import datetime
from flask import Flask, request, jsonify, Response
from functools import wraps
import os

"""
Blog Posts API Endpoint

This module provides REST API endpoints for managing blog posts.
Implements CRUD operations with proper validation and error handling.
"""


app = Flask(__name__)


# Models
class BlogPost:
    """Represents a blog post entity."""
    
    def __init__(
        self,
        post_id: int,
        title: str,
        content: str,
        author: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ) -> None:
        self.post_id = post_id
        self.title = title
        self.content = content
        self.author = author
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert blog post to dictionary representation."""
        return {
            "id": self.post_id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# In-memory storage (replace with database layer in production)
blog_posts: Dict[int, BlogPost] = {}
next_id: int = 1


# Authentication decorator (stub - implement actual auth)
def requires_auth(f):
    """
    Decorator to enforce authentication on endpoints.
    Why: Ensures only authenticated users can modify blog posts.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return jsonify({"error": "Authentication required"}), 401
        # TODO: Implement actual token validation
        return f(*args, **kwargs)
    return decorated


# Input validation
def validate_blog_post_input(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate blog post input data.
    Why: Prevents injection attacks and ensures data integrity (OWASP).
    """
    if not data:
        return "Request body is required"
    
    if not isinstance(data.get('title'), str) or len(data['title'].strip()) == 0:
        return "Title is required and must be a non-empty string"
    
    if not isinstance(data.get('content'), str) or len(data['content'].strip()) == 0:
        return "Content is required and must be a non-empty string"
    
    if not isinstance(data.get('author'), str) or len(data['author'].strip()) == 0:
        return "Author is required and must be a non-empty string"
    
    # Sanitize input to prevent XSS
    if any(char in data['title'] for char in ['<', '>', '"', "'"]):
        return "Title contains invalid characters"
    
    return None


@app.route('/api/posts', methods=['GET'])
def get_all_posts() -> Response:
    """Retrieve all blog posts."""
    posts_list = [post.to_dict() for post in blog_posts.values()]
    return jsonify({"posts": posts_list, "count": len(posts_list)}), 200


@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id: int) -> Response:
    """Retrieve a specific blog post by ID."""
    post = blog_posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    return jsonify(post.to_dict()), 200


@app.route('/api/posts', methods=['POST'])
@requires_auth
def create_post() -> Response:
    """Create a new blog post."""
    global next_id
    
    data = request.get_json()
    validation_error = validate_blog_post_input(data)
    
    if validation_error:
        return jsonify({"error": validation_error}), 400
    
    new_post = BlogPost(
        post_id=next_id,
        title=data['title'].strip(),
        content=data['content'].strip(),
        author=data['author'].strip()
    )
    
    blog_posts[next_id] = new_post
    next_id += 1
    
    return jsonify(new_post.to_dict()), 201


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@requires_auth
def update_post(post_id: int) -> Response:
    """Update an existing blog post."""
    post = blog_posts.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    data = request.get_json()
    validation_error = validate_blog_post_input(data)
    
    if validation_error:
        return jsonify({"error": validation_error}), 400
    
    post.title = data['title'].strip()
    post.content = data['content'].strip()
    post.author = data['author'].strip()
    post.updated_at = datetime.utcnow()
    
    return jsonify(post.to_dict()), 200


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@requires_auth
def delete_post(post_id: int) -> Response:
    """Delete a blog post."""
    if post_id not in blog_posts:
        return jsonify({"error": "Post not found"}), 404
    
    del blog_posts[post_id]
    return jsonify({"message": "Post deleted successfully"}), 200


if __name__ == '__main__':
    # Never hardcode secrets - use environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    
    app.run(debug=debug_mode, port=port)
    