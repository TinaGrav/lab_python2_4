from typing import Protocol, List, Dict, Any
from typing_extensions import runtime_checkable
from create_task import create_task


@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> List[Dict[str, Any]]:
        ...


def check_source(source):
    print(f"Checking source: {source.__class__.__name__}")
    if not isinstance(source, TaskSource):
        return "Mistake"
    try:
        tasks_dict = source.get_tasks()
    except Exception:
        return "Mistake"
    if not tasks_dict:
        return "No tasks"
    tasks = []
    for task_dict in tasks_dict:
        try:
            task = create_task(task_dict)
            tasks.append(task)
        except Exception:
            print("Mistake in creating tasks")
    for task in tasks:
        print(task)
    return True