import os
import sys
import typing
import logging

import wiji
import psutil

from benchmarks import metrics


myMet = metrics.Metrics()


CURRENT_PROCESS = psutil.Process()


class BenchmarksHook(wiji.hook.BaseHook):
    def __init__(self,) -> None:
        self.logger = wiji.logger.SimpleLogger("wiji.benchmarks.BenchmarksHook")

    async def set_host_metrics(self):
        """
        calculates & set's various host metrics
        """
        mem = psutil.virtual_memory()
        total_ram = mem.total / 1_000_000
        used_ram = mem.used / 1_000_000
        free_ram = mem.free / 1_000_000

        cpu_percent = CURRENT_PROCESS.cpu_percent()
        process_id = CURRENT_PROCESS.pid

        val = {
            "total_ram": total_ram,
            "used_ram": used_ram,
            "free_ram": free_ram,
            "cpu_percent": cpu_percent,
            "process_id": process_id,
        }
        await myMet.lpush("host_metrics", val)

    async def notify(
        self,
        task_name: str,
        task_id: str,
        queue_name: str,
        hook_metadata: str,
        state: wiji.task.TaskState,
        queuing_duration: typing.Union[None, typing.Dict[str, float]] = None,
        queuing_exception: typing.Union[None, Exception] = None,
        execution_duration: typing.Union[None, typing.Dict[str, float]] = None,
        execution_exception: typing.Union[None, Exception] = None,
        return_value: typing.Union[None, typing.Any] = None,
    ) -> None:

        await self.set_host_metrics()

        try:
            if not isinstance(queuing_exception, type(None)):
                raise ValueError(
                    "task Queuing produced error. task_name={0}".format(task_name)
                ) from queuing_exception
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
                    "queuing_exception": str(queuing_exception),
                },
            )
            sys.exit(98)
        try:
            if not isinstance(execution_exception, type(None)):
                raise ValueError(
                    "task Execution produced error. task_name={0}".format(task_name)
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

        if state == wiji.task.TaskState.QUEUED:
            queuing_duration = float("{0:.2f}".format(queuing_duration["monotonic"]))
            tasks_queued = await myMet.incr(
                counter_name="tasks_queued_counter_{0}".format(task_name)
            )
            val = {
                "task_name": task_name,
                "tasks_queued": tasks_queued,
                "queuing_duration": queuing_duration,
            }
            await myMet.set(task_name + "_queuing_duration", val)
            self.logger.log(
                logging.DEBUG,
                {
                    "event": "wiji.BenchmarksHook.notify",
                    "state": state,
                    "task_name": task_name,
                    "queue_name": queue_name,
                },
            )

        elif state == wiji.task.TaskState.EXECUTED:
            execution_duration = float("{0:.2f}".format(execution_duration["monotonic"]))
            tasks_dequeued = await myMet.incr(
                counter_name="tasks_dequeued_counter_{0}".format(task_name)
            )
            val = {
                "task_name": task_name,
                "tasks_dequeued": tasks_dequeued,
                "execution_duration": execution_duration,
            }
            await myMet.set(task_name + "_execution_duration", val)

            self.logger.log(
                logging.DEBUG,
                {
                    "event": "wiji.BenchmarksHook.notify",
                    "stage": "start",
                    "state": state,
                    "task_name": task_name,
                    "queue_name": queue_name,
                    "execution_exception": str(execution_exception),
                    "return_value": str(return_value),
                },
            )
