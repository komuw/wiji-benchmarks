import asyncio
from unittest import TestCase, mock

import wiji

from benchmarks.tasks import CPUTask


class TestTasks(TestCase):
    """
    TestCase to showcase how users of `wiji` can write tests for their code that is using wiji

    run tests as:
        python -m unittest discover -v -s .
    run one testcase as:
        python -m unittest -v tests.test_tasks.TestTasks.test_something
    """

    @staticmethod
    def _run(coro):
        """
        helper function that runs any coroutine in an event loop
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

    def test_cpu_task(self):
        with mock.patch.object(CPUTask, "the_broker", wiji.broker.InMemoryBroker()), mock.patch(
            "benchmarks.tasks.hashlib.blake2b"
        ) as mock_blake2b:
            task = CPUTask()
            task.synchronous_delay()

            worker = wiji.Worker(the_task=task)
            self._run(worker.consume_tasks(TESTING=True))

            self.assertTrue(mock_blake2b.called)
