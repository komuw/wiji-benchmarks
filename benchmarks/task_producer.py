import asyncio
import random
import string

from . import tasks


async def produce_network_io_task() -> None:
    for i in range(0, 200000):
        await tasks.network_io_task.delay()


async def produce_disk_io_task() -> None:
    for i in range(0, 200000):
        filename = (
            "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            + "-"
            + str(i)
            + ".txt"
        )
        await tasks.disk_io_task(filename=filename)


async def produce_cpu_bound_task() -> None:
    for i in range(0, 200000):
        await tasks.cpu_bound_task.delay()


async def main() -> None:
    """
    main function to produce tasks.
    """

    gather_tasks = asyncio.gather(
        produce_network_io_task(), produce_disk_io_task(), produce_cpu_bound_task()
    )
    await gather_tasks


asyncio.run(main(), debug=True)
