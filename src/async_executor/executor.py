import asyncio
import logging
from typing import Protocol, runtime_checkable
from src.class_task import Task
from handlers import TaskHandlerProtocol


class AsyncTaskExecutor:

    def __init__(self, handler: TaskHandlerProtocol, workers: int = 2) -> None:
        if not isinstance(handler, TaskHandlerProtocol):  # если передали не асинхронный класс - ошибка
            raise TypeError(
                f"handler должен реализовывать TaskHandlerProtocol, "
                f"получен: {type(handler).__name__}"
            )

        self._handler = handler  # сохраняем обработчик
        self._workers_count = workers  # сколько воркеров запускать
        self._queue: asyncio.Queue[Task] = asyncio.Queue()  # асинхронная очередь
        self._worker_tasks: list[asyncio.Task] = []  # список с запущенными задачами
        self._logger = logging.getLogger(self.__class__.__name__)  # логгер

    async def __aenter__(self) -> "AsyncTaskExecutor":
        self._logger.info(   # логируем запуск
            f"Запуск исполнителя: {self._workers_count} воркеров, "
            f"обработчик: {type(self._handler).__name__}"
        )
        self._worker_tasks = [  # создаем воркеры
            asyncio.create_task(self._worker(worker_id=i))
            for i in range(self._workers_count)
        ]
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._queue.join()  # ждем обработку всех задач
        self._logger.info("Все задачи обработаны")

        for worker_task in self._worker_tasks:  # удаляем все воркеры
            worker_task.cancel()

        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._logger.info("Исполнитель остановлен")

    async def submit(self, task: Task) -> None:  # принимает Task
        self._logger.info(f"Задача id={task.id} добавлена в очередь")
        await self._queue.put(task)

    async def _worker(self, worker_id: int) -> None:
        worker_logger = logging.getLogger(f"worker-{worker_id}")
        worker_logger.info("Воркер запущен")  #  логирование запуска

        while True:
            task = await self._queue.get()  # ждет задачу
            try:
                worker_logger.info(f"Воркер взял задачу id={task.id}")
                await self._handler.handle(task)  # задача передается обработчику
            except Exception as e:  # обработка ошибок
                worker_logger.error(f"Ошибка при обработке задачи id={task.id}: {e}")
            finally:
                self._queue.task_done()

