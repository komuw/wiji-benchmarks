import sys

import prometheus_client


class BenchmarksHook:
    def __init__(self) -> None:
        self.registry = prometheus_client.CollectorRegistry()
        _labels = ["library", "task_name", "state"]
        self.counter = prometheus_client.Counter(
            name="number_of_tasks",
            documentation="number of tasks processed by celery.",
            labelnames=_labels,
            registry=self.registry,
        )

        # go to prometheus dashboard(http://localhost:9000/) & you can run queries like:
        # 1. container_memory_rss{name="celery_cli", container_label_com_docker_compose_service="celery_cli"}
        # 2. container_memory_rss{name=~"celery_cli|task_producer"}
        # 3. number_of_tasks_total{state="EXECUTED"}
        # 4. rate(number_of_tasks_total{task_name="MemTask"}[30s]) # task execution/queueing rate over the past 30seconds

    def notify(self, task_name) -> None:
        try:
            self.counter.labels(
                library="celery", task_name=task_name, state="EXECUTED"
            ).inc()  # Increment by 1
        finally:
            prometheus_client.push_to_gateway(
                "push_to_gateway:9091", job="BenchmarksHook", registry=self.registry
            )
