import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { tasksAPI, categoriesAPI } from './api';
import TaskForm from './TaskForm';

function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filter, setFilter] = useState({ priority: '', completed: '', category_id: '' });
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchTasks();
    fetchCategories();
  }, [filter]);

  const fetchTasks = async () => {
    try {
      const params = {};
      if (filter.priority) params.priority = filter.priority;
      if (filter.completed !== '') params.completed = filter.completed;
      if (filter.category_id) params.category_id = filter.category_id;

      const response = await tasksAPI.getTasks(params);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.getCategories();
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;

    try {
      await tasksAPI.deleteTask(taskId);
      setTasks(tasks.filter(task => task.id !== taskId));
    } catch (error) {
      console.error('Error deleting task:', error);
      alert('Failed to delete task');
    }
  };

  const handleToggleComplete = async (task) => {
    try {
      const response = await tasksAPI.updateTask(task.id, { completed: !task.completed });
      setTasks(tasks.map(t => t.id === task.id ? response.data : t));
    } catch (error) {
      console.error('Error updating task:', error);
      alert('Failed to update task');
    }
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setShowTaskForm(true);
  };

  const handleTaskSaved = () => {
    setShowTaskForm(false);
    setEditingTask(null);
    fetchTasks();
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading tasks...</p>
      </div>
    );
  }

  return (
    <div>
      <header className="header">
        <div className="header-content">
          <h1>📋 Task Manager</h1>
          <div className="header-actions">
            <div className="user-info">
              <span>Welcome, {user?.username}!</span>
            </div>
            <button onClick={handleLogout} className="btn btn-outline btn-small">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="container">
        <div className="task-list-container">
          {/* Filters */}
          <div className="task-filters">
            <button 
              onClick={() => setShowTaskForm(true)} 
              className="btn btn-primary"
            >
              + New Task
            </button>

            <select 
              value={filter.priority} 
              onChange={(e) => setFilter({ ...filter, priority: e.target.value })}
            >
              <option value="">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>

            <select 
              value={filter.completed} 
              onChange={(e) => setFilter({ ...filter, completed: e.target.value })}
            >
              <option value="">All Tasks</option>
              <option value="false">Active</option>
              <option value="true">Completed</option>
            </select>

            <select 
              value={filter.category_id} 
              onChange={(e) => setFilter({ ...filter, category_id: e.target.value })}
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>

          {/* Task Grid */}
          {tasks.length === 0 ? (
            <div className="empty-state">
              <h3>No tasks found</h3>
              <p>Create a new task to get started!</p>
            </div>
          ) : (
            <div className="task-grid">
              {tasks.map(task => (
                <div 
                  key={task.id} 
                  className={`task-card priority-${task.priority} ${task.completed ? 'completed' : ''}`}
                >
                  <div className="task-header">
                    <div>
                      <h3 className={`task-title ${task.completed ? 'completed' : ''}`}>
                        {task.title}
                      </h3>
                      {task.category && (
                        <span 
                          className="task-category" 
                          style={{ backgroundColor: task.category.color + '20', color: task.category.color }}
                        >
                          {task.category.name}
                        </span>
                      )}
                    </div>
                    <span className={`task-priority priority-${task.priority}`}>
                      {task.priority}
                    </span>
                  </div>

                  {task.description && (
                    <p className="task-description">{task.description}</p>
                  )}

                  <div className="task-meta">
                    {task.due_date && (
                      <span>📅 Due: {new Date(task.due_date).toLocaleDateString()}</span>
                    )}
                    <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
                  </div>

                  <div className="task-actions">
                    <button 
                      onClick={() => handleToggleComplete(task)}
                      className="icon-btn complete"
                    >
                      {task.completed ? '↩️ Undo' : '✓ Complete'}
                    </button>
                    <button 
                      onClick={() => handleEditTask(task)}
                      className="icon-btn edit"
                    >
                      ✏️ Edit
                    </button>
                    <button 
                      onClick={() => handleDeleteTask(task.id)}
                      className="icon-btn delete"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Task Form Modal */}
      {showTaskForm && (
        <TaskForm
          task={editingTask}
          categories={categories}
          onClose={() => {
            setShowTaskForm(false);
            setEditingTask(null);
          }}
          onSave={handleTaskSaved}
        />
      )}
    </div>
  );
}

export default Dashboard;
