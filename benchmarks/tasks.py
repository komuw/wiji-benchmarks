import os
import random
import string
import hashlib

import aiohttp
from cryptography.fernet import Fernet

import wiji
import wijisqs

from benchmarks import metrics
from benchmarks.redis_broker import ExampleRedisBroker


myMet = metrics.Metrics()


BROKER = ExampleRedisBroker()
# wijisqs.SqsBroker(
#     aws_region_name=os.environ["aws_region_name"],
#     aws_access_key_id=os.environ["aws_access_key_id"],
#     aws_secret_access_key=os.environ["aws_secret_access_key"],
#     queue_tags={"name": "wiji.SqsBroker.benchmarks", "url": "https://github.com/komuw/wiji"},
#     loglevel="DEBUG",
#     long_poll=True,
#     batch_send=True,
# )


class NetworkIOTask(wiji.task.Task):
    """
    class that simulates a network IO bound task.
    This task calls a url that has a latency that varies between 6 seconds and 42seconds
    """

    async def run(self, *args, **kwargs):
        latency = random.randint(6, 42)  # latency in seconds
        url = "https://httpbin.org/delay/{latency}".format(latency=latency)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                res_text = await resp.text()
                print(res_text[:50])

        await myMet.incr(counter_name="network_io_task_DEQUEUED")


network_io_task = NetworkIOTask(the_broker=BROKER, queue_name="NetworkIOTaskQueue")


class DiskIOTask(wiji.task.Task):
    """
    class that simulates a disk IO bound task.
    This task:
      - creates a random file
      - generates a random 16KB text
      - opens the file, writes that 16KB text to it, flushes the file, then closes the file
      - opens the file again, reads its content, then closes the file.
      - then it deletes the file
    
    this task will also tax your cpu.
    """

    async def run(self, *args, **kwargs):
        filename = "/tmp/" + kwargs["filename"]
        content = "".join(random.choices(string.ascii_uppercase + string.digits, k=16384))  # 16KB

        f = open(filename, mode="a")
        f.write(content)
        f.flush()
        f.close()

        new_file = open(filename, mode="r")
        new_content = new_file.read()
        new_file.close()
        print(new_content[:10])

        os.remove(filename)

        await myMet.incr(counter_name="disk_io_task_DEQUEUED")


disk_io_task = DiskIOTask(the_broker=BROKER, queue_name="DiskIOTaskQueue")


class CPUTask(wiji.task.Task):
    """
    class that simulates a cpu  bound task.
    This task:
      - generates a 16KB text
      - does blake2 hash of it
      - encrypts the text
      - then decrypts it.
    """

    async def run(self, *args, **kwargs):
        content = "".join(random.choices(string.ascii_uppercase + string.digits, k=16384))  # 16KB

        h = hashlib.blake2b()
        h.update(content.encode())
        h.hexdigest()

        key = Fernet.generate_key()
        f = Fernet(key)
        token = f.encrypt(content.encode())
        f.decrypt(token)

        await myMet.incr(counter_name="cpu_bound_task_DEQUEUED")


cpu_bound_task = CPUTask(the_broker=BROKER, queue_name="CPUTaskQueue")


class DividerTask(wiji.task.Task):
    """
    task that divides its input by 3.
    This will be chained with the AdderTask.
    """

    async def run(self, dividend):
        answer = dividend / 3

        await myMet.incr(counter_name="divider_task_DEQUEUED")
        return answer


divider_task = DividerTask(the_broker=BROKER, queue_name="DividerTaskQueue")


class AdderTask(wiji.task.Task):
    """
    task that adds two numbers together
    """

    async def run(self, a, b):
        result = a + b

        await myMet.incr(counter_name="adder_task_DEQUEUED")
        return result


adder_task = AdderTask(the_broker=BROKER, chain=divider_task, queue_name="AdderTaskQueue")
