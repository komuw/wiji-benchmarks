import os
import json
import typing
import asyncio
import functools
import concurrent
import logging

import redis
import wiji


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
        self.redis_instance = redis.StrictRedis(host=host, port=port, db=0)
        self.thread_name_prefix = "wiji-benchmarks-metrics-pool"

    async def set(self, key: str, val: dict) -> None:
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()

        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            await self.loop.run_in_executor(
                executor, functools.partial(self._blocking_set, key=key, val=val)
            )

    def _blocking_set(self, key: str, val: typing.Dict[str, typing.Any]) -> None:
        try:
            old_val = self.redis_instance.get(key)
            if old_val:
                old_val = json.loads(old_val)
                old_val.update(val)
                val = old_val
        except Exception:
            pass

        self.redis_instance.set(key, json.dumps(val))

    async def get(self, key: str) -> dict:
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()

        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            val = await self.loop.run_in_executor(
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
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()

        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            counter = await self.loop.run_in_executor(
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
        metric_names = [
            "network_io_task",
            "disk_io_task",
            "cpu_bound_task",
            "adder_task",
            "divider_task",
        ]

        while True:
            # NB: the metrics may not have queueing metrics(eg queue_count) until all tasks have been queued
            for met_name in metric_names:
                val = await met.get(key=met_name)
                logger.log(logging.INFO, {"event": "stream_metric", "val": val})

            await asyncio.sleep(10)

    asyncio.run(main(), debug=True)


if __name__ == "__main__":
    main()
