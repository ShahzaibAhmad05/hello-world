import pytest
from models import User, db


def test_register_success(client):
    """Test successful user registration"""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['username'] == 'newuser'


def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    # First registration
    client.post('/api/auth/register', json={
        'username': 'duplicate',
        'email': 'user1@example.com',
        'password': 'password123'
    })
    
    # Second registration with same username
    response = client.post('/api/auth/register', json={
        'username': 'duplicate',
        'email': 'user2@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 409
    assert 'already exists' in response.get_json()['error'].lower()


def test_register_missing_fields(client):
    """Test registration with missing fields"""
    response = client.post('/api/auth/register', json={
        'username': 'incompleteuser'
    })
    
    assert response.status_code == 400


def test_login_success(client):
    """Test successful login"""
    # Register user first
    client.post('/api/auth/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'password123'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """Test getting current user information"""
    response = client.get('/api/auth/me', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'testuser'


def test_get_current_user_no_token(client):
    """Test getting current user without token"""
    response = client.get('/api/auth/me')
    
    assert response.status_code == 401
