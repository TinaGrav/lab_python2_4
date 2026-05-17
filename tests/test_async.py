import asyncio
import unittest
from typing import Protocol, runtime_checkable
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.class_task import Task
from src.async_executor.handlers import TaskHandlerProtocol, PrintHandler, PriorityHandler, FaultyHandler
from src.async_executor.executor import AsyncTaskExecutor


class TestContract(unittest.TestCase):

    def test_handlers_satisfy_contract(self):
        self.assertIsInstance(PrintHandler(), TaskHandlerProtocol)
        self.assertIsInstance(PriorityHandler(), TaskHandlerProtocol)
        self.assertIsInstance(FaultyHandler(), TaskHandlerProtocol)

    def test_bad_handler_fails_contract(self):
        class BadHandler:
            def process(self, task):
                pass

        self.assertNotIsInstance(BadHandler(), TaskHandlerProtocol)

    def test_issubclass_works(self):
        self.assertTrue(issubclass(PrintHandler, TaskHandlerProtocol))

        class BadHandler:
            pass

        self.assertFalse(issubclass(BadHandler, TaskHandlerProtocol))


class TestHandlers(unittest.TestCase):

    def test_print_handler_works(self):
        task = Task(id=1, payload="test", priority=3)
        asyncio.run(PrintHandler().handle(task))

    def test_priority_handler_respects_priority(self):
        handler = PriorityHandler()

        async def measure(task):
            start = asyncio.get_event_loop().time()
            await handler.handle(task)
            return asyncio.get_event_loop().time() - start

        time_1 = asyncio.run(measure(Task(id=1, payload="p1", priority=1)))
        time_5 = asyncio.run(measure(Task(id=2, payload="p5", priority=5)))
        self.assertLess(time_1, time_5)

    def test_faulty_handler_fails_every_second(self):
        handler = FaultyHandler()

        async def run():
            await handler.handle(Task(id=1, payload="p1"))
            with self.assertRaises(RuntimeError):
                await handler.handle(Task(id=2, payload="p2"))
            await handler.handle(Task(id=3, payload="p3"))

        asyncio.run(run())


class TestExecutor(unittest.TestCase):

    def test_create_with_bad_handler_raises_error(self):
        class BadHandler:
            pass

        with self.assertRaises(TypeError):
            AsyncTaskExecutor(handler=BadHandler())

    def test_submit_and_process_all_tasks(self):
        tasks = [Task(id=i, payload=f"task_{i}") for i in range(1, 6)]

        async def run():
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=2) as ex:
                for t in tasks:
                    await ex.submit(t)
            self.assertTrue(ex._queue.empty())

        asyncio.run(run())

    def test_parallel_is_faster_than_sequential(self):
        tasks = [Task(id=i, payload=f"task_{i}") for i in range(1, 6)]

        async def time_with_workers(n):
            start = asyncio.get_event_loop().time()
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=n) as ex:
                for t in tasks:
                    await ex.submit(t)
            return asyncio.get_event_loop().time() - start

        time_1 = asyncio.run(time_with_workers(1))
        time_3 = asyncio.run(time_with_workers(3))
        self.assertLess(time_3, time_1)

    def test_error_does_not_crash_executor(self):
        tasks = [
            Task(id=1, payload="p1"),
            Task(id=2, payload="p2"),
            Task(id=3, payload="p3"),
        ]

        async def run():
            async with AsyncTaskExecutor(handler=FaultyHandler(), workers=1) as ex:
                for t in tasks:
                    await ex.submit(t)

        asyncio.run(run())

    def test_workers_start_and_stop(self):
        async def run():
            executor = AsyncTaskExecutor(handler=PrintHandler(), workers=2)
            self.assertEqual(len(executor._worker_tasks), 0)

            async with executor as ex:
                self.assertEqual(len(ex._worker_tasks), 2)
                for wt in ex._worker_tasks:
                    self.assertFalse(wt.done())

            for wt in executor._worker_tasks:
                self.assertTrue(wt.done())

        asyncio.run(run())

    def test_custom_handler_works(self):
        class CustomHandler:
            def __init__(self):
                self.processed = []

            async def handle(self, task: Task) -> None:
                self.processed.append(task.id)
                await asyncio.sleep(0.05)

        handler = CustomHandler()

        async def run():
            async with AsyncTaskExecutor(handler=handler, workers=2) as ex:
                for i in range(3):
                    await ex.submit(Task(id=i, payload=f"p{i}"))

        asyncio.run(run())
        self.assertEqual(len(handler.processed), 3)
        self.assertEqual(sorted(handler.processed), [0, 1, 2])
