class PriorityCheck:
    def __set_name__(self, owner, priority):  # set name for priority
        self.name = f"_{priority}"

    def __get__(self, task, owner):  # get priority from task
        return getattr(task, self.name, 3)     # priority is 3 when task created

    def __set__(self, task, value):  # set a new priority
        try:
            value = int(value)  # check if value is int
            if (1 <= value <= 5):  # check if value is 1-5
                setattr(task, self.name, value)
            else:
                raise ValueError("Wrong priority number")
        except ValueError:
            raise ValueError("Wrong priority type")


class StatusCheck:
    def __set_name__(self, owner, status):  # set name for priority
        self.name = f"_{status}"

    def __get__(self, task, owner):  # get priority from task
        return getattr(task, self.name, "uncompleted")  # status is uncompleted when task created

    def __set__(self, task, value):  # set a new status
        valid_statuses = ["uncompleted", "in_progress", "done", "cancelled"]  # list of statuses
        if isinstance(value, str):  # checks if status is str
            if value in valid_statuses:  # checks if status in list
                setattr(task, self.name, value)
            else:
                raise ValueError("Wrong status")
        else:
            raise TypeError("Wrong status type")


class DescriptionCheck:
    def __set_name__(self, owner, description):  # set name for description
        self.name = f"_{description}"

    def __get__(self, task, owner):  # get ready status from task
        return getattr(task, self.name, "")

    def __set__(self, task, value):  # set a new description
        if isinstance(value, str):  # check if description is str
            if len(value.strip()) > 0:  # check if description is not empty
                setattr(task, self.name, value)
            else:
                raise ValueError("Wrong description")
        else:
            raise ValueError("Wrong description type")


class IsReadyCheck:
    def __set_name__(self, owner, name):  # set name for is_ready
        self.name = name

    def __get__(self, obj, owner):  # return True if statuses are not done/cancelled
        return obj.status not in ('done', 'cancelled')
