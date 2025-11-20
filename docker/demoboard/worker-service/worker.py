import time
import json
import redis
from db import init_db

r = redis.Redis(host="redis", port=6379)
db = init_db()

print("Worker started, waiting for jobs...")

while True:
    _, message = r.blpop("jobs")
    job = json.loads(message)
    task_id = job["task_id"]

    print(f"Processing task {task_id}")
    time.sleep(5)

    curr = db.cursor()
    curr.execute("UPDATE tasks SET status='completed' WHERE id=%s", (task_id,))
    db.commit()

    print(f"Task {task_id} completed")
