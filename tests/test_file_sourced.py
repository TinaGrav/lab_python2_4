import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.file_sourced import File_source
import unittest
class TestFileSource:
   def test_get_tasks_success(self):
      source = File_source("test_file.json")
      tasks = source.get_tasks()
      assert type(tasks) == list
      assert len(tasks) == 2
      assert tasks[0]["id"] == 1
      assert tasks[0]["payload"] == "Задача 1"

   def test_get_tasks_file_not_found(self):
      source = File_source("not_exist.json")
      result = source.get_tasks()
      assert result == "Mistake: file not found"

   def test_get_tasks_returns_list_of_dicts(self):
      source = File_source("test_file.json")
      tasks = source.get_tasks()

      for task in tasks:
         assert "id" in task
         assert "payload" in task

   def test_get_tasks_called_twice(self):
      source = File_source("test_file.json")
      tasks1 = source.get_tasks()
      tasks2 = source.get_tasks()
      assert tasks1 == tasks2