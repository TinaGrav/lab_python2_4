import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import unittest
from datetime import datetime
from src.class_task import Task

class TestTask(unittest.TestCase):

    def test_create_task_default_values(self):
        task = Task(1, "Test task")

        self.assertEqual(task.id, 1)
        self.assertEqual(task.payload, "Test task")
        self.assertEqual(task.priority, 3)
        self.assertEqual(task.status, "uncompleted")
        self.assertTrue(task.is_ready)
        self.assertIsNotNone(task.created_at)

    def test_create_task_with_custom_priority(self):
        task = Task(1, "Test task", priority=5)
        self.assertEqual(task.priority, 5)

    def test_create_task_with_custom_status(self):
        task = Task(1, "Test task", status="done")
        self.assertEqual(task.status, "done")
        self.assertFalse(task.is_ready)

    def test_change_priority_valid(self):
        task = Task(1, "Test task")
        task.priority = 2
        self.assertEqual(task.priority, 2)

    def test_change_priority_invalid_number(self):
        task = Task(1, "Test task")
        with self.assertRaises(ValueError) as context:
            task.priority = 10
        self.assertEqual(str(context.exception), "Wrong priority type")

    def test_change_priority_invalid_type(self):
        task = Task(1, "Test task")
        with self.assertRaises(ValueError) as context:
            task.priority = "abc"
        self.assertEqual(str(context.exception), "Wrong priority type")

    def test_change_status_valid(self):
        task = Task(1, "Test task")
        task.status = "done"
        self.assertEqual(task.status, "done")
        self.assertFalse(task.is_ready)

    def test_change_status_invalid_value(self):
        task = Task(1, "Test task")
        with self.assertRaises(ValueError) as context:
            task.status = "invalid_status"
        self.assertEqual(str(context.exception), "Wrong status")

    def test_change_status_invalid_type(self):
        task = Task(1, "Test task")
        with self.assertRaises(TypeError) as context:
            task.status = 123
        self.assertEqual(str(context.exception), "Wrong status type")

    def test_change_description_valid(self):
        task = Task(1, "Test task")
        task.payload = "New description"
        self.assertEqual(task.payload, "New description")

    def test_change_description_empty(self):
        task = Task(1, "Test task")
        with self.assertRaises(ValueError) as context:
            task.payload = ""
        self.assertEqual(str(context.exception), "Wrong description")

    def test_change_description_whitespace(self):
        task = Task(1, "Test task")
        with self.assertRaises(ValueError) as context:
            task.payload = "   "
        self.assertEqual(str(context.exception), "Wrong description")

    def test_change_description_invalid_type(self):
        task = Task(1, "Test task")
        with self.assertRaises(ValueError) as context:
            task.payload = 123
        self.assertEqual(str(context.exception), "Wrong description type")

    def test_cannot_change_id(self):
        task = Task(1, "Test task")
        with self.assertRaises(AttributeError) as context:
            task.id = 999
        self.assertEqual(str(context.exception), "Sorry, but you can't change id")

    def test_cannot_change_created_at(self):
        task = Task(1, "Test task")
        with self.assertRaises(AttributeError) as context:
            task.created_at = "2024-01-01"
        self.assertEqual(str(context.exception), "Sorry, but you can't change creation time")

    def test_is_ready_for_different_statuses(self):
        task = Task(1, "Test task")

        task.status = "uncompleted"
        self.assertTrue(task.is_ready)

        task.status = "in_progress"
        self.assertTrue(task.is_ready)

        task.status = "done"
        self.assertFalse(task.is_ready)

        task.status = "cancelled"
        self.assertFalse(task.is_ready)

    def test_str_representation(self):
        task = Task(1, "Test task", priority=4, status="in_progress")
        str_output = str(task)

        self.assertIn("id: 1", str_output)
        self.assertIn("payload: Test task", str_output)
        self.assertIn("priority: 4", str_output)
        self.assertIn("status: in_progress", str_output)
        self.assertIn("ready status: True", str_output)

    def test_multiple_tasks_independent(self):
        task1 = Task(1, "Task 1", priority=1, status="done")
        task2 = Task(2, "Task 2", priority=5, status="uncompleted")

        self.assertEqual(task1.priority, 1)
        self.assertEqual(task2.priority, 5)
        self.assertEqual(task1.status, "done")
        self.assertEqual(task2.status, "uncompleted")
        self.assertFalse(task1.is_ready)
        self.assertTrue(task2.is_ready)

        task1.priority = 3
        self.assertEqual(task1.priority, 3)
        self.assertEqual(task2.priority, 5)

    def test_creation_time_format(self):
        task = Task(1, "Test task")
        created = task.created_at

        parts = created.split()
        self.assertEqual(len(parts), 2)

        date_parts = parts[0].split("-")
        time_parts = parts[1].split(":")

        self.assertEqual(len(date_parts), 3)
        self.assertEqual(len(time_parts), 3)


if __name__ == "__main__":
    unittest.main()