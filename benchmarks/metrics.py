import os
import json
import uuid
import typing
import logging
import asyncio
import functools
import concurrent

import redis
import wiji
import matplotlib.pyplot as plt

from benchmarks import tasks


class Metrics:
    """
    This keeps track of how many tasks of each type;
      - have been queued.
      - have been dequeed
      - any other Metrics we fancy.
    """

    def __init__(self):
        host = "localhost"
        port = 6379
        if os.environ.get("IN_DOCKER"):
            host = os.environ["REDIS_HOST"]
            port = os.environ["REDIS_PORT"]
        self.redis_instance = redis.StrictRedis(
            host=host, port=port, db=0, socket_connect_timeout=8, socket_timeout=8
        )
        self.thread_name_prefix = "wiji-benchmarks-metrics-pool"
        self._LOOP: typing.Union[None, asyncio.events.AbstractEventLoop] = None

    def _get_loop(self,):
        if self._LOOP:
            return self._LOOP
        try:
            loop: asyncio.events.AbstractEventLoop = asyncio.get_running_loop()
        except RuntimeError:
            loop: asyncio.events.AbstractEventLoop = asyncio.get_event_loop()
        except Exception as e:
            raise e
        # cache event loop
        self._LOOP = loop
        return loop

    async def set(self, key: str, val: dict) -> None:
        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            await self._get_loop().run_in_executor(
                executor, functools.partial(self._blocking_set, key=key, val=val)
            )

    def _blocking_set(self, key: str, val: typing.Dict[str, typing.Any]) -> None:
        self.redis_instance.set(key, json.dumps(val))

    async def get(self, key: str) -> dict:
        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            val = await self._get_loop().run_in_executor(
                executor, functools.partial(self._blocking_get, key=key)
            )
            if val:
                return json.loads(val)
            else:
                return {}

    def _blocking_get(self, key: str) -> typing.Dict[str, typing.Any]:
        val = self.redis_instance.get(key)
        return val

    async def incr(self, counter_name: str) -> None:
        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            counter = await self._get_loop().run_in_executor(
                executor, functools.partial(self._blocking_incr, counter_name=counter_name)
            )
            return counter

    def _blocking_incr(self, counter_name: str) -> None:
        return self.redis_instance.incrby(counter_name)

    async def lpush(self, name: str, val: dict) -> None:
        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            await self._get_loop().run_in_executor(
                executor, functools.partial(self._blocking_lpush, name=name, val=val)
            )

    def _blocking_lpush(self, name: str, val: dict) -> None:
        self.redis_instance.lpush(name, json.dumps(val))

    async def lrange(self, name: str) -> list:
        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            items = await self._get_loop().run_in_executor(
                executor, functools.partial(self._blocking_lrange, name=name)
            )
            return items

    def _blocking_lrange(self, name: str) -> list:
        return self.redis_instance.lrange(name, 0, -1)


async def stream_metrics(delay_duration):
    """
    stream metrics as they come in.
    """
    logger = wiji.logger.SimpleLogger("metrics_streaming")
    logger.bind(level="INFO", log_metadata={})

    met = Metrics()

    task_names = [
        tasks.NetworkIOTask.task_name,
        tasks.DiskIOTask.task_name,
        tasks.CPUTask.task_name,
        tasks.MemTask.task_name,
        tasks.DividerTask.task_name,
        tasks.AdderTask.task_name,
    ]

    metric_names = []
    for t_name in task_names:
        metric_names.append(t_name + "_queuing_duration")
        metric_names.append(t_name + "_execution_duration")

    while True:
        # NB: the metrics may not have queueing metrics(eg queue_count) until all tasks have been queued
        queuing_metrics = []
        for met_name in metric_names:
            val = await met.get(key=met_name)
            queuing_metrics.append(val)
        logger.log(logging.INFO, {"event": "stream_metric", "queuing_metrics": queuing_metrics})
        with open("/tmp/metrics/queuing_metrics.json", mode="w") as f:  # overrite file
            f.write(json.dumps(queuing_metrics))

        host_metrics = await met.lrange(name="host_metrics")
        logger.log(logging.INFO, {"event": "stream_metric", "host_metrics": host_metrics})

        new_host_metrics = []
        for i in host_metrics:
            new_host_metrics.append(i.decode())
        with open("/tmp/metrics/host_metrics.json", mode="w") as f:
            f.write(json.dumps(new_host_metrics))

        await asyncio.sleep(delay_duration)


