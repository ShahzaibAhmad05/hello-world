import pytest
from models import User, Task, Category
from datetime import datetime, timedelta


def test_full_workflow(client, app):
    """Integration test for complete user workflow"""
    # 1. Register a new user
    register_data = {
        'username': 'integrationuser',
        'email': 'integration@example.com',
        'password': 'securepass123'
    }
    
    response = client.post('/api/auth/register', json=register_data)
    assert response.status_code == 201
    data = response.get_json()
    token = data['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. Create a category
    category_response = client.post('/api/categories',
        headers=headers,
        json={'name': 'Work Projects', 'color': '#FF5733'}
    )
    assert category_response.status_code == 201
    category_id = category_response.get_json()['id']
    
    # 3. Create multiple tasks
    tasks_to_create = [
        {'title': 'High Priority Task', 'priority': 'high', 'category_id': category_id},
        {'title': 'Medium Task', 'priority': 'medium', 'description': 'Some details'},
        {'title': 'Low Priority Task', 'priority': 'low', 'due_date': (datetime.utcnow() + timedelta(days=7)).isoformat()},
    ]
    
    task_ids = []
    for task_data in tasks_to_create:
        response = client.post('/api/tasks', headers=headers, json=task_data)
        assert response.status_code == 201
        task_ids.append(response.get_json()['id'])
    
    # 4. Get all tasks
    response = client.get('/api/tasks', headers=headers)
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 3
    
    # 5. Filter tasks by priority
    response = client.get('/api/tasks?priority=high', headers=headers)
    assert response.status_code == 200
    high_priority_tasks = response.get_json()
    assert len(high_priority_tasks) == 1
    assert high_priority_tasks[0]['title'] == 'High Priority Task'
    
    # 6. Update a task
    response = client.put(f'/api/tasks/{task_ids[0]}',
        headers=headers,
        json={'title': 'Updated High Priority Task', 'completed': True}
    )
    assert response.status_code == 200
    updated_task = response.get_json()
    assert updated_task['title'] == 'Updated High Priority Task'
    assert updated_task['completed'] == True
    
    # 7. Filter completed tasks
    response = client.get('/api/tasks?completed=true', headers=headers)
    assert response.status_code == 200
    completed_tasks = response.get_json()
    assert len(completed_tasks) == 1
    
    # 8. Delete a task
    response = client.delete(f'/api/tasks/{task_ids[1]}', headers=headers)
    assert response.status_code == 200
    
    # 9. Verify task was deleted
    response = client.get('/api/tasks', headers=headers)
    assert response.status_code == 200
    remaining_tasks = response.get_json()
    assert len(remaining_tasks) == 2
    
    # 10. Logout (verify token still works until expiration)
    response = client.get('/api/auth/me', headers=headers)
    assert response.status_code == 200


def test_user_isolation(client):
    """Test that users can only access their own data"""
    # Create first user
    user1_data = {
        'username': 'user1',
        'email': 'user1@example.com',
        'password': 'password123'
    }
    response = client.post('/api/auth/register', json=user1_data)
    user1_token = response.get_json()['access_token']
    user1_headers = {'Authorization': f'Bearer {user1_token}'}
    
    # Create second user
    user2_data = {
        'username': 'user2',
        'email': 'user2@example.com',
        'password': 'password123'
    }
    response = client.post('/api/auth/register', json=user2_data)
    user2_token = response.get_json()['access_token']
    user2_headers = {'Authorization': f'Bearer {user2_token}'}
    
    # User 1 creates a task
    task_response = client.post('/api/tasks',
        headers=user1_headers,
        json={'title': 'User 1 Task', 'priority': 'high'}
    )
    task_id = task_response.get_json()['id']
    
    # User 1 can access their task
    response = client.get(f'/api/tasks/{task_id}', headers=user1_headers)
    assert response.status_code == 200
    
    # User 2 cannot access User 1's task
    response = client.get(f'/api/tasks/{task_id}', headers=user2_headers)
    assert response.status_code == 404
    
    # User 2's task list is empty
    response = client.get('/api/tasks', headers=user2_headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 0


def test_category_cascade_delete(client, auth_headers, app):
    """Test that deleting a category sets tasks' category_id to NULL"""
    # Create a category
    category_response = client.post('/api/categories',
        headers=auth_headers,
        json={'name': 'Test Category'}
    )
    category_id = category_response.get_json()['id']
    
    # Create a task with this category
    task_response = client.post('/api/tasks',
        headers=auth_headers,
        json={'title': 'Categorized Task', 'category_id': category_id, 'priority': 'medium'}
    )
    task_id = task_response.get_json()['id']
    
    # Delete the category
    response = client.delete(f'/api/categories/{category_id}', headers=auth_headers)
    assert response.status_code == 200
    
    # Verify task still exists but category_id is NULL
    task_response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
    assert task_response.status_code == 200
    task = task_response.get_json()
    assert task['category_id'] is None


def test_error_handling(client, auth_headers):
    """Test various error scenarios"""
    # Invalid priority
    response = client.post('/api/tasks',
        headers=auth_headers,
        json={'title': 'Task', 'priority': 'invalid'}
    )
    assert response.status_code == 400
    
    # Missing required field
    response = client.post('/api/tasks',
        headers=auth_headers,
        json={'description': 'No title'}
    )
    assert response.status_code == 400
    
    # Invalid due date format
    response = client.post('/api/tasks',
        headers=auth_headers,
        json={'title': 'Task', 'due_date': 'not-a-date', 'priority': 'low'}
    )
    assert response.status_code == 400
    
    # Access non-existent task
    response = client.get('/api/tasks/99999', headers=auth_headers)
    assert response.status_code == 404
    
    # Delete non-existent task
    response = client.delete('/api/tasks/99999', headers=auth_headers)
    assert response.status_code == 404
