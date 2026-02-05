class TodoManager:
    def __init__(self):
        self.tasks = []
        self.task_id_counter = 1
    
    def add_task(self, title, description=""):
        """Add a new task to the list."""
        task = {
            "id": self.task_id_counter,
            "title": title,
            "description": description,
            "completed": False
        }
        self.tasks.append(task)
        self.task_id_counter += 1
        return task
    
    def mark_complete(self, task_id):
        """Mark a task as complete."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                return task
        return None
    
    def delete_task(self, task_id):
        """Delete a task by ID."""
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
    
    def list_all_tasks(self):
        """Return all tasks."""
        return self.tasks
    
    def filter_by_status(self, completed=False):
        """Filter tasks by completion status."""
        return [task for task in self.tasks if task["completed"] == completed]


# Example usage
if __name__ == "__main__":
    manager = TodoManager()
    
    manager.add_task("Buy groceries", "Milk, bread, eggs")
    manager.add_task("Write report", "Quarterly report due Friday")
    manager.add_task("Call dentist")
    
    print("All tasks:", manager.list_all_tasks())
    print("\nPending tasks:", manager.filter_by_status(completed=False))
    
    manager.mark_complete(1)
    print("\nCompleted tasks:", manager.filter_by_status(completed=True))
    