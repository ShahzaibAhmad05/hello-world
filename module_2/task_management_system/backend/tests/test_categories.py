import pytest


def test_create_category(client, auth_headers):
    """Test creating a new category"""
    response = client.post('/api/categories',
        headers=auth_headers,
        json={
            'name': 'Work',
            'color': '#FF5733'
        }
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Work'
    assert data['color'] == '#FF5733'


def test_get_categories(client, auth_headers):
    """Test getting all categories"""
    # Create some categories
    client.post('/api/categories', headers=auth_headers, json={'name': 'Personal'})
    client.post('/api/categories', headers=auth_headers, json={'name': 'Work'})
    
    response = client.get('/api/categories', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2


def test_update_category(client, auth_headers):
    """Test updating a category"""
    # Create a category
    create_response = client.post('/api/categories',
        headers=auth_headers,
        json={'name': 'Old Name', 'color': '#000000'}
    )
    category_id = create_response.get_json()['id']
    
    # Update the category
    response = client.put(f'/api/categories/{category_id}',
        headers=auth_headers,
        json={'name': 'New Name', 'color': '#FFFFFF'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'New Name'
    assert data['color'] == '#FFFFFF'


def test_delete_category(client, auth_headers):
    """Test deleting a category"""
    # Create a category
    create_response = client.post('/api/categories',
        headers=auth_headers,
        json={'name': 'To Delete'}
    )
    category_id = create_response.get_json()['id']
    
    # Delete the category
    response = client.delete(f'/api/categories/{category_id}', headers=auth_headers)
    
    assert response.status_code == 200


def test_create_task_with_category(client, auth_headers):
    """Test creating a task with a category"""
    # Create a category first
    category_response = client.post('/api/categories',
        headers=auth_headers,
        json={'name': 'Project Alpha'}
    )
    category_id = category_response.get_json()['id']
    
    # Create a task with the category
    response = client.post('/api/tasks',
        headers=auth_headers,
        json={
            'title': 'Categorized Task',
            'category_id': category_id,
            'priority': 'medium'
        }
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['category_id'] == category_id
    assert data['category']['name'] == 'Project Alpha'
