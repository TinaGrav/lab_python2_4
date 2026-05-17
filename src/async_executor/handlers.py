import asyncio
import logging
from typing import Protocol, runtime_checkable
from class_task import Task

logging.basicConfig(   # настройка логирования
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("async_executor")


@runtime_checkable
class TaskHandlerProtocol(Protocol):
    async def handle(self, task: Task) -> None:
        ...


class PrintHandler:   # логирование начала обработки
    async def handle(self, task: Task) -> None:
        logger.info(f"[PrintHandler] Начинаю обработку задачи id={task.id}: '{task.payload}'")
        await asyncio.sleep(0.3)
        logger.info(f"[PrintHandler] Задача id={task.id} выполнена")


class PriorityHandler:  # вычисление времени обработки в зависимости от приоритета: чем выше приоритет,
    # тем быстрее обрабатывается задача

    async def handle(self, task: Task) -> None:
        delay = task.priority * 0.1
        logger.info(
            f"[PriorityHandler] Задача id={task.id} (приоритет={task.priority}), "
            f"время обработки: {delay:.1f}с"
        )
        await asyncio.sleep(delay)
        logger.info(f"[PriorityHandler] Задача id={task.id} завершена")


class FaultyHandler:  # имитация ошибок для демонстрации центролизованной обработки ошибок

    def __init__(self) -> None:
        self._count = 0

    async def handle(self, task: Task) -> None:
        self._count += 1
        if self._count % 2 == 0:
            raise RuntimeError(f"Имитация ошибки")
        logger.info(f"[FaultyHandler] Задача id={task.id} успешно обработана")
        await asyncio.sleep(0.2)
