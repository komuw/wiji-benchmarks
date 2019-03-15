import wiji

from . import tasks

# run using wiji-cli as:
#   wiji-cli --config benchmarks.wiji_app.myConf
myConf = wiji.conf.WijiConf(tasks=[tasks.network_io_task, tasks.disk_io_task, tasks.cpu_bound_task])
