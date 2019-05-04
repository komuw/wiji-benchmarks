import os
import json
import typing
import asyncio
import functools
import concurrent
import logging

import redis
import wiji

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


def main():
    async def main() -> None:
        """
        stream metrics as they come in.

        usage:
            python benchmarks/metrics.py
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
            for met_name in metric_names:
                val = await met.get(key=met_name)
                logger.log(
                    logging.INFO, {"event": "stream_metric", "val": val, "met_name": met_name}
                )

            await asyncio.sleep(10)

    asyncio.run(main(), debug=True)


if __name__ == "__main__":
    main()
