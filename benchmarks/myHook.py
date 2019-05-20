import sys
import typing
import random
import logging

import wiji

import prometheus_client


class BenchmarksHook(wiji.hook.BaseHook):
    def __init__(self) -> None:
        self.logger = wiji.logger.SimpleLogger("wiji.benchmarks.BenchmarksHook")

        self.registry = prometheus_client.CollectorRegistry()
        self.counters = {}
        _tasks = ["DiskIOTask", "NetworkIOTask", "CPUTask", "MemTask", "DividerTask", "AdderTask"]
        for task in _tasks:
            _queued_counter = prometheus_client.Counter(
                "{task}_queued".format(task=task),
                "number of task:{task} that have been queued by wiji.".format(task=task),
                registry=self.registry,
            )
            _exectued_counter = prometheus_client.Counter(
                "{task}_exectued".format(task=task),
                "number of task:{task} that have been exectued by wiji.".format(task=task),
                registry=self.registry,
            )
            self.counters.update({task: {"queued": _queued_counter, "executed": _exectued_counter}})

        # go to prometheus dashboard(http://localhost:9090/) & you can run queries like:
        # container_memory_rss{name="wiji_cli", container_label_com_docker_compose_service="wiji_cli"}

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
            sys.exit(97)
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
            sys.exit(98)

        try:
            if state == wiji.task.TaskState.QUEUED:
                self.counters[queue_name]["queued"].inc()  # Increment by 1
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
                self.counters[queue_name]["executed"].inc()  # Increment by 1
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
                },
            )
            sys.exit(99)
        finally:
            prometheus_client.push_to_gateway(
                "push_to_gateway:9091", job="BenchmarksHook", registry=self.registry
            )
