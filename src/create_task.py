from class_task import Task


def create_task(input_inf: dict) -> Task:  # create Task from raw dict
    return Task(id=input_inf['id'],
                payload=input_inf['payload'])


