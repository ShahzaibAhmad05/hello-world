# Task Manager Application
# Features:
# 1. Add task with title, description, priority (high/medium/low)
# 2. List all tasks
# 3. Mark task as complete
# 4. Delete task
# 5. Filter tasks by priority
# 6. Search tasks by keyword

class Task:
    """
    Represents a single task with title, description, priority, and completion status.
    
    Attributes:
        title (str): The title of the task.
        description (str): A detailed description of the task.
        priority (str): The priority level of the task (high/medium/low).
        completed (bool): Indicates whether the task has been completed.
    """
    
    def __init__(self, title: str, description: str, priority: str):
        """
        Initialize a new Task instance.
        
        Args:
            title (str): The title of the task.
            description (str): A detailed description of the task.
            priority (str): The priority level (high/medium/low).
        """
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = False

    def mark_complete(self):
        """
        Mark the task as completed.
        
        Sets the completed attribute to True to indicate task completion.
        """
        self.completed = True

    def __str__(self):
        """
        Return a string representation of the task.
        
        Returns:
            str: A formatted string showing the task's status, title, description, and priority.
        """
        status = "Completed" if self.completed else "Pending"
        return f"[{status}] {self.title} - {self.description} (Priority: {self.priority})"

class TaskManager:
    """
    Manages a collection of tasks with various operations.
    
    Provides functionality to add, list, complete, delete, filter, and search tasks.
    
    Attributes:
        tasks (list): A list of Task objects managed by this TaskManager.
    """
    
    def __init__(self):
        """
        Initialize a new TaskManager instance with an empty task list.
        """
        self.tasks = []

    def add_task(self, title: str, description: str, priority: str):
        """
        Add a new task to the task manager.
        
        Creates a new Task object with the provided information and appends it
        to the tasks list.
        
        Args:
            title (str): The title of the task.
            description (str): A detailed description of the task.
            priority (str): The priority level (high/medium/low).
        """
        task = Task(title, description, priority)
        self.tasks.append(task)

    def list_tasks(self):
        """
        Display all tasks in the task manager.
        
        Prints each task with its index number (starting from 1) and full details
        including status, title, description, and priority.
        """
        for idx, task in enumerate(self.tasks, start=1):
            print(f"{idx}. {task}")

    def mark_task_complete(self, task_index: int):
        """
        Mark a specific task as completed.
        
        Args:
            task_index (int): The zero-based index of the task to mark as complete.
        
        Note:
            Prints an error message if the provided index is out of range.
        """
        # Validate task index is within valid range
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index].mark_complete()
        else:
            print("Invalid task index")

    def delete_task(self, task_index: int):
        """
        Delete a task from the task manager.
        
        Args:
            task_index (int): The zero-based index of the task to delete.
        
        Note:
            Prints an error message if the provided index is out of range.
        """
        # Validate task index before deletion
        if 0 <= task_index < len(self.tasks):
            del self.tasks[task_index]
        else:
            print("Invalid task index")

    def filter_tasks_by_priority(self, priority: str):
        """
        Display tasks filtered by a specific priority level.
        
        Uses list comprehension to filter tasks matching the specified priority
        and displays them with their index numbers.
        
        Args:
            priority (str): The priority level to filter by (high/medium/low).
        """
        # List comprehension to filter tasks by priority
        filtered_tasks = [task for task in self.tasks if task.priority == priority]
        for idx, task in enumerate(filtered_tasks, start=1):
            print(f"{idx}. {task}")

    def search_tasks_by_keyword(self, keyword: str):
        """
        Search and display tasks containing a specific keyword.
        
        Performs case-insensitive search in both task title and description.
        Uses list comprehension to find matching tasks.
        
        Args:
            keyword (str): The keyword to search for in task titles and descriptions.
        """
        # List comprehension with case-insensitive search in title and description
        searched_tasks = [task for task in self.tasks if keyword.lower() in task.title.lower() or keyword.lower() in task.description.lower()]
        for idx, task in enumerate(searched_tasks, start=1):
            print(f"{idx}. {task}")


if __name__ == "__main__":
    manager = TaskManager()
    manager.add_task("Buy groceries", "Milk, Bread, Eggs", "high")
    manager.add_task("Read book", "Finish reading '1984'", "medium")
    manager.add_task("Exercise", "Go for a 30-minute run", "low")

    print("All Tasks:")
    manager.list_tasks()

    print("\nMarking first task as complete...")
    manager.mark_task_complete(0)
    manager.list_tasks()

    print("\nFiltering tasks by priority 'medium':")
    manager.filter_tasks_by_priority("medium")

    print("\nSearching tasks with keyword 'read':")
    manager.search_tasks_by_keyword("read")

    print("\nDeleting second task...")
    manager.delete_task(1)
    manager.list_tasks()
    