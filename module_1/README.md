
## Task Manager Documentation

### Overview

The Task Manager is a comprehensive Python application for managing tasks with various operations including adding, listing, completing, deleting, filtering, and searching tasks. It provides a simple yet powerful interface for task organization and tracking.

>![NOTE]
>This README was generated using co-pilot (Claude Sonnet 4.5), it may contain minor issues / mistakes.

### Features

- ✅ **Add Tasks**: Create new tasks with title, description, and priority levels
- 📋 **List Tasks**: View all tasks with their status and details
- ✔️ **Complete Tasks**: Mark tasks as completed
- 🗑️ **Delete Tasks**: Remove tasks from the list
- 🔍 **Filter by Priority**: View tasks based on priority levels (high/medium/low)
- 🔎 **Search Tasks**: Find tasks by keywords in title or description

### Installation

No external dependencies required. The Task Manager uses only Python standard library.

```bash
# Clone or navigate to the project directory
cd hello-world

# Ensure you're using Python 3.6 or later
python --version
```

### Usage Examples

#### Basic Usage

```python
from module_1.task_manager import TaskManager

# Create a new task manager instance
manager = TaskManager()

# Add some tasks
manager.add_task("Buy groceries", "Milk, Bread, Eggs", "high")
manager.add_task("Read book", "Finish reading '1984'", "medium")
manager.add_task("Exercise", "Go for a 30-minute run", "low")

# List all tasks
print("All Tasks:")
manager.list_tasks()
```

**Output:**
```
All Tasks:
1. [Pending] Buy groceries - Milk, Bread, Eggs (Priority: high)
2. [Pending] Read book - Finish reading '1984' (Priority: medium)
3. [Pending] Exercise - Go for a 30-minute run (Priority: low)
```

#### Completing Tasks

```python
# Mark the first task as complete (index 0)
manager.mark_task_complete(0)

# View updated task list
manager.list_tasks()
```

**Output:**
```
1. [Completed] Buy groceries - Milk, Bread, Eggs (Priority: high)
2. [Pending] Read book - Finish reading '1984' (Priority: medium)
3. [Pending] Exercise - Go for a 30-minute run (Priority: low)
```

#### Filtering by Priority

```python
# View only high-priority tasks
print("\nHigh Priority Tasks:")
manager.filter_tasks_by_priority("high")

# View only medium-priority tasks
print("\nMedium Priority Tasks:")
manager.filter_tasks_by_priority("medium")
```

**Output:**
```
High Priority Tasks:
1. [Completed] Buy groceries - Milk, Bread, Eggs (Priority: high)

Medium Priority Tasks:
1. [Pending] Read book - Finish reading '1984' (Priority: medium)
```

#### Searching Tasks

```python
# Search for tasks containing "read"
print("\nSearch results for 'read':")
manager.search_tasks_by_keyword("read")

# Search is case-insensitive
manager.search_tasks_by_keyword("BOOK")
```

**Output:**
```
Search results for 'read':
1. [Pending] Read book - Finish reading '1984' (Priority: medium)
```

#### Deleting Tasks

```python
# Delete a task by index (0-based)
manager.delete_task(1)  # Deletes the second task

# View remaining tasks
manager.list_tasks()
```

### API Reference

#### Task Class

```python
Task(title: str, description: str, priority: str)
```

**Attributes:**
- `title` (str): The title of the task
- `description` (str): Detailed description of the task
- `priority` (str): Priority level - "high", "medium", or "low"
- `completed` (bool): Task completion status

**Methods:**
- `mark_complete()`: Mark the task as completed
- `__str__()`: Return string representation of the task

#### TaskManager Class

```python
TaskManager()
```

**Attributes:**
- `tasks` (list): List of Task objects

**Methods:**

##### `add_task(title: str, description: str, priority: str)`
Add a new task to the manager.

**Parameters:**
- `title`: Task title
- `description`: Task description
- `priority`: Priority level ("high", "medium", "low")

##### `list_tasks()`
Display all tasks with their details.

