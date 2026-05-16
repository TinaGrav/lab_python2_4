import json


def file_input(file_name):
    with open(file_name, "r", encoding='utf-8') as f:  #open input file
        tasks = json.load(f)
    return tasks


class File_source:
    def __init__(self, input_file: str = "input_file.json"):  #use "input_file.txt" for creating tasks
        self.input_file = input_file

    def get_tasks(self):
        try:
            tasks = file_input(self.input_file)  #create tasks
        except FileNotFoundError:   #check if file exists
            return "Mistake: file not found"
        return tasks

