import os
import sys
import random
import string
import logging
import hashlib

import celery
import requests
from cryptography.fernet import Fernet


"""
run as:
    1. celery worker -A tasks --concurrency=3 --loglevel=DEBUG
"""


host = "localhost"
port = 6379
password = None
if os.environ.get("IN_DOCKER"):
    host = os.environ["REDIS_HOST"]
    port = os.environ["REDIS_PORT"]
    password = os.environ.get("REDIS_PASSWORD", None)


# broker
CELERY_BROKER_URL = "redis://{host}:{port}/{db_number}".format(
    password=password, host=host, port=port, db_number=0
)
app = celery.Celery("tasks", broker=CELERY_BROKER_URL)


def get_memory():
    """
    Get node total memory and memory usage in KB(kilo-byte).

    returns a dict like:
      {'total': 3075868, 'free': 283536, 'buffers': 1749044, 'cached': 552156, 'used': 491132}
    """
    with open("/proc/meminfo", "r") as mem:
        ret = {}
        for i in mem:
            sline = i.split()
            if str(sline[0]) == "MemTotal:":
                ret["total"] = int(sline[1])
            elif str(sline[0]) == "MemFree:":
                ret["free"] = int(sline[1])
            elif str(sline[0]) == "Buffers:":
                ret["buffers"] = int(sline[1])
            elif str(sline[0]) == "Cached:":
                ret["cached"] = int(sline[1])

        ret["used"] = int(ret["total"]) - (int(ret["free"] + ret["buffers"] + ret["cached"]))
    return ret


ALL_MEMORY = get_memory()


class DiskIOTask(app.Task):
    """
    class that simulates a disk IO bound task.
    This task:
      - creates a random file
      - generates a random 16KB text(about the size of `The Raven` by `Edgar Allan Poe`)
      - opens the file, writes that 16KB text to it & closes that file
      - finally it deletes the file

    this task will also tax your cpu.
    """

    name = "DiskIOTask"

    def run(self, filename):
        content = "".join(random.choices(string.ascii_uppercase + string.digits, k=16384))  # 16KB
        f = open(filename, mode="a")
        f.write(content)
        f.close()
        os.remove(filename)


class NetworkIOTask(app.Task):
    """
    class that simulates a network IO bound task.
    This task calls a url with a latency that varies between 100 milliseconds and 400 milliseconds
    """

    name = "NetworkIOTask"

    def run(self, *args, **kwargs):
        url = "http://slow_app:9797/slow"
        res = requests.get(url)
        print("response", res.content[:50])


class CPUTask(app.Task):
    """
    class that simulates a cpu  bound task.
    This task:
      - generates a 16KB text
      - does blake2 hash of it
      - encrypts the text
      - then decrypts it.
    """

    name = "CPUTask"

    def run(self, *args, **kwargs):
        content = "".join(random.choices(string.ascii_uppercase + string.digits, k=16384))  # 16KB

        h = hashlib.blake2b()
        h.update(content.encode())
        h.hexdigest()

        fernet_key = Fernet.generate_key()
        f = Fernet(fernet_key)
        token = f.encrypt(content.encode())
        f.decrypt(token)


class MemTask(app.Task):
    """
    class that simulates a RAM/memory bound task.
    This task:
      - calculates how much free RAM there is.
      - then stores something in RAM that is equal to 10% of the free RAM
    """

    name = "MemTask"

    def run(self, *args, **kwargs):
        free_ram = ALL_MEMORY["free"] * 1000  # convert to bytes
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


class DividerTask(app.Task):
    """
    task that divides its input by 3.
    This will be chained with the AdderTask.
    """

    name = "DividerTask"

    def run(self, dividend):
        answer = dividend / 3
        return answer


class AdderTask(app.Task):
    """
    task that adds two numbers together.
    the result of this task is then passed over to the DividerTask as an argument
    """

    name = "AdderTask"

    def run(self, a, b):
        result = a + b
        return result


app.tasks.register(DiskIOTask())
app.tasks.register(NetworkIOTask())
app.tasks.register(CPUTask())
app.tasks.register(MemTask())
app.tasks.register(DividerTask())
app.tasks.register(AdderTask())
