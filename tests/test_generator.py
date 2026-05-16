import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.generator import Generator_source
import unittest
class TestGeneratorSource(unittest.TestCase):
    def test_generator_creates_object(self):
        source = Generator_source()
        self.assertIsNotNone(source)

    def test_generator_has_get_tasks_method(self):
        source = Generator_source()
        self.assertTrue(hasattr(source, 'get_tasks'))
        self.assertTrue(callable(source.get_tasks))

    def test_get_tasks_returns_list(self):
        source = Generator_source()
        tasks = source.get_tasks()
        self.assertIsInstance(tasks, list)

    def test_tasks_have_correct_structure(self):
        source = Generator_source()
        tasks = source.get_tasks()

        if tasks:
            task = tasks[0]
            self.assertIn("id", task)
            self.assertIn("payload", task)
            self.assertIsInstance(task["id"], int)
            self.assertIsInstance(task["payload"], str)

    def test_generator_file_not_found_raises_error(self):
        source = Generator_source("not_exist.txt")
        with self.assertRaises(FileNotFoundError):
            source.get_tasks()

    def test_generator_accepts_custom_file(self):
        source = Generator_source("custom_file.txt")
        self.assertEqual(source.descriptions_file, "custom_file.txt")

    def test_generator_default_file(self):
        source = Generator_source()
        self.assertEqual(source.descriptions_file, "describ_list.txt")