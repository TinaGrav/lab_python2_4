import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from unittest.mock import patch
from src.input_source import Input_source, check_num, check_id, check_payload


class TestCheckNum(unittest.TestCase):
    def test_valid_number(self):
        result = check_num("5")
        self.assertEqual(result, 5)

    @patch('builtins.input')
    def test_invalid_then_valid(self, mock_input):
        mock_input.return_value = "3"
        result = check_num("abc")
        self.assertEqual(result, 3)


class TestCheckId(unittest.TestCase):
    def test_valid_id(self):
        result = check_id("10")
        self.assertEqual(result, 10)

    @patch('builtins.input')
    def test_invalid_then_valid(self, mock_input):
        mock_input.return_value = "7"
        result = check_id("abc")
        self.assertEqual(result, 7)


class TestCheckPayload(unittest.TestCase):
    def test_valid_payload(self):
        result = check_payload("Test1")
        self.assertEqual(result, "Test1")

    @patch('builtins.input')
    def test_empty_then_valid(self, mock_input):
        mock_input.return_value = "Test2"
        result = check_payload("")
        self.assertEqual(result, "Test2")

    def test_payload_with_spaces(self):
        result = check_payload("  Test3  ")
        self.assertEqual(result, "  Test3  ")


class TestInputSource(unittest.TestCase):
    def test_create_object(self):
        source = Input_source()
        self.assertIsNotNone(source)
        self.assertEqual(source.tasks, [])

    def test_has_get_tasks_method(self):
        source = Input_source()
        self.assertTrue(hasattr(source, 'get_tasks'))

    @patch('builtins.input')
    def test_get_tasks_one_task(self, mock_input):
        mock_input.side_effect = ["1", "1", "Test"]
        source = Input_source()
        tasks = source.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[0]["payload"], "Test")

    @patch('builtins.input')
    def test_get_tasks_two_tasks(self, mock_input):
        mock_input.side_effect = ["2", "1", "Test1", "2", "Test2"]
        source = Input_source()
        tasks = source.get_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[0]["payload"], "Test1")
        self.assertEqual(tasks[1]["id"], 2)
        self.assertEqual(tasks[1]["payload"], "Test2")

    @patch('builtins.input')
    def test_get_tasks_returns_list(self, mock_input):
        mock_input.side_effect = ["1", "1", "Test"]
        source = Input_source()
        tasks = source.get_tasks()
        self.assertIsInstance(tasks, list)

    @patch('builtins.input')
    def test_get_tasks_task_has_id_and_payload(self, mock_input):
        mock_input.side_effect = ["1", "5", "Test"]
        source = Input_source()
        tasks = source.get_tasks()
        self.assertIn("id", tasks[0])
        self.assertIn("payload", tasks[0])

    @patch('builtins.input')
    def test_get_tasks_id_is_int(self, mock_input):
        mock_input.side_effect = ["1", "42", "Test"]
        source = Input_source()
        tasks = source.get_tasks()
        self.assertIsInstance(tasks[0]["id"], int)
        self.assertEqual(tasks[0]["id"], 42)

    @patch('builtins.input')
    def test_get_tasks_payload_is_string(self, mock_input):
        mock_input.side_effect = ["1", "1", "Test"]
        source = Input_source()
        tasks = source.get_tasks()
        self.assertIsInstance(tasks[0]["payload"], str)

    @patch('builtins.input')
    def test_get_tasks_saves_to_self_tasks(self, mock_input):
        mock_input.side_effect = ["1", "1", "Test"]
        source = Input_source()
        tasks = source.get_tasks()
        self.assertEqual(source.tasks, tasks)

