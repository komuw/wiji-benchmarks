import wiji

from benchmarks import tasks

# Usage:
#   wiji-cli --app benchmarks.wiji_app.myApp

myApp = wiji.app.App(
    task_classes=[
        tasks.NetworkIOTask,
        tasks.DiskIOTask,
        tasks.CPUTask,
        tasks.MemTask,
        tasks.DividerTask,
        tasks.AdderTask,
    ]
)
