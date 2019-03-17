import asyncio
import random
import string

from benchmarks import tasks
from benchmarks import metrics

# Usage:
#  python benchmarks/task_producer.py


myMet = metrics.Metrics()


max_tasks: int = 200_001


async def produce_disk_io_task() -> None:
    """
    queue 200K of disk IO bound tasks.
    """
    for i in range(0, max_tasks):
        filename = (
            "/tmp/"
            + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            + "-"
            + str(i)
            + ".txt"
        )
        await tasks.disk_io_task.delay(filename=filename)
        await myMet.incr(counter_name="disk_io_task_queued")


async def produce_network_io_task() -> None:
    """
    queue 200K of network IO bound tasks.
    """
    for i in range(0, max_tasks):
        await tasks.network_io_task.delay()
        await myMet.incr(counter_name="network_io_task_queued")


async def produce_cpu_bound_task() -> None:
    """
    queue 200K of cpu bound tasks.
    """
    for i in range(0, max_tasks):
        await tasks.cpu_bound_task.delay()
        await myMet.incr(counter_name="cpu_bound_task_queued")


async def produce_adder_task() -> None:
    """
    queue 200K of adder tasks.
    Those will in turn generate 200K divider tasks
    """
    for i in range(0, max_tasks):
        await tasks.adder_task.delay(a=90, b=88)
        await myMet.incr(counter_name="adder_task_queued")


async def main() -> None:
    """
    main function to produce tasks.
    """

    gather_tasks = asyncio.gather(
        produce_disk_io_task(),
        produce_network_io_task(),
        produce_cpu_bound_task(),
        produce_adder_task(),
    )
    await gather_tasks


asyncio.run(main(), debug=True)
