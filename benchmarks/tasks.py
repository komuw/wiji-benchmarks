import os
import sys
import random
import string
import logging
import hashlib

import psutil
import aiohttp
from cryptography.fernet import Fernet

import wiji
import wijisqs

from benchmarks import myHook
from benchmarks import redis_broker


myHook = myHook.BenchmarksHook()


USE_SQS = os.environ.get("USE_SQS", "NO")
if USE_SQS == "YES":
    BROKER = wijisqs.SqsBroker(
        aws_region_name=os.environ["AWS_REGION_NAME"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        queue_tags={"name": "wiji.SqsBroker.benchmarks", "url": "https://github.com/komuw/wiji"},
        loglevel="DEBUG",
        long_poll=True,
        batch_send=True,
    )
else:
    BROKER = redis_broker.ExampleRedisBroker()


class BaseTask(wiji.task.Task):
    the_broker = BROKER
    the_hook = myHook
    loglevel = "INFO"


class DiskIOTask(BaseTask):
    """
    class that simulates a disk IO bound task.
    This task:
      - creates a random file
      - generates a random 16KB text(about the size of `The Raven` by `Edgar Allan Poe`)
      - opens the file, writes that 16KB text to it & closes that file
      - finally it deletes the file

    this task will also tax your cpu.
    """

    queue_name = "DiskIOTask"
    task_name = "task_name-{0}".format(queue_name)

    async def run(self, filename):
        content = "".join(random.choices(string.ascii_uppercase + string.digits, k=16384))  # 16KB
        f = open(filename, mode="a")
        f.write(content)
        f.close()
        os.remove(filename)


class NetworkIOTask(BaseTask):
    """
    class that simulates a network IO bound task.
    This task calls a url with a latency that varies between 200 milliseconds and 700 milliseconds
    """

    queue_name = "NetworkIOTask"
    task_name = "task_name-{0}".format(queue_name)

    async def run(self, *args, **kwargs):
        latency = random.randint(2, 7) / 10  # latency in seconds
        url = "https://httpbin.org/delay/{latency}".format(latency=latency)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                res_text = await resp.text()
                self.logger.log(
                    logging.INFO, {"event": "NetworkIOTask_run", "response": res_text[:50]}
                )


class CPUTask(BaseTask):
    """
    class that simulates a cpu  bound task.
    This task:
      - generates a 16KB text
      - does blake2 hash of it
      - encrypts the text
      - then decrypts it.
    """

    queue_name = "CPUTask"
    task_name = "task_name-{0}".format(queue_name)

    async def run(self, *args, **kwargs):
        content = "".join(random.choices(string.ascii_uppercase + string.digits, k=16384))  # 16KB

        h = hashlib.blake2b()
        h.update(content.encode())
        h.hexdigest()

        fernet_key = Fernet.generate_key()
        f = Fernet(fernet_key)
        token = f.encrypt(content.encode())
        f.decrypt(token)


class MemTask(BaseTask):
    """
    class that simulates a RAM/memory bound task.
    This task:
      - calculates how much free RAM there is.
      - then stores something in RAM that is equal to 10% of the free RAM
    """

    queue_name = "MemTask"
    task_name = "task_name-{0}".format(queue_name)

    @staticmethod
    def calculate_ram():
        """
        calculates various values of RAM(inclusive of SWAP).
        returns the size of free RAM in bytes
        """
        mem = psutil.virtual_memory()
        return mem.free

    async def run(self, *args, **kwargs):
        free_ram = self.calculate_ram()
        # store something in RAM that will use up a significant percentage of the available free RAM.
        target_size = int(0.1 * free_ram)
        stored_string = "a"
        stored_string = stored_string * target_size
        stored_string_size = sys.getsizeof(stored_string)
        self.logger.log(
            logging.INFO,
            {
                "event": "MemTask_run",
                "stored_string_size_bytes": stored_string_size,
                "stored_string_size_MB": stored_string_size / 1_000_000,
            },
        )
        del stored_string


class DividerTask(BaseTask):
    """
    task that divides its input by 3.
    This will be chained with the AdderTask.
    """

    queue_name = "DividerTask"
    task_name = "task_name-{0}".format(queue_name)

    async def run(self, dividend):
        answer = dividend / 3
        return answer


class AdderTask(BaseTask):
    """
    task that adds two numbers together.
    the result of this task is then passed over to the DividerTask as an argument
    """

    queue_name = "AdderTask"
    task_name = "task_name-{0}".format(queue_name)
    chain = DividerTask

    async def run(self, a, b):
        result = a + b
        return result
