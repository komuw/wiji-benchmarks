import typing
import logging

import wiji

from benchmarks import metrics


myMet = metrics.Metrics()


class Yo:
    def __init__(self,) -> None:
        self.DE_queue_counts = {
            "network_io_task": 0,
            "disk_io_task": 0,
            "cpu_bound_task": 0,
            "adder_task": 0,
            "divider_task": 0,
        }

    def update(self, key):
        val = self.DE_queue_counts[key]
        self.DE_queue_counts[key] = val + 1

    def get(self, key):
        return self.DE_queue_counts[key]

    def all(self):
        return self.DE_queue_counts


yy = Yo()


class BenchmarksHook(wiji.hook.BaseHook):
    def __init__(self,) -> None:
        self.logger = wiji.logger.SimpleLogger("wiji.benchmarks.BenchmarksHook")

        self.lookup = {
            "NetworkIOTask": "network_io_task",
            "DiskIOTask": "disk_io_task",
            "CPUTask": "cpu_bound_task",
            "AdderTask": "adder_task",
            "DividerTask": "divider_task",
        }

    async def notify(
        self,
        task_name: str,
        task_id: str,
        queue_name: str,
        hook_metadata: str,
        state: wiji.task.TaskState,
        execution_duration: typing.Union[None, typing.Dict[str, float]] = None,
        execution_exception: typing.Union[None, Exception] = None,
        return_value: typing.Union[None, typing.Any] = None,
    ) -> None:

        if state == wiji.task.TaskState.EXECUTED:
            key = self.lookup[task_name]
            yy.update(key=key)

            time_to_execute_one_task = float("{0:.2f}".format(execution_duration["monotonic"]))

            val = {
                "task_name": key,
                "DE_queue_count": 0,
                "time_to_execute_one_task": time_to_execute_one_task,
            }
            await myMet.set(key, val)

            self.logger.log(
                logging.INFO,
                {
                    "event": "wiji.BenchmarksHook.notify",
                    "stage": "start",
                    "state": state,
                    "task_name": task_name,
                    "task_id": task_id,
                    "queue_name": queue_name,
                    "hook_metadata": hook_metadata,
                    "execution_duration": execution_duration,
                    "execution_exception": str(execution_exception),
                    "return_value": str(return_value),
                    "key": key,
                    "val": val,
                    "DE_queue_counts": yy.all(),
                    "DE_queue_counts[key]": yy.get(key=key),
                },
            )
