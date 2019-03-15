import asyncio
import random
import string

from benchmarks import tasks


# Usage:
#  python benchmarks/task_producer.py


async def produce_disk_io_task() -> None:
    """
    queue 200K of disk IO bound tasks.
    """
    for i in range(0, 200_001):
        filename = (
            "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            + "-"
            + str(i)
            + ".txt"
        )
        await tasks.disk_io_task.delay(filename=filename)


async def produce_network_io_task() -> None:
    """
    queue 200K of network IO bound tasks.
    """
    for i in range(0, 200_001):
        await tasks.network_io_task.delay()


async def produce_cpu_bound_task() -> None:
    """
    queue 200K of cpu bound tasks.
    """
    for i in range(0, 200_001):
        await tasks.cpu_bound_task.delay()


async def main() -> None:
    """
    main function to produce 
    """

    gather_tasks = asyncio.gather(
        produce_disk_io_task(), produce_network_io_task(), produce_cpu_bound_task()
    )
    await gather_tasks


asyncio.run(main(), debug=True)
