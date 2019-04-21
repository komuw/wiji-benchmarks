import sys
import typing
import logging

import wiji

from benchmarks import metrics


myMet = metrics.Metrics()


class BenchmarksHook(wiji.hook.BaseHook):
    def __init__(self,) -> None:
        self.logger = wiji.logger.SimpleLogger("wiji.benchmarks.BenchmarksHook")

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
        try:
            if not isinstance(execution_exception, type(None)):
                raise ValueError(
                    "task produced error. task_name={0}".format(task_name)
                ) from execution_exception
        except Exception as e:
            # yep, we are serious that this benchmarks should complete without error
            # else we exit
            self.logger.log(
                logging.ERROR,
                {
                    "event": "wiji.BenchmarksHook.notify",
                    "stage": "end",
                    "error": str(e),
                    "state": state,
                    "task_name": task_name,
                    "queue_name": queue_name,
                    "execution_exception": str(execution_exception),
                    "return_value": str(return_value),
                },
            )
            sys.exit(99)

        if state == wiji.task.TaskState.EXECUTED:
            key = task_name
            time_to_execute_one_task = float("{0:.2f}".format(execution_duration["monotonic"]))

            counter = await myMet.incr(
                counter_name="counter_{0}".format(task_name)
            )  # key raises a redis Error
            val = {
                "task_name": key,
                "DE_queue_count": counter,
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
                    "queue_name": queue_name,
                    "execution_exception": str(execution_exception),
                    "return_value": str(return_value),
                    "key": key,
                    "val": val,
                },
            )
