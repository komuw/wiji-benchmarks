import random
import string
import threading

import tasks

# Usage:
#  python benchmarks/task_producer.py


max_tasks_to_queue: int = 100_004


def produce_disk_io_task() -> None:
    """
    queue `max_tasks_to_queue` of disk IO bound tasks.
    """
    for i in range(0, max_tasks_to_queue):
        filename = (
            "/tmp/"
            + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            + "-"
            + str(i)
            + ".txt"
        )
        tasks.DiskIOTask().delay(filename=filename)


def produce_network_io_task() -> None:
    """
    queue `max_tasks_to_queue` of network IO bound tasks.
    """
    t = tasks.NetworkIOTask()
    for i in range(0, max_tasks_to_queue):
        t.delay()


def produce_cpu_bound_task() -> None:
    """
    queue `max_tasks_to_queue` of cpu bound tasks.
    """
    t = tasks.CPUTask()
    for i in range(0, max_tasks_to_queue):
        t.delay()


def produce_ram_bound_task() -> None:
    """
    queue `max_tasks_to_queue` of RAM bound tasks.
    """
    t = tasks.MemTask()
    for i in range(0, max_tasks_to_queue):
        t.delay()


def produce_adder_task() -> None:
    """
    queue `max_tasks_to_queue` of adder tasks.
    Those will in turn generate `max_tasks_to_queue` divider tasks
    """
    t1 = tasks.AdderTask()
    t2 = tasks.DividerTask()
    for i in range(0, max_tasks_to_queue):
        chain = t1.s(a=90, b=88) | t2.s()
        chain()


def main() -> None:
    """
    main function to produce tasks.
    """
    t = threading.Thread(
        target=produce_disk_io_task,
        name="Thread-<task_producer-{0}>".format(produce_disk_io_task.__name__),
    )
    t.start()

    t = threading.Thread(
        target=produce_network_io_task,
        name="Thread-<task_producer-{0}>".format(produce_network_io_task.__name__),
    )
    t.start()

    t = threading.Thread(
        target=produce_cpu_bound_task,
        name="Thread-<task_producer-{0}>".format(produce_cpu_bound_task.__name__),
    )
    t.start()

    t = threading.Thread(
        target=produce_ram_bound_task,
        name="Thread-<task_producer-{0}>".format(produce_ram_bound_task.__name__),
    )
    t.start()

    t = threading.Thread(
        target=produce_adder_task,
        name="Thread-<task_producer-{0}>".format(produce_adder_task.__name__),
    )
    t.start()


if __name__ == "__main__":
    main()