##### `mark_task_complete(task_index: int)`
Mark a specific task as completed.

**Parameters:**
- `task_index`: Zero-based index of the task

##### `delete_task(task_index: int)`
Delete a task from the manager.

**Parameters:**
- `task_index`: Zero-based index of the task

##### `filter_tasks_by_priority(priority: str)`
Display tasks filtered by priority level.

**Parameters:**
- `priority`: Priority level to filter ("high", "medium", "low")

##### `search_tasks_by_keyword(keyword: str)`
Search and display tasks containing a keyword.

**Parameters:**
- `keyword`: Search term (case-insensitive)

### Complete Example

```python
from module_1.task_manager import TaskManager

def main():
    # Initialize the task manager
    manager = TaskManager()
    
    # Add various tasks
    manager.add_task("Complete project report", "Finalize Q4 project report", "high")
    manager.add_task("Team meeting", "Weekly sync with development team", "medium")
    manager.add_task("Code review", "Review pull requests from team members", "high")
    manager.add_task("Update documentation", "Update API documentation", "low")
    manager.add_task("Bug fix", "Fix login page bug", "high")
    
    print("=" * 60)
    print("TASK MANAGER - ALL TASKS")
    print("=" * 60)
    manager.list_tasks()
    
    print("\n" + "=" * 60)
    print("HIGH PRIORITY TASKS")
    print("=" * 60)
    manager.filter_tasks_by_priority("high")
    
    print("\n" + "=" * 60)
    print("COMPLETING TASKS")
    print("=" * 60)
    manager.mark_task_complete(0)  # Complete project report
    manager.mark_task_complete(2)  # Complete code review
    print("Marked 2 tasks as complete")
    
    print("\n" + "=" * 60)
    print("SEARCHING FOR 'BUG'")
    print("=" * 60)
    manager.search_tasks_by_keyword("bug")
    
    print("\n" + "=" * 60)
    print("DELETING COMPLETED TASKS")
    print("=" * 60)
    manager.delete_task(2)  # Delete code review task
    print("Deleted completed code review task")
    
    print("\n" + "=" * 60)
    print("FINAL TASK LIST")
    print("=" * 60)
    manager.list_tasks()

if __name__ == "__main__":
    main()
```

### Error Handling

The Task Manager handles common errors gracefully:

```python
manager = TaskManager()

# Attempting to complete a non-existent task
manager.mark_task_complete(10)  # Output: Invalid task index

# Attempting to delete a non-existent task
manager.delete_task(5)  # Output: Invalid task index
```

### Testing

The project includes comprehensive unit tests. Run tests using:

```bash
python -m unittest test_task_manager.py
```

Or for verbose output:

```bash
python -m unittest test_task_manager.py -v
```

**Test Coverage:**
- Task creation and addition
- Task listing and display
- Task completion
- Task deletion
- Priority filtering
- Keyword searching
- Edge cases and error scenarios

### Best Practices

1. **Priority Levels**: Use "high", "medium", or "low" for consistency
2. **Descriptive Titles**: Keep titles concise but descriptive
3. **Detailed Descriptions**: Provide enough context in descriptions
4. **Index Management**: Remember that task indices are zero-based
5. **Regular Cleanup**: Delete completed tasks to keep the list manageable

### Project Structure

```
hello-world/
├── module_1/
│   ├── __init__.py          # Package initialization
│   ├── task_manager.py      # Task Manager implementation
│   └── exercises.py         # Programming exercises
├── test_task_manager.py     # Unit tests
└── README.md                # This file
```

### Future Enhancements

Potential features for future versions:
- Task due dates and reminders
- Task categories and tags
- Persistent storage (JSON/database)
- Task sorting options
- Bulk operations
- Task priority editing
- Export/import functionality

### Contributing

This project was created as part of coursework at SEECS, NUST. Feel free to fork and modify for your own learning purposes.

### License

This project is for educational purposes.

---

*Documentation generated with GitHub Copilot - January 2026*
