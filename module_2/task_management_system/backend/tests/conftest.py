import pytest
from app import create_app
from models import db, User, Task, Category


@pytest.fixture
def app():
    """Create and configure a test application instance"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Create a user and return auth headers"""
    # Register a test user
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    data = response.get_json()
    token = data['access_token']
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_user(app):
    """Create a sample user"""
    with app.app_context():
        user = User(username='sampleuser', email='sample@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id
