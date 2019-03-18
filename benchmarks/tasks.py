import os
import time
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


USE_SQS = os.environ.get("USE_SQS", "NO")
if USE_SQS == "YES":
    BROKER = wijisqs.SqsBroker(
        aws_region_name=os.environ["aws_region_name"],
        aws_access_key_id=os.environ["aws_access_key_id"],
        aws_secret_access_key=os.environ["aws_secret_access_key"],
        queue_tags={"name": "wiji.SqsBroker.benchmarks", "url": "https://github.com/komuw/wiji"},
        loglevel="DEBUG",
        long_poll=True,
        batch_send=True,
    )
else:
    BROKER = ExampleRedisBroker()


class NetworkIOTask(wiji.task.Task):
    """
    class that simulates a network IO bound task.
    This task calls a url that has a latency that varies between 2 seconds and 7 seconds
    """

    async def run(self, *args, **kwargs):
        key = "network_io_task"
        val = {"task_name": key, "DE_queue_count": 0, "time_to_execute_one_task": 0.00}
        start = time.monotonic()

        latency = random.randint(2, 7)  # latency in seconds
        url = "https://httpbin.org/delay/{latency}".format(latency=latency)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                res_text = await resp.text()
                print(res_text[:50])

        end = time.monotonic()
        val["DE_queue_count"] += 1
        val["time_to_execute_one_task"] = float("{0:.2f}".format(end - start))
        await myMet.set(key, val)


network_io_task = NetworkIOTask(the_broker=BROKER, queue_name="NetworkIOTaskQueue")


class DiskIOTask(wiji.task.Task):
    """
    class that simulates a disk IO bound task.
    This task:
      - creates a random file
      - generates a random 16KB text
      - opens the file, writes that 16KB text to it, fsyncs to disk, then closes that file
      - finally it deletes the file

    this task will also tax your cpu.
    """

    async def run(self, *args, **kwargs):
        key = "disk_io_task"
        val = {"task_name": key, "DE_queue_count": 0, "time_to_execute_one_task": 0.00}
        start = time.monotonic()

        filename = kwargs["filename"]
        content = "".join(random.choices(string.ascii_uppercase + string.digits, k=16384))  # 16KB

        f = open(filename, mode="a")
        f.write(content)
        f.flush()
        f.close()

        os.remove(filename)

        end = time.monotonic()
        val["DE_queue_count"] += 1
        val["time_to_execute_one_task"] = float("{0:.2f}".format(end - start))
        await myMet.set(key, val)


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
        key = "cpu_bound_task"
        val = {"task_name": key, "DE_queue_count": 0, "time_to_execute_one_task": 0.00}
        start = time.monotonic()

        content = "".join(random.choices(string.ascii_uppercase + string.digits, k=16384))  # 16KB

        h = hashlib.blake2b()
        h.update(content.encode())
        h.hexdigest()

        key = Fernet.generate_key()
        f = Fernet(key)
        token = f.encrypt(content.encode())
        f.decrypt(token)

        end = time.monotonic()
        val["DE_queue_count"] += 1
        val["time_to_execute_one_task"] = float("{0:.2f}".format(end - start))
        await myMet.set(key, val)


cpu_bound_task = CPUTask(the_broker=BROKER, queue_name="CPUTaskQueue")


class DividerTask(wiji.task.Task):
    """
    task that divides its input by 3.
    This will be chained with the AdderTask.
    """

    async def run(self, dividend):
        key = "divider_task"
        val = {"task_name": key, "DE_queue_count": 0, "time_to_execute_one_task": 0.00}
        start = time.monotonic()

        answer = dividend / 3

        end = time.monotonic()
        val["DE_queue_count"] += 1
        val["time_to_execute_one_task"] = float("{0:.2f}".format(end - start))
        await myMet.set(key, val)

        return answer


divider_task = DividerTask(the_broker=BROKER, queue_name="DividerTaskQueue")


class AdderTask(wiji.task.Task):
    """
    task that adds two numbers together
    """

    async def run(self, a, b):
        key = "adder_task"
        val = {"task_name": key, "DE_queue_count": 0, "time_to_execute_one_task": 0.00}
        start = time.monotonic()

        result = a + b

        end = time.monotonic()
        val["DE_queue_count"] += 1
        val["time_to_execute_one_task"] = float("{0:.2f}".format(end - start))
        await myMet.set(key, val)

        return result


adder_task = AdderTask(the_broker=BROKER, chain=divider_task, queue_name="AdderTaskQueue")
