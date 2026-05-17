import random
def generate_tasks(file):
    num = random.randint(1, 10)  # random number of generating tasks
    tasks = []
    with open(file, "r", encoding='utf-8') as file:
        lines = file.read().splitlines()
    for i in range(num):      #create as many tasks as needed
        task_id = random.randint(1, 100)    #create random id
        task_description = random.choice(lines)  #use random task description
        tasks.append({"id": task_id, "payload": task_description})  #add created task to list
    return tasks

class Generator_source:
    def __init__(self, descriptions_file: str = "describ_list.txt"):
        self.descriptions_file = descriptions_file

    def get_tasks(self):
        tasks = generate_tasks(self.descriptions_file)
        return tasks

