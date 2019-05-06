import json


result_head = """
Queuing metrics results:     
| Task name      |  Numober of tasks queued | Time to queue 1 task(sec) | Number of tasks dequeued | Time to execute 1 task(sec) |
| :---           |  ---:                    |  ---:                     |   ---:                   |  ---:                       |    
"""

result_body = """| {task_name}    |  {tasks_queued}          |  {queuing_duration}       |  {tasks_dequeued}        |  {execution_duration}       |
"""


def cool():
    with open("./tmp/metrics/final_queuing_metrics.json", mode="r") as f:
        x = f.read()
        final_queuing_metrics = json.loads(x)
        return final_queuing_metrics


final_queuing_metrics = cool()


all_res = []
for i in final_queuing_metrics.keys():
    _result = result_body.format(
        task_name=i,
        tasks_queued=final_queuing_metrics[i].get("tasks_queued"),
        queuing_duration=final_queuing_metrics[i].get("queuing_duration"),
        tasks_dequeued=final_queuing_metrics[i].get("tasks_dequeued"),
        execution_duration=final_queuing_metrics[i].get("execution_duration"),
    )
    all_res.append(_result)


final_markdwon = result_head + "".join(all_res)
with open("./tmp/metrics/ala.md", mode="w") as f:
    f.write(final_markdwon)
