from flask import Flask, jsonify
from models import db
from routes import api
from config import config
import os
import logging
from datetime import datetime

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Setup logging
    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
        app.logger.info('URL Shortener API startup')
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'URL Shortener API',
            'version': '1.0.0',
            'endpoints': {
                'shorten_url': 'POST /shorten',
                'redirect': 'GET /<short_code>',
                'statistics': 'GET /stats/<short_code>',
                'list_urls': 'GET /urls',
                'delete_url': 'DELETE /urls/<short_code>',
                'health_check': 'GET /health'
            },
            'documentation': '/docs'
        }), 200
    
    # API documentation endpoint
    @app.route('/docs')
    def api_docs():
        return jsonify({
            'title': 'URL Shortener API Documentation',
            'version': '1.0.0',
            'base_url': app.config.get('BASE_URL', 'http://localhost:5000'),
            'endpoints': {
                'POST /shorten': {
                    'description': 'Create a short URL',
                    'parameters': {
                        'url': 'string (required) - The URL to shorten',
                        'expires_in_hours': 'integer (optional) - Expiration time in hours'
                    },
                    'example_request': {
                        'url': 'https://www.example.com/very-long-url',
                        'expires_in_hours': 24
                    },
                    'example_response': {
                        'message': 'URL shortened successfully',
                        'data': {
                            'short_code': 'abc123',
                            'short_url': 'http://localhost:5000/abc123',
                            'original_url': 'https://www.example.com/very-long-url'
                        }
                    }
                },
                'GET /<short_code>': {
                    'description': 'Redirect to original URL',
                    'parameters': {
                        'short_code': 'string (required) - The short code to redirect'
                    },
                    'response': 'HTTP 302 redirect to original URL'
                },
                'GET /stats/<short_code>': {
                    'description': 'Get click statistics for a short URL',
                    'parameters': {
                        'short_code': 'string (required) - The short code to get stats for'
                    },
                    'example_response': {
                        'url': '...',
                        'statistics': {
                            'total_clicks': 42,
                            'clicks_last_30_days': 15,
                            'daily_stats': [{'date': '2026-02-05', 'clicks': 3}],
                            'top_referrers': [{'referrer': 'google.com', 'count': 10}]
                        }
                    }
                },
                'GET /urls': {
                    'description': 'List all URLs with pagination',
                    'parameters': {
                        'page': 'integer (optional, default=1) - Page number',
                        'per_page': 'integer (optional, default=20, max=100) - Items per page'
                    }
                },
                'DELETE /urls/<short_code>': {
                    'description': 'Deactivate a short URL',
                    'parameters': {
                        'short_code': 'string (required) - The short code to deactivate'
                    }
                },
                'GET /health': {
                    'description': 'Health check endpoint',
                    'response': {
                        'status': 'healthy',
                        'timestamp': '2026-02-05T10:30:00Z'
                    }
                }
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)