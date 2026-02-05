import pytest
from datetime import datetime, timedelta


def test_create_task(client, auth_headers):
    """Test creating a new task"""
    response = client.post('/api/tasks', 
        headers=auth_headers,
        json={
            'title': 'Test Task',
            'description': 'This is a test task',
            'priority': 'high'
        }
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Task'
    assert data['priority'] == 'high'
    assert data['completed'] == False


def test_create_task_with_due_date(client, auth_headers):
    """Test creating a task with due date"""
    due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    
    response = client.post('/api/tasks',
        headers=auth_headers,
        json={
            'title': 'Task with deadline',
            'due_date': due_date,
            'priority': 'medium'
        }
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['due_date'] is not None


def test_create_task_missing_title(client, auth_headers):
    """Test creating a task without title"""
    response = client.post('/api/tasks',
        headers=auth_headers,
        json={'description': 'No title task'}
    )
    
    assert response.status_code == 400


def test_get_tasks(client, auth_headers):
    """Test getting all tasks"""
    # Create some tasks
    client.post('/api/tasks', headers=auth_headers, json={'title': 'Task 1', 'priority': 'low'})
    client.post('/api/tasks', headers=auth_headers, json={'title': 'Task 2', 'priority': 'high'})
    
    response = client.get('/api/tasks', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2


def test_get_task_by_id(client, auth_headers):
    """Test getting a specific task"""
    # Create a task
    create_response = client.post('/api/tasks',
        headers=auth_headers,
        json={'title': 'Specific Task', 'priority': 'medium'}
    )
    task_id = create_response.get_json()['id']
    
    # Get the task
    response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Specific Task'


def test_update_task(client, auth_headers):
    """Test updating a task"""
    # Create a task
    create_response = client.post('/api/tasks',
        headers=auth_headers,
        json={'title': 'Original Title', 'priority': 'low'}
    )
    task_id = create_response.get_json()['id']
    
    # Update the task
    response = client.put(f'/api/tasks/{task_id}',
        headers=auth_headers,
        json={
            'title': 'Updated Title',
            'completed': True,
            'priority': 'high'
        }
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Updated Title'
    assert data['completed'] == True
    assert data['priority'] == 'high'


def test_delete_task(client, auth_headers):
    """Test deleting a task"""
    # Create a task
    create_response = client.post('/api/tasks',
        headers=auth_headers,
        json={'title': 'Task to Delete', 'priority': 'medium'}
    )
    task_id = create_response.get_json()['id']
    
    # Delete the task
    response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
    
    assert response.status_code == 200
    
    # Verify task is deleted
    get_response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
    assert get_response.status_code == 404


def test_filter_tasks_by_priority(client, auth_headers):
    """Test filtering tasks by priority"""
    # Create tasks with different priorities
    client.post('/api/tasks', headers=auth_headers, json={'title': 'Low Priority', 'priority': 'low'})
    client.post('/api/tasks', headers=auth_headers, json={'title': 'High Priority', 'priority': 'high'})
    
    # Filter by high priority
    response = client.get('/api/tasks?priority=high', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['priority'] == 'high'


def test_unauthorized_access(client):
    """Test accessing tasks without authentication"""
    response = client.get('/api/tasks')
    
    assert response.status_code == 401