async def combine_queuing_metrics(delay_duration):
    """
    """
    queuing_metrics = None
    task_queuing_metrics = {
        # "MyExampleTask1": {
        #     "tasks_queued": 45,
        #     "queuing_duration": 0.98,
        #     "tasks_dequeued": 3,
        #     "execution_duration": 0.56,
        # }
    }
    while True:
        await asyncio.sleep(delay_duration + (delay_duration / 6))
        with open("/tmp/metrics/queuing_metrics.json", mode="r") as f:
            met = f.read()
            queuing_metrics = json.loads(met)

        for task_met in queuing_metrics:
            if not task_queuing_metrics.get(task_met["task_name"]):
                task_queuing_metrics[task_met["task_name"]] = {}

            if task_met.get("tasks_queued"):
                task_queuing_metrics[task_met["task_name"]].update(
                    {"tasks_queued": task_met.get("tasks_queued")}
                )
            if task_met.get("queuing_duration"):
                task_queuing_metrics[task_met["task_name"]].update(
                    {"queuing_duration": task_met.get("queuing_duration")}
                )
            if task_met.get("tasks_dequeued"):
                task_queuing_metrics[task_met["task_name"]].update(
                    {"tasks_dequeued": task_met.get("tasks_dequeued")}
                )
            if task_met.get("execution_duration"):
                task_queuing_metrics[task_met["task_name"]].update(
                    {"execution_duration": task_met.get("execution_duration")}
                )

        with open("/tmp/metrics/final_queuing_metrics.json", mode="w") as f:
            f.write(json.dumps(task_queuing_metrics, indent=2))


async def combine_host_metrics(delay_duration):
    def get_host_met():
        new_host_metrics = []
        with open("/tmp/metrics/host_metrics.json", mode="r") as f:
            met = f.read()
            host_metrics = json.loads(met)
            for i in host_metrics:
                new_host_metrics.append(json.loads(i))
        return new_host_metrics

    def get_mem_metrics(new_host_metrics):
        """
        To plot/graph:
          1. create figure
          2. plt.plot
          3. style, add x-y labels
          4. plt.legend, plt.title, plt.ylim
          5. plt.savefig
        """
        TOTAL_RAM = new_host_metrics[0]["total_ram"]
        rss_mem_over_time = []
        for i in new_host_metrics:
            rss_mem_over_time.append(i["rss_mem"])

        plt.figure("mem-{0}".format(str(uuid.uuid4())))
        plt.plot(rss_mem_over_time, color="green", label="rss memory")
        # plt.plot(total_ram_array, color="blue", label="total memory")  # 2graphs in one
        plt.style.use("seaborn-whitegrid")
        plt.ylabel("Memory usage (MB)")
        plt.xlabel("time")
        plt.legend()  # legend(loc="upper right")
        plt.title("Memory usage. Total Memory={0} MB".format(int(TOTAL_RAM)))
        plt.ylim(0, TOTAL_RAM / 8)

        mem_graph = "/tmp/metrics/rss_mem_over_time.png"
        if os.path.exists(mem_graph):
            # so that it can be overritten
            os.remove(mem_graph)
        plt.savefig(mem_graph)

    def get_cpu_metrics(new_host_metrics):
        cpu_percent_over_time = []
        for i in new_host_metrics:
            cpu_percent_over_time.append(i["cpu_percent"])

        plt.figure(
            "cpu-{0}".format(str(uuid.uuid4()))
        )  # creates new named instance instead of re-using
        plt.plot(cpu_percent_over_time, color="green", label="cpu_percent")
        plt.style.use("seaborn-whitegrid")
        plt.ylabel("CPU usage (%)")
        plt.xlabel("time")
        plt.legend()
        plt.title("CPU usage.")
        plt.ylim(0, 100)

        cpu_graph = "/tmp/metrics/cpu_percent_over_time.png"
        if os.path.exists(cpu_graph):
            # so that it can be overritten
            os.remove(cpu_graph)
        plt.savefig(cpu_graph)

    while True:
        await asyncio.sleep(delay_duration + (delay_duration / 6))
        new_host_metrics = get_host_met()
        get_mem_metrics(new_host_metrics)
        get_cpu_metrics(new_host_metrics)


def main():
    """
    usage:
        python benchmarks/metrics.py
    """

    async def async_main(delay_duration) -> None:
        gather_tasks = asyncio.gather(
            stream_metrics(delay_duration=delay_duration),
            combine_queuing_metrics(delay_duration=delay_duration),
            combine_host_metrics(delay_duration=delay_duration),
        )
        await gather_tasks

    asyncio.run(async_main(delay_duration=10 * 60), debug=True)  # 10mins


if __name__ == "__main__":
    main()
