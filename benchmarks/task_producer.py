import time
import asyncio
import random
import string

from benchmarks import tasks
from benchmarks import metrics

# Usage:
#  python benchmarks/task_producer.py


myMet = metrics.Metrics()


max_tasks: int = 10001


async def produce_disk_io_task() -> None:
    """
    queue `max_tasks` of disk IO bound tasks.
    """
    key = tasks.DiskIOTask.task_name
    val = {"task_name": key, "queue_count": 0, "time_to_queue_one_task": 0.00}
    for i in range(0, max_tasks):
        filename = (
            "/tmp/"
            + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            + "-"
            + str(i)
            + ".txt"
        )

        start = time.monotonic()
        await tasks.DiskIOTask().delay(filename=filename)
        end = time.monotonic()
        val["queue_count"] += 1
        val["time_to_queue_one_task"] = float("{0:.2f}".format(end - start))

    await myMet.set(key, val)


async def produce_network_io_task() -> None:
    """
    queue `max_tasks` of network IO bound tasks.
    """
    key = tasks.NetworkIOTask.task_name
    val = {"task_name": key, "queue_count": 0, "time_to_queue_one_task": 0.00}
    for i in range(0, max_tasks):
        start = time.monotonic()
        await tasks.NetworkIOTask().delay()
        end = time.monotonic()
        val["queue_count"] += 1
        val["time_to_queue_one_task"] = float("{0:.2f}".format(end - start))

    await myMet.set(key, val)


async def produce_cpu_bound_task() -> None:
    """
    queue `max_tasks` of cpu bound tasks.
    """
    key = tasks.CPUTask.task_name
    val = {"task_name": key, "queue_count": 0, "time_to_queue_one_task": 0.00}
    for i in range(0, max_tasks):
        start = time.monotonic()
        await tasks.CPUTask().delay()
        end = time.monotonic()
        val["queue_count"] += 1
        val["time_to_queue_one_task"] = float("{0:.2f}".format(end - start))

    await myMet.set(key, val)


async def produce_ram_bound_task() -> None:
    """
    queue `max_tasks` of RAM bound tasks.
    """
    key = tasks.MemTask.task_name
    val = {"task_name": key, "queue_count": 0, "time_to_queue_one_task": 0.00}
    for i in range(0, max_tasks):
        start = time.monotonic()
        await tasks.MemTask().delay()
        end = time.monotonic()
        val["queue_count"] += 1
        val["time_to_queue_one_task"] = float("{0:.2f}".format(end - start))

    await myMet.set(key, val)


async def produce_adder_task() -> None:
    """
    queue `max_tasks` of adder tasks.
    Those will in turn generate `max_tasks` divider tasks
    """
    key = tasks.AdderTask.task_name
    val = {"task_name": key, "queue_count": 0, "time_to_queue_one_task": 0.00}
    for i in range(0, max_tasks):
        start = time.monotonic()
        await tasks.AdderTask().delay(a=90, b=88)
        end = time.monotonic()
        val["queue_count"] += 1
        val["time_to_queue_one_task"] = float("{0:.2f}".format(end - start))

    await myMet.set(key, val)


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


asyncio.run(main(), debug=True)
