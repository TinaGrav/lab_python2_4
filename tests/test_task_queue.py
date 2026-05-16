import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import unittest
from src.class_task import Task
from src.task_queue import TaskQueue, TaskIterator


class TestTaskIterator(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            Task(1, "Task 1", priority=1),
            Task(2, "Task 2", priority=2),
            Task(3, "Task 3", priority=3)
        ]
        self.iterator = TaskIterator(self.tasks)

    def test_iter_returns_self(self):
        self.assertIs(iter(self.iterator), self.iterator)

    def test_next_returns_tasks_in_order(self):
        self.assertEqual(next(self.iterator).id, 1)
        self.assertEqual(next(self.iterator).id, 2)
        self.assertEqual(next(self.iterator).id, 3)

    def test_stop_iteration_raised(self):
        for _ in range(3):
            next(self.iterator)
        with self.assertRaises(StopIteration):
            next(self.iterator)

    def test_multiple_iterators_independent(self):
        iter1 = TaskIterator(self.tasks)
        iter2 = TaskIterator(self.tasks)
        self.assertEqual(next(iter1).id, 1)
        self.assertEqual(next(iter1).id, 2)
        self.assertEqual(next(iter2).id, 1)


class TestTaskQueue(unittest.TestCase):
    def setUp(self):
        self.queue = TaskQueue()
        self.task1 = Task(1, "First task", priority=1, status="done")
        self.task2 = Task(2, "Second task", priority=2, status="uncompleted")
        self.task3 = Task(3, "Third task", priority=1, status="uncompleted")
        self.task4 = Task(4, "Fourth task", priority=3, status="done")

    def test_add_task(self):
        self.queue.add_task(self.task1)
        self.assertEqual(len(self.queue), 1)
        self.assertEqual(self.queue.tasks[0], self.task1)

    def test_add_multiple_tasks(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        self.queue.add_task(self.task3)
        self.assertEqual(len(self.queue), 3)

    def test_len(self):
        self.assertEqual(len(self.queue), 0)
        self.queue.add_task(self.task1)
        self.assertEqual(len(self.queue), 1)
        self.queue.add_task(self.task2)
        self.assertEqual(len(self.queue), 2)

    def test_last_with_tasks(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        self.assertEqual(self.queue.last(), self.task2)

    def test_last_with_one_task(self):
        self.queue.add_task(self.task1)
        self.assertEqual(self.queue.last(), self.task1)

    def test_iteration(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        self.queue.add_task(self.task3)
        tasks_ids = [task.id for task in self.queue]
        self.assertEqual(tasks_ids, [1, 2, 3])

    def test_multiple_iterations(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        first_pass = [task.id for task in self.queue]
        second_pass = [task.id for task in self.queue]
        self.assertEqual(first_pass, second_pass)

    def test_independent_iterators(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        iter1 = iter(self.queue)
        iter2 = iter(self.queue)
        self.assertEqual(next(iter1).id, 1)
        self.assertEqual(next(iter1).id, 2)
        self.assertEqual(next(iter2).id, 1)

    def test_filter_by_status(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        self.queue.add_task(self.task3)
        self.queue.add_task(self.task4)
        filtered = list(self.queue.filter(status="done"))
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].id, 1)
        self.assertEqual(filtered[1].id, 4)

    def test_filter_by_priority(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        self.queue.add_task(self.task3)
        self.queue.add_task(self.task4)
        filtered = list(self.queue.filter(priority=1))
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].id, 1)
        self.assertEqual(filtered[1].id, 3)

    def test_filter_by_status_and_priority(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        self.queue.add_task(self.task3)
        self.queue.add_task(self.task4)
        filtered = list(self.queue.filter(status="done", priority=1))
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].id, 1)

    def test_filter_with_no_params(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        filtered = list(self.queue.filter())
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].id, 1)
        self.assertEqual(filtered[1].id, 2)

    def test_filter_returns_generator(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        result = self.queue.filter(status="done")
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, '__next__'))
        self.assertNotIsInstance(result, list)

    def test_filter_with_empty_queue(self):
        filtered = list(self.queue.filter(status="done"))
        self.assertEqual(len(filtered), 0)

    def test_queue_works_with_list_comprehension(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        self.queue.add_task(self.task3)
        task_ids = [task.id for task in self.queue]
        self.assertEqual(task_ids, [1, 2, 3])

    def test_queue_works_with_sum_with_custom_key(self):
        self.queue.add_task(self.task1)
        self.queue.add_task(self.task2)
        self.queue.add_task(self.task3)
        total_ids = sum(task.id for task in self.queue)
        self.assertEqual(total_ids, 1 + 2 + 3)


if __name__ == '__main__':
    unittest.main()