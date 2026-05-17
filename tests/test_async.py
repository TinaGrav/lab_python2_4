import asyncio
import unittest
from typing import Protocol, runtime_checkable

from src.class_task import Task
from src.async import TaskHandlerProtocol, PrintHandler, PriorityHandler, FaultyHandler, AsyncTaskExecutor



def async_test(coro):
    """Декоратор для запуска асинхронного теста через asyncio.run."""
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))
    return wrapper


# ═══════════════════════════════════════════════
# Тесты контракта TaskHandlerProtocol
# ═══════════════════════════════════════════════

class TestTaskHandlerProtocol(unittest.TestCase):
    """Проверка поведенческого контракта (duck typing)."""

    def test_print_handler_satisfies_contract(self):
        """PrintHandler должен соответствовать контракту."""
        handler = PrintHandler()
        self.assertIsInstance(handler, TaskHandlerProtocol)

    def test_priority_handler_satisfies_contract(self):
        """PriorityHandler должен соответствовать контракту."""
        handler = PriorityHandler()
        self.assertIsInstance(handler, TaskHandlerProtocol)

    def test_faulty_handler_satisfies_contract(self):
        """FaultyHandler должен соответствовать контракту."""
        handler = FaultyHandler()
        self.assertIsInstance(handler, TaskHandlerProtocol)

    def test_class_without_handle_fails_contract(self):
        """Класс без метода handle НЕ должен соответствовать контракту."""
        class BadHandler:
            def process(self, task):
                pass

        handler = BadHandler()
        self.assertNotIsInstance(handler, TaskHandlerProtocol)

    def test_class_with_sync_handle_fails_contract(self):
        """Класс с синхронным handle НЕ должен соответствовать контракту."""
        class SyncHandler:
            def handle(self, task):
                pass

        handler = SyncHandler()
        self.assertNotIsInstance(handler, TaskHandlerProtocol)

    def test_class_with_async_handle_satisfies_contract(self):
        """Класс с async handle ДОЛЖЕН соответствовать контракту."""
        class GoodHandler:
            async def handle(self, task: Task) -> None:
                pass

        handler = GoodHandler()
        self.assertIsInstance(handler, TaskHandlerProtocol)

    def test_issubclass_works_with_protocol(self):
        """issubclass должен работать с runtime_checkable Protocol."""
        self.assertTrue(issubclass(PrintHandler, TaskHandlerProtocol))
        self.assertTrue(issubclass(PriorityHandler, TaskHandlerProtocol))
        self.assertTrue(issubclass(FaultyHandler, TaskHandlerProtocol))

        class BadHandler:
            pass

        self.assertFalse(issubclass(BadHandler, TaskHandlerProtocol))


# ═══════════════════════════════════════════════
# Тесты обработчиков
# ═══════════════════════════════════════════════

class TestPrintHandler(unittest.TestCase):
    """Тесты PrintHandler."""

    def setUp(self):
        self.handler = PrintHandler()

    def test_handle_returns_none(self):
        """handle должен отработать без ошибок и вернуть None."""
        task = Task(id=1, payload="test", priority=3)
        result = asyncio.run(self.handler.handle(task))
        self.assertIsNone(result)

    def test_handle_different_tasks(self):
        """handle должен принимать любые Task без исключений."""
        tasks = [
            Task(id=i, payload=f"task_{i}", priority=(i % 5) + 1)
            for i in range(1, 6)
        ]

        async def run_all():
            for task in tasks:
                await self.handler.handle(task)

        asyncio.run(run_all())  # не должно быть исключений


class TestPriorityHandler(unittest.TestCase):
    """Тесты PriorityHandler."""

    def setUp(self):
        self.handler = PriorityHandler()

    def test_handle_uses_priority(self):
        """Время обработки должно зависеть от приоритета."""
        task = Task(id=1, payload="test", priority=3)

        async def measure():
            start = asyncio.get_event_loop().time()
            await self.handler.handle(task)
            return asyncio.get_event_loop().time() - start

        elapsed = asyncio.run(measure())
        # priority=3, delay = 3 * 0.1 = 0.3с
        # Допускаем погрешность
        self.assertGreaterEqual(elapsed, 0.2)
        self.assertLessEqual(elapsed, 0.5)

    def test_high_priority_is_faster(self):
        """Приоритет 1 должен обрабатываться быстрее приоритета 5."""
        task_fast = Task(id=1, payload="fast", priority=1)
        task_slow = Task(id=2, payload="slow", priority=5)

        async def measure(task):
            start = asyncio.get_event_loop().time()
            await self.handler.handle(task)
            return asyncio.get_event_loop().time() - start

        fast_time = asyncio.run(measure(task_fast))
        slow_time = asyncio.run(measure(task_slow))

        self.assertLess(fast_time, slow_time)


class TestFaultyHandler(unittest.TestCase):
    """Тесты FaultyHandler."""

    def setUp(self):
        self.handler = FaultyHandler()

    def test_first_task_succeeds(self):
        """Первая задача должна обработаться успешно (нечётная)."""
        task = Task(id=1, payload="first")

        async def run():
            await self.handler.handle(task)

        asyncio.run(run())  # не должно быть исключений

    def test_second_task_fails(self):
        """Вторая задача должна упасть (чётная)."""
        task1 = Task(id=1, payload="first")
        task2 = Task(id=2, payload="second")

        async def run():
            await self.handler.handle(task1)  # успех (count=1)
            await self.handler.handle(task2)  # падает (count=2)

        with self.assertRaises(RuntimeError):
            asyncio.run(run())

    def test_pattern_success_fail_alternates(self):
        """Проверка чередования успех/ошибка/успех/ошибка."""

        async def run():
            handler = FaultyHandler()

            # Задача 1 — успех
            await handler.handle(Task(id=1, payload="p1"))

            # Задача 2 — ошибка
            with self.assertRaises(RuntimeError):
                await handler.handle(Task(id=2, payload="p2"))

            # Задача 3 — снова успех
            await handler.handle(Task(id=3, payload="p3"))

            # Задача 4 — снова ошибка
            with self.assertRaises(RuntimeError):
                await handler.handle(Task(id=4, payload="p4"))

        asyncio.run(run())


# ═══════════════════════════════════════════════
# Тесты AsyncTaskExecutor
# ═══════════════════════════════════════════════

class TestAsyncTaskExecutorConstruction(unittest.TestCase):
    """Тесты создания исполнителя."""

    def test_create_with_valid_handler(self):
        """Создание с обработчиком, соответствующим контракту."""
        executor = AsyncTaskExecutor(handler=PrintHandler(), workers=2)
        self.assertEqual(executor._workers_count, 2)
        self.assertIsInstance(executor._handler, PrintHandler)

    def test_create_with_default_workers(self):
        """По умолчанию должно быть 2 воркера."""
        executor = AsyncTaskExecutor(handler=PrintHandler())
        self.assertEqual(executor._workers_count, 2)

    def test_create_with_invalid_handler_raises_typeerror(self):
        """Создание с плохим обработчиком должно дать TypeError."""
        class BadHandler:
            pass

        with self.assertRaises(TypeError):
            AsyncTaskExecutor(handler=BadHandler())

    def test_create_with_custom_workers_count(self):
        """Проверка произвольного количества воркеров."""
        for n in [1, 3, 5]:
            executor = AsyncTaskExecutor(handler=PrintHandler(), workers=n)
            self.assertEqual(executor._workers_count, n)


class TestAsyncTaskExecutorSubmit(unittest.TestCase):
    """Тесты метода submit."""

    def test_submit_adds_task_to_queue(self):
        """После submit очередь не должна быть пустой."""
        async def run():
            task = Task(id=1, payload="test", priority=3)
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=1) as executor:
                await executor.submit(task)
                self.assertFalse(executor._queue.empty())

        asyncio.run(run())

    def test_submit_multiple_tasks(self):
        """Все задачи должны попасть в очередь."""
        async def run():
            tasks = [
                Task(id=i, payload=f"task_{i}", priority=(i % 5) + 1)
                for i in range(1, 6)
            ]
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=1) as executor:
                for task in tasks:
                    await executor.submit(task)
                self.assertEqual(executor._queue.qsize(), len(tasks))

        asyncio.run(run())


class TestAsyncTaskExecutorProcessing(unittest.TestCase):
    """Тесты обработки задач."""

    def test_single_task_processed(self):
        """Одна задача должна быть обработана без ошибок."""
        async def run():
            task = Task(id=1, payload="test", priority=3)
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=1) as executor:
                await executor.submit(task)
            # После выхода из async with все задачи гарантированно обработаны

        asyncio.run(run())  # не должно быть исключений

    def test_all_tasks_processed(self):
        """Все задачи должны быть обработаны."""
        async def run():
            tasks = [
                Task(id=i, payload=f"task_{i}", priority=(i % 5) + 1)
                for i in range(1, 6)
            ]
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=2) as executor:
                for task in tasks:
                    await executor.submit(task)
            # Если вышли без ошибок — queue.join() дождался всех task_done()

        asyncio.run(run())  # не должно быть исключений

    def test_parallel_processing_faster_than_sequential(self):
        """
        Параллельная обработка (3 воркера) должна быть быстрее,
        чем последовательная (1 воркер).
        """
        tasks = [
            Task(id=i, payload=f"task_{i}", priority=3)
            for i in range(1, 6)
        ]

        async def run_with_workers(n_workers):
            start = asyncio.get_event_loop().time()
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=n_workers) as ex:
                for t in tasks:
                    await ex.submit(t)
            return asyncio.get_event_loop().time() - start

        time_1 = asyncio.run(run_with_workers(1))
        time_3 = asyncio.run(run_with_workers(3))

        # 5 задач * 0.3с = 1.5с последовательно, 3 воркера ~0.6с
        self.assertLess(time_3, time_1)


class TestAsyncTaskExecutorErrorHandling(unittest.TestCase):
    """Тесты обработки ошибок (централизованная обработка)."""

    def test_executor_survives_handler_error(self):
        """
        Ошибка в обработчике НЕ должна ронять весь executor.
        Все последующие задачи должны быть обработаны.
        """
        async def run():
            tasks = [
                Task(id=1, payload="first"),
                Task(id=2, payload="second"),  # упадёт (чётная для FaultyHandler)
                Task(id=3, payload="third"),
            ]
            async with AsyncTaskExecutor(handler=FaultyHandler(), workers=1) as executor:
                for task in tasks:
                    await executor.submit(task)
            # Если вышли из async with без исключений — система выжила

        asyncio.run(run())  # не должно быть исключений

    def test_error_does_not_block_other_tasks(self):
        """
        Даже если одна задача упала, другие должны обработаться.
        """
        async def run():
            handler = FaultyHandler()
            processed = []

            # Оборачиваем handle, чтобы считать успешные обработки
            original_handle = handler.handle

            async def counting_handle(task):
                try:
                    await original_handle(task)
                    processed.append(task.id)
                except RuntimeError:
                    pass  # ошибки считаем отдельно, здесь не учитываем

            handler.handle = counting_handle

            tasks = [
                Task(id=1, payload="p1"),
                Task(id=2, payload="p2"),
                Task(id=3, payload="p3"),
                Task(id=4, payload="p4"),
            ]

            async with AsyncTaskExecutor(handler=handler, workers=1) as executor:
                for task in tasks:
                    await executor.submit(task)

            return processed

        processed = asyncio.run(run())
        # Задачи 1 и 3 должны быть обработаны успешно (нечётные)
        self.assertIn(1, processed)
        self.assertIn(3, processed)
        self.assertEqual(len(processed), 2)  # только нечётные не упали


class TestAsyncTaskExecutorContextManager(unittest.TestCase):
    """Тесты асинхронного контекстного менеджера."""

    def test_workers_started_on_enter(self):
        """При входе в async with воркеры должны запуститься."""
        async def run():
            executor = AsyncTaskExecutor(handler=PrintHandler(), workers=2)
            self.assertEqual(len(executor._worker_tasks), 0)  # до входа

            async with executor as ex:
                self.assertEqual(len(ex._worker_tasks), 2)  # после входа
                # Воркеры должны быть активны
                for worker_task in ex._worker_tasks:
                    self.assertFalse(worker_task.done())

        asyncio.run(run())

    def test_workers_stopped_on_exit(self):
        """При выходе из async with воркеры должны остановиться."""
        async def run():
            tasks = [
                Task(id=i, payload=f"task_{i}", priority=3)
                for i in range(1, 4)
            ]
            executor = AsyncTaskExecutor(handler=PrintHandler(), workers=2)

            async with executor as ex:
                for task in tasks:
                    await ex.submit(task)

            # После выхода все воркеры должны быть завершены
            for worker_task in executor._worker_tasks:
                self.assertTrue(worker_task.done())

        asyncio.run(run())

    def test_queue_empty_after_processing(self):
        """После выхода очередь должна быть пуста."""
        async def run():
            tasks = [
                Task(id=i, payload=f"task_{i}", priority=3)
                for i in range(1, 4)
            ]
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=2) as executor:
                for task in tasks:
                    await executor.submit(task)

            self.assertTrue(executor._queue.empty())

        asyncio.run(run())

    def test_exception_inside_context_still_calls_aexit(self):
        """
        Даже при исключении внутри async with,
        __aexit__ должен вызваться и остановить воркеров.
        """
        async def run():
            executor = AsyncTaskExecutor(handler=PrintHandler(), workers=1)

            with self.assertRaises(ValueError):
                async with executor:
                    raise ValueError("тестовое исключение")

            # Воркеры должны быть остановлены даже после исключения
            for worker_task in executor._worker_tasks:
                self.assertTrue(worker_task.done())

        asyncio.run(run())


class TestAsyncTaskExecutorExtensibility(unittest.TestCase):
    """Тесты расширяемости (разные обработчики)."""

    def test_custom_handler_works(self):
        """Произвольный обработчик с async handle должен работать."""
        async def run():
            class CustomHandler:
                def __init__(self):
                    self.processed = []

                async def handle(self, task: Task) -> None:
                    self.processed.append(task.id)
                    await asyncio.sleep(0.05)

            handler = CustomHandler()

            async with AsyncTaskExecutor(handler=handler, workers=2) as executor:
                for i in range(3):
                    await executor.submit(Task(id=i, payload=f"task_{i}"))

            return handler.processed

        processed = asyncio.run(run())
        self.assertEqual(len(processed), 3)
        self.assertEqual(sorted(processed), [0, 1, 2])

    def test_switch_handler_between_runs(self):
        """Разные запуски могут использовать разных обработчиков."""
        async def run():
            tasks = [Task(id=i, payload=f"p{i}") for i in range(2)]

            # Первый запуск с PrintHandler
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=1) as ex1:
                await ex1.submit(tasks[0])

            # Второй запуск с PriorityHandler
            async with AsyncTaskExecutor(handler=PriorityHandler(), workers=1) as ex2:
                await ex2.submit(tasks[1])

        asyncio.run(run())  # Оба должны отработать без ошибок


# ═══════════════════════════════════════════════
# Интеграционные тесты
# ═══════════════════════════════════════════════

class TestIntegration(unittest.TestCase):
    """Интеграционные тесты: полный цикл работы системы."""

    def test_full_cycle_with_all_handler_types(self):
        """Полный цикл с последовательным запуском разных обработчиков."""
        async def run():
            tasks = [
                Task(id=1, payload="task_1", priority=2),
                Task(id=2, payload="task_2", priority=4),
                Task(id=3, payload="task_3", priority=1),
            ]

            # PrintHandler
            async with AsyncTaskExecutor(handler=PrintHandler(), workers=2) as ex:
                for t in tasks:
                    await ex.submit(t)

            # PriorityHandler
            async with AsyncTaskExecutor(handler=PriorityHandler(), workers=3) as ex:
                for t in tasks:
                    await ex.submit(t)

            # FaultyHandler
            async with AsyncTaskExecutor(handler=FaultyHandler(), workers=1) as ex:
                for t in tasks:
                    await ex.submit(t)

        asyncio.run(run())  # Если дошли сюда — всё отработало

    def test_many_tasks_many_workers(self):
        """Стресс-тест: 20 задач, 5 воркеров."""
        async def run():
            tasks = [
                Task(id=i, payload=f"bulk_task_{i}", priority=(i % 5) + 1)
                for i in range(20)
            ]

            async with AsyncTaskExecutor(handler=PrintHandler(), workers=5) as ex:
                for t in tasks:
                    await ex.submit(t)

            self.assertTrue(ex._queue.empty())

        asyncio.run(run())


# ═══════════════════════════════════════════════
# Запуск тестов
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)