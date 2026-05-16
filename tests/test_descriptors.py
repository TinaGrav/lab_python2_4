import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import unittest
from src.class_task import Task


class TestPriorityDescriptor(unittest.TestCase):

   def test_priority_default_value(self):
      task = Task(1, "Test task")
      self.assertEqual(task.priority, 3)

   def test_priority_set_valid_value(self):
      task = Task(1, "Test task")
      task.priority = 1
      self.assertEqual(task.priority, 1)

      task.priority = 5
      self.assertEqual(task.priority, 5)

      task.priority = 3
      self.assertEqual(task.priority, 3)

   def test_priority_set_invalid_number_low(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.priority = 0
      self.assertEqual(str(context.exception), "Wrong priority type")

   def test_priority_set_invalid_number_high(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.priority = 6
      self.assertEqual(str(context.exception), "Wrong priority type")

   def test_priority_set_string_number(self):
      task = Task(1, "Test task")
      task.priority = "4"
      self.assertEqual(task.priority, 4)

   def test_priority_set_invalid_string(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.priority = "hello"
      self.assertEqual(str(context.exception), "Wrong priority type")

   def test_priority_set_float(self):
      task = Task(1, "Test task")
      task.priority = 3.7
      self.assertEqual(task.priority, 3)

   def test_priority_multiple_tasks_independent(self):
      task1 = Task(1, "Task 1", priority=1)
      task2 = Task(2, "Task 2", priority=5)

      self.assertEqual(task1.priority, 1)
      self.assertEqual(task2.priority, 5)

      task1.priority = 3
      self.assertEqual(task1.priority, 3)
      self.assertEqual(task2.priority, 5)


class TestStatusDescriptor(unittest.TestCase):

   def test_status_default_value(self):
      task = Task(1, "Test task")
      self.assertEqual(task.status, "uncompleted")

   def test_status_set_valid_values(self):
      task = Task(1, "Test task")

      task.status = "in_progress"
      self.assertEqual(task.status, "in_progress")

      task.status = "done"
      self.assertEqual(task.status, "done")

      task.status = "cancelled"
      self.assertEqual(task.status, "cancelled")

      task.status = "uncompleted"
      self.assertEqual(task.status, "uncompleted")


   def test_status_set_invalid_value(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.status = "invalid"
      self.assertEqual(str(context.exception), "Wrong status")

   def test_status_set_empty_string(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.status = ""
      self.assertEqual(str(context.exception), "Wrong status")

   def test_status_set_invalid_type(self):
      task = Task(1, "Test task")
      with self.assertRaises(TypeError) as context:
         task.status = 123
      self.assertEqual(str(context.exception), "Wrong status type")

   def test_status_set_list(self):
      task = Task(1, "Test task")
      with self.assertRaises(TypeError) as context:
         task.status = ["done"]
      self.assertEqual(str(context.exception), "Wrong status type")

   def test_status_multiple_tasks_independent(self):
      task1 = Task(1, "Task 1", status="uncompleted")
      task2 = Task(2, "Task 2", status="done")

      self.assertEqual(task1.status, "uncompleted")
      self.assertEqual(task2.status, "done")

      task1.status = "in_progress"
      self.assertEqual(task1.status, "in_progress")
      self.assertEqual(task2.status, "done")


class TestDescriptionDescriptor(unittest.TestCase):

   def test_description_default_value(self):
      task = Task(1, "Test task")
      self.assertEqual(task.payload, "Test task")

   def test_description_set_valid_value(self):
      task = Task(1, "Test task")
      task.payload = "New description"
      self.assertEqual(task.payload, "New description")

   def test_description_set_empty_string(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.payload = ""
      self.assertEqual(str(context.exception), "Wrong description")

   def test_description_set_whitespace_only(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.payload = "   "
      self.assertEqual(str(context.exception), "Wrong description")

   def test_description_set_whitespace_around(self):
      task = Task(1, "Test task")
      task.payload = "  new description  "
      self.assertEqual(task.payload, "  new description  ")

   def test_description_set_invalid_type_int(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.payload = 123
      self.assertEqual(str(context.exception), "Wrong description type")

   def test_description_set_invalid_type_list(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.payload = ["description"]
      self.assertEqual(str(context.exception), "Wrong description type")

   def test_description_set_invalid_type_none(self):
      task = Task(1, "Test task")
      with self.assertRaises(ValueError) as context:
         task.payload = None
      self.assertEqual(str(context.exception), "Wrong description type")

   def test_description_long_text(self):
      long_text = "A" * 1000
      task = Task(1, long_text)
      self.assertEqual(task.payload, long_text)

      task.payload = "B" * 500
      self.assertEqual(task.payload, "B" * 500)

   def test_description_multiple_tasks_independent(self):
      task1 = Task(1, "Description 1")
      task2 = Task(2, "Description 2")

      self.assertEqual(task1.payload, "Description 1")
      self.assertEqual(task2.payload, "Description 2")

      task1.payload = "Changed"
      self.assertEqual(task1.payload, "Changed")
      self.assertEqual(task2.payload, "Description 2")


class TestIsReadyDescriptor(unittest.TestCase):

   def test_is_ready_default(self):
      task = Task(1, "Test task")
      self.assertTrue(task.is_ready)

   def test_is_ready_when_uncompleted(self):
      task = Task(1, "Test task", status="uncompleted")
      self.assertTrue(task.is_ready)

   def test_is_ready_when_in_progress(self):
      task = Task(1, "Test task", status="in_progress")
      self.assertTrue(task.is_ready)

   def test_is_ready_when_done(self):
      task = Task(1, "Test task", status="done")
      self.assertFalse(task.is_ready)

   def test_is_ready_when_cancelled(self):
      task = Task(1, "Test task", status="cancelled")
      self.assertFalse(task.is_ready)

   def test_is_ready_updates_with_status_change(self):
      task = Task(1, "Test task", status="uncompleted")
      self.assertTrue(task.is_ready)

      task.status = "in_progress"
      self.assertTrue(task.is_ready)

      task.status = "done"
      self.assertFalse(task.is_ready)

      task.status = "uncompleted"
      self.assertTrue(task.is_ready)

   def test_is_ready_non_data_descriptor_can_be_overridden(self):
      task = Task(1, "Test task", status="done")
      self.assertFalse(task.is_ready)

      task.is_ready = "manual override"
      self.assertEqual(task.is_ready, "manual override")

      del task.is_ready
      self.assertFalse(task.is_ready)

   def test_is_ready_different_tasks_independent(self):
      task1 = Task(1, "Task 1", status="done")
      task2 = Task(2, "Task 2", status="uncompleted")

      self.assertFalse(task1.is_ready)
      self.assertTrue(task2.is_ready)

      task1.status = "uncompleted"
      task2.status = "done"

      self.assertTrue(task1.is_ready)
      self.assertFalse(task2.is_ready)



if __name__ == "__main__":
   unittest.main()
