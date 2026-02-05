import pytest
from app import create_app
from models import db, URL, Click
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_url():
    """Sample URL for testing"""
    return 'https://www.example.com/test-page'

@pytest.fixture
def sample_url_data(sample_url):
    """Sample URL data for API requests"""
    return {'url': sample_url}