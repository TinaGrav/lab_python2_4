from file_sourced import File_source
from generator import Generator_source
from input_source import Input_source
from check_sources import check_source
from create_task import create_task
from task_queue import TaskQueue


def choose_option():
    try:
        opt = int(input())
        if 1 <= opt <= 5:
            return opt
        else:
            print("Mistake. Try again")
            return choose_option()
    except ValueError:
        print("Mistake. Try again")
        return choose_option()


def user_part():
    print("Hello! Here you can check how sources work.")
    print("How do you want to create tasks?")
    print("You can create them from file(1), generate them(2), write by yourself(3), "
          "change smth about the last task, filter tasks(5) or exit(6)")
    queue = TaskQueue()
    while True:
        print("Write in option you prefer: 1, 2, 3, 4, 5 or 6: ")
        opt = choose_option()
        if opt == 1:  # create tasks from file source
            print("Now tasks are created from 'input_file.json'. You can change tasks by changing the file")
            file_source = File_source("input_file.json")
            for task in file_source.get_tasks():
                task = create_task(task)
                queue.add_task(task)

        elif opt == 2:  # create tasks from generator
            print("Now descriptions of the tasks are generated from tasks in file 'describ_list.txt'. "
                  "You can change tasks by changing the file")
            generator = Generator_source()
            for task in generator.get_tasks():
                task = create_task(task)
                queue.add_task(task)

        elif opt == 3:  # create tasks from input source
            print("Here you need to create tasks by yourself")
            inputed = Input_source()
            for task in inputed.get_tasks():
                task = create_task(task)
                queue.add_task(task)

        elif opt == 4:
            if queue:
                task = queue.last()
                print(task)
                print("What do you want to change about this task?")
                print("Write id(1), payload(2), priority(3), status(4), creation time(5) or ready status(6):")
                opt = choose_option()
                if opt == 1:
                    task.id = 0
                elif opt == 2:
                    print("Write new payload:")
                    task.payload = input()
                elif opt == 3:
                    print("Write new priority:")
                    task.priority = input()
                elif opt == 4:
                    print("Write new status:")
                    task.status = input()
                elif opt == 5:
                    task.created_at = 0
                else:
                    print("Ready status is updated")
                    if task.is_ready:
                        print("Task is ready to go")
                    else:
                        print("Task is not ready to go")
            else:
                print("Task list is empty, there is nothing to change")

        elif opt == 5:
            if queue:
                while True:
                    print("Do you want to filter tasks by status(1), priority(2) or both(3)?")
                    filt = int(input())
                    if 1 <= filt <= 3:
                        if filt == 1:
                            print("Write status to filter with: uncompleted, in_progress, done or cancelled")
                            status = input()
                            for task in queue.filter(status=status):
                                print(task)
                            break
                        elif filt == 2:
                            print("Write status to filter with: 1, 2, 3, 4 or 5")
                            priority = int(input())
                            for task in queue.filter(priority=priority):
                                print(task)
                            break
                        elif filt == 3:
                            print("Write status to filter with: uncompleted, in_progress, done or cancelled")
                            status = input()
                            print("Write status to filter with: 1, 2, 3, 4 or 5")
                            priority = int(input())
                            for task in queue.filter(status=status, priority=priority):
                                print(task)
                            break
                    else:
                        print("Wrong value for filter. Try again")
            else:
                print("Task list is empty, there is nothing to filter")

        elif opt == 6:
            print("Goodbye! Have a good time!")
            break