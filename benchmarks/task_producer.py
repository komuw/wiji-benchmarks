import asyncio
import random
import string

from benchmarks import tasks


# Usage:
#  python benchmarks/task_producer.py


max_tasks_to_queue: int = 100_004


async def produce_disk_io_task() -> None:
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
        await tasks.DiskIOTask().delay(filename=filename)


async def produce_network_io_task() -> None:
    """
    queue `max_tasks_to_queue` of network IO bound tasks.
    """
    t = tasks.NetworkIOTask()
    for i in range(0, max_tasks_to_queue):
        await t.delay()


async def produce_cpu_bound_task() -> None:
    """
    queue `max_tasks_to_queue` of cpu bound tasks.
    """
    t = tasks.CPUTask()
    for i in range(0, max_tasks_to_queue):
        await t.delay()


async def produce_ram_bound_task() -> None:
    """
    queue `max_tasks_to_queue` of RAM bound tasks.
    """
    t = tasks.MemTask()
    for i in range(0, max_tasks_to_queue):
        await t.delay()


async def produce_adder_task() -> None:
    """
    queue `max_tasks_to_queue` of adder tasks.
    Those will in turn generate `max_tasks_to_queue` divider tasks
    """
    t = tasks.AdderTask()
    for i in range(0, max_tasks_to_queue):
        await t.delay(a=90, b=88)


async def main() -> None:
    """
    main function to produce tasks.
    """

    gather_tasks = asyncio.gather(
        produce_disk_io_task(),
        produce_network_io_task(),
        produce_cpu_bound_task(),
        produce_ram_bound_task(),
        produce_adder_task(),
    )
    await gather_tasks


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
