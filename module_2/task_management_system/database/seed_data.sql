-- Seed data for testing Task Management System
-- Password for all users: password123

-- Insert test users
INSERT INTO users (username, email, password_hash, created_at) VALUES
('john_doe', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/VqTwe', CURRENT_TIMESTAMP),
('jane_smith', 'jane@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/VqTwe', CURRENT_TIMESTAMP),
('test_user', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/VqTwe', CURRENT_TIMESTAMP);

-- Insert categories for user 1 (john_doe)
INSERT INTO categories (name, color, user_id, created_at) VALUES
('Work', '#3B82F6', 1, CURRENT_TIMESTAMP),
('Personal', '#10B981', 1, CURRENT_TIMESTAMP),
('Shopping', '#F59E0B', 1, CURRENT_TIMESTAMP),
('Health', '#EF4444', 1, CURRENT_TIMESTAMP);

-- Insert categories for user 2 (jane_smith)
INSERT INTO categories (name, color, user_id, created_at) VALUES
('Projects', '#8B5CF6', 2, CURRENT_TIMESTAMP),
('Family', '#EC4899', 2, CURRENT_TIMESTAMP);

-- Insert tasks for user 1 (john_doe)
INSERT INTO tasks (title, description, completed, priority, due_date, user_id, category_id, created_at, updated_at) VALUES
('Complete project proposal', 'Draft and submit the Q1 project proposal to management', 0, 'high', datetime('now', '+3 days'), 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Team meeting preparation', 'Prepare slides and agenda for weekly team sync', 0, 'medium', datetime('now', '+1 day'), 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Code review', 'Review pull requests from team members', 1, 'medium', datetime('now', '-1 day'), 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Grocery shopping', 'Buy milk, eggs, bread, and vegetables', 0, 'low', datetime('now', '+2 days'), 1, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Dentist appointment', 'Annual checkup at 2 PM', 0, 'high', datetime('now', '+7 days'), 1, 4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Read book chapter', 'Finish chapter 5 of "Clean Code"', 1, 'low', NULL, 1, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Update resume', 'Add recent projects and achievements', 0, 'medium', datetime('now', '+14 days'), 1, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert tasks for user 2 (jane_smith)
INSERT INTO tasks (title, description, completed, priority, due_date, user_id, category_id, created_at, updated_at) VALUES
('Website redesign', 'Create mockups for the new company website', 0, 'high', datetime('now', '+5 days'), 2, 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Client presentation', 'Prepare demo for client meeting', 0, 'high', datetime('now', '+2 days'), 2, 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Birthday planning', 'Plan surprise party for mom', 0, 'medium', datetime('now', '+10 days'), 2, 6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Database migration', 'Migrate legacy database to new schema', 1, 'high', datetime('now', '-2 days'), 2, 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert tasks for user 3 (test_user) - no categories
INSERT INTO tasks (title, description, completed, priority, due_date, user_id, category_id, created_at, updated_at) VALUES
('Sample task 1', 'This is a sample task for testing', 0, 'low', NULL, 3, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Sample task 2', 'Another sample task', 1, 'medium', datetime('now', '-1 day'), 3, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
