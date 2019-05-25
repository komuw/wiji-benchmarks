# import asyncio
# import random
# import string

# from benchmarks import tasks


# Usage:
#  python benchmarks/task_producer.py

import tasks

max_tasks_to_queue: int = 100_004


def main() -> None:
    """
    main function to produce tasks.
    """
    t = tasks.MyTask()
    for i in range(0, 99):
        t.delay(45, 89)

    # for i in range(0, 99):
    #     tasks.add.delay(45, 89)

    # gather_tasks = asyncio.gather(
    #     produce_disk_io_task(),
    #     produce_network_io_task(),
    #     produce_cpu_bound_task(),
    #     produce_ram_bound_task(),
    #     produce_adder_task(),
    # )
    # await gather_tasks


if __name__ == "__main__":
    main()
