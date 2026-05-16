def check_num(num):  # checks if number of tastks is correct
    try:
        num = int(num)
        if num <= 0:   # checks if number of tasks >0
            print("Mistake in number of tasks. Try ones more")
            new_num = input()
            return check_num(new_num)
        return num
    except ValueError:  # if number is not int
        print("Mistake in number of tasks. Try ones more")
        new_num = input()
        return check_num(new_num)


def check_id(id):   # checks if id is correct
    try:
        id = int(id)
        return id
    except ValueError:  # if id is not int
        print("Mistake in id. Try ones more")
        new_id = input()
        return check_id(new_id)


def check_payload(payload):  # checks if payload is correct
    if len(payload) < 1:
        print("Mistake in payload. Try ones more")
        new_payload = input()
        return check_payload(new_payload)
    else:
        return payload


class Input_source:
    def __init__(self):
        self.tasks = []

    def get_tasks(self):
        print("Write number of tasks: ")
        num_input = input()
        num_input = check_num(num_input)

        for i in range(num_input):  # create as tasks as needed
            print(f"Task {i+1}")
            print("Write id: ")
            id_input = input()
            id_input = check_id(id_input)  # asks for id

            print("Write payload: ")
            payload_input = input()
            payload_input = check_payload(payload_input)   # asks for payload
            self.tasks.append({"id": id_input, "payload": payload_input})  # add task to list
        return self.tasks


