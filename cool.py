import json


result = """
Queuing metrics results:     
| Task name      |  Numober of tasks queued | Time to queue 1 task(sec) | Number of tasks dequeued | Time to execute 1 task(sec) |
| :---           |  ---:                    |  ---:                     |   ---:                   |  ---:                       |       
| {task_name}    |  {tasks_queued}          |  {queuing_duration}       |  {tasks_dequeued}        |  {execution_duration}       |
"""

#   "task_name-DiskIOTask": {
#     "tasks_queued": 4243,
#     "queuing_duration": 0.05,
#     "tasks_dequeued": 4243,
#     "execution_duration": 0.01
#   }
# with open("./tmp/metrics/ala.md", mode="w") as f:
#     f.write(x.format(sec=90))


def cool():
    with open("./tmp/metrics/final_queuing_metrics.json", mode="r") as f:
        x = f.read()
        final_queuing_metrics = json.loads(x)
        return final_queuing_metrics


final_queuing_metrics = cool()

for i in final_queuing_metrics.keys():
    print(i)

    _result = result.format(
        task_name=i,
        tasks_queued=final_queuing_metrics[i].get("tasks_queued"),
        queuing_duration=final_queuing_metrics[i].get("queuing_duration"),
        tasks_dequeued=final_queuing_metrics[i].get("tasks_dequeued"),
        execution_duration=final_queuing_metrics[i].get("execution_duration"),
    )
import pdb

pdb.set_trace()
print()
print()
print("l")

with open("./tmp/metrics/ala.md", mode="w") as f:
    f.write(_result)
