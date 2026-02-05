from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task, Category
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')
categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')


# ============ Task Routes ============

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Query parameters for filtering
        completed = request.args.get('completed')
        priority = request.args.get('priority')
        category_id = request.args.get('category_id')
        
        query = Task.query.filter_by(user_id=current_user_id)
        
        if completed is not None:
            query = query.filter_by(completed=completed.lower() == 'true')
        
        if priority:
            query = query.filter_by(priority=priority)
        
        if category_id:
            query = query.filter_by(category_id=int(category_id))
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        return jsonify([task.to_dict() for task in tasks]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    try:
        current_user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify(task.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high']
        priority = data.get('priority', 'medium')
        if priority not in valid_priorities:
            return jsonify({'error': f'Priority must be one of: {", ".join(valid_priorities)}'}), 400
        
        # Parse due date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use ISO format'}), 400
        
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=priority,
            due_date=due_date,
            category_id=data.get('category_id'),
            user_id=current_user_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify(task.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    try:
        current_user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'completed' in data:
            task.completed = data['completed']
        if 'priority' in data:
            valid_priorities = ['low', 'medium', 'high']
            if data['priority'] not in valid_priorities:
                return jsonify({'error': f'Priority must be one of: {", ".join(valid_priorities)}'}), 400
            task.priority = data['priority']
        if 'category_id' in data:
            task.category_id = data['category_id']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Invalid due_date format. Use ISO format'}), 400
            else:
                task.due_date = None
        
        db.session.commit()
        
        return jsonify(task.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    try:
        current_user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ Category Routes ============

@categories_bp.route('', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all categories for the current user"""
    try:
        current_user_id = get_jwt_identity()
        categories = Category.query.filter_by(user_id=current_user_id).all()
        
        return jsonify([category.to_dict() for category in categories]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@categories_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new category"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        category = Category(
            name=data['name'],
            color=data.get('color', '#3B82F6'),
            user_id=current_user_id
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify(category.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Update a category"""
    try:
        current_user_id = get_jwt_identity()
        category = Category.query.filter_by(id=category_id, user_id=current_user_id).first()
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            category.name = data['name']
        if 'color' in data:
            category.color = data['color']
        
        db.session.commit()
        
        return jsonify(category.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Delete a category"""
    try:
        current_user_id = get_jwt_identity()
        category = Category.query.filter_by(id=category_id, user_id=current_user_id).first()
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': 'Category deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
