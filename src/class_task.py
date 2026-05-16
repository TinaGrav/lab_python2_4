from datetime import datetime
from descriptors import PriorityCheck, StatusCheck, DescriptionCheck, IsReadyCheck


class Task:
    priority = PriorityCheck()  # use descriptors for priority, status, payload and ready status
    status = StatusCheck()
    payload = DescriptionCheck()
    is_ready = IsReadyCheck()

    def __init__(self,
                 id: int,
                 payload: str,
                 priority: int = 3,
                 status: str = "uncompleted") -> None:
        self._id = id
        self.payload = payload
        self._creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.priority = priority
        self.status = status

    @property
    def id(self) -> int:   # read-only for id
        return self._id

    @id.setter
    def id(self, value: int) -> None:  # if you try to change id - error
        raise AttributeError("Sorry, but you can't change id")

    @property
    def created_at(self) -> str:  # read-only for creation_time
        return self._creation_time

    @created_at.setter
    def created_at(self, value: str) -> None:  # if you try to change ct - error
        raise AttributeError("Sorry, but you can't change creation time")

    def __str__(self) -> str:  # make readable string for print
        return (f"id: {self.id}, payload: {self.payload}, "
                f"time of creation: {self.created_at}, "
                f"priority: {self.priority}, status: {self.status}, "
                f"ready status: {self.is_ready}")





