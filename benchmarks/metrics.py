import os
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

    async def incr(self, counter_name: str) -> None:
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()

        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            await self.loop.run_in_executor(
                executor, functools.partial(self._blocking_incr, counter_name=counter_name)
            )

    def _blocking_incr(self, counter_name: str) -> None:
        self.redis_instance.incr(counter_name)

    async def get(self, counter_name: str) -> typing.Union[None, str]:
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()

        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix=self.thread_name_prefix
        ) as executor:
            count = await self.loop.run_in_executor(
                executor, functools.partial(self._blocking_get, counter_name=counter_name)
            )
            if count:
                count = count.decode()
            return count

    def _blocking_get(self, counter_name: str) -> typing.Union[None, bytes]:
        return self.redis_instance.get(counter_name)


def main():
    async def main() -> None:
        """
        stream metrics as they come in.
        """
        logger = wiji.logger.SimpleLogger("metrics_streaming")
        logger.bind(level="INFO", log_metadata={})

        met = Metrics()
        metric_names = [
            "disk_io_task_queued",
            "network_io_task_queued",
            "cpu_bound_task_queued",
            "adder_task_queued",
        ]
        while True:
            for met_name in metric_names:
                met_count = await met.get(counter_name=met_name)
                print("\n")
                print("METRIC: {0}. value: {1}".format(met_name, met_count))
                logger.log(
                    logging.INFO,
                    {"event": "stream_metric", "metric_name": met_name, "metric_count": met_count},
                )

            await asyncio.sleep(10)

    asyncio.run(main(), debug=True)


if __name__ == "__main__":
    main()
