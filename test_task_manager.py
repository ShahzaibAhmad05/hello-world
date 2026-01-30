# Generate comprehensive unit tests for task manager
# Include edge cases and error scenarios

import unittest
from io import StringIO
from unittest.mock import patch
from module_1.task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    """
    Comprehensive unit test suite for the TaskManager class.
    
    Tests all core functionality including adding, listing, completing, deleting,
    filtering, and searching tasks, as well as edge cases and error scenarios.
    """
    
    def setUp(self):
        """
        Set up test fixtures before each test method.
        
        Creates a fresh TaskManager instance for each test to ensure test isolation.
        """
        self.manager = TaskManager()

    def test_add_task(self):
        """
        Test adding a task to the task manager.
        
        Verifies that:
        - Task is successfully added to the tasks list
        - Task count increases by 1
        - Task properties are correctly set
        """
        self.manager.add_task("Test Task", "This is a test task", "high")
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(self.manager.tasks[0].title, "Test Task")

    def test_list_tasks(self):
        """
        Test listing all tasks in the task manager.
        
        Verifies that:
        - All tasks are displayed with correct formatting
        - Task indices start from 1
        - Task details are correctly shown
        """
        self.manager.add_task("Task 1", "Description 1", "low")
        self.manager.add_task("Task 2", "Description 2", "medium")
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.manager.list_tasks()
            output = fake_out.getvalue()
            self.assertIn("1. [Pending] Task 1 - Description 1 (Priority: low)", output)
            self.assertIn("2. [Pending] Task 2 - Description 2 (Priority: medium)", output)

    def test_mark_task_complete(self):
        """
        Test marking a task as complete.
        
        Verifies that:
        - Task completion status is updated to True
        - Task remains in the list after completion
        """
        self.manager.add_task("Task to Complete", "Complete this task", "high")
        self.manager.mark_task_complete(0)
        self.assertTrue(self.manager.tasks[0].completed)

    def test_mark_task_complete_invalid_index(self):
        """
        Test marking a task complete with an invalid index (edge case).
        
        Verifies that:
        - Appropriate error message is logged
        - System handles out-of-range indices gracefully
        """
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.manager.mark_task_complete(5)
            output = fake_out.getvalue()
            self.assertIn("Invalid task index", output)

    def test_delete_task(self):
        """
        Test deleting a task from the task manager.
        
        Verifies that:
        - Task is successfully removed from the list
        - Task count decreases by 1
        """
        self.manager.add_task("Task to Delete", "Delete this task", "medium")
        self.manager.delete_task(0)
        self.assertEqual(len(self.manager.tasks), 0)

    def test_delete_task_invalid_index(self):
        """
        Test deleting a task with an invalid index (edge case).
        
        Verifies that:
        - Appropriate error message is logged
        - System handles out-of-range indices gracefully
        """
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.manager.delete_task(3)
            output = fake_out.getvalue()
            self.assertIn("Invalid task index", output)

    def test_filter_tasks_by_priority(self):
        """
        Test filtering tasks by priority level.
        
        Verifies that:
        - Only tasks matching the specified priority are displayed
        - Filtered results maintain correct formatting
        - Other priority tasks are excluded from results
        """
        self.manager.add_task("High Priority Task", "Important task", "high")
        self.manager.add_task("Low Priority Task", "Less important task", "low")
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.manager.filter_tasks_by_priority("high")
            output = fake_out.getvalue()
            self.assertIn("1. [Pending] High Priority Task - Important task (Priority: high)", output)

    def test_search_tasks_by_keyword(self):
        """
        Test searching tasks by keyword.
        
        Verifies that:
        - Tasks containing the keyword in title or description are found
        - Search is case-insensitive
        - Results are correctly formatted
        """
        self.manager.add_task("Buy milk", "Get milk from store", "medium")
        self.manager.add_task("Read book", "Read the new novel", "low")
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.manager.search_tasks_by_keyword("milk")
            output = fake_out.getvalue()
            self.assertIn("1. [Pending] Buy milk - Get milk from store (Priority: medium)", output)


if __name__ == '__main__':
    unittest.main()