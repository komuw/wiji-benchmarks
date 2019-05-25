import os
import celery

"""
run as:
    1. celery worker -A tasks --concurrency=3 --loglevel=DEBUG
"""


host = "localhost"
port = 6379
password = None
if os.environ.get("IN_DOCKER"):
    host = os.environ["REDIS_HOST"]
    port = os.environ["REDIS_PORT"]
    password = os.environ.get("REDIS_PASSWORD", None)


# broker
CELERY_BROKER_URL = "redis://{host}:{port}/{db_number}".format(
    password=password, host=host, port=port, db_number=0
)
app = celery.Celery("tasks", broker=CELERY_BROKER_URL)


class MyTask(app.Task):
    name = "MyTask"

    def run(self, a, b):
        res = a + b
        print("res: ", res)
        return res


app.tasks.register(MyTask())
