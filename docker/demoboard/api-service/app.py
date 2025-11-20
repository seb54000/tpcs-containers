from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import init_db, get_db
from worker_queue import publish_job

app = FastAPI()
db = init_db()

class Task(BaseModel):
    id: int | None = None
    title: str
    status: str = "pending"

@app.post("/tasks")
def create_task(task: Task):
    curr = get_db()
    curr.execute("INSERT INTO tasks (title, status) VALUES (%s, %s) RETURNING id",
                 (task.title, task.status))
    task.id = curr.fetchone()[0]
    return task

@app.get("/tasks")
def list_tasks():
    curr = get_db()
    curr.execute("SELECT id, title, status FROM tasks")
    rows = curr.fetchall()
    return [{"id": r[0], "title": r[1], "status": r[2]} for r in rows]

@app.post("/tasks/{task_id}/start-job")
def start_job(task_id: int):
    curr = get_db()
    curr.execute("UPDATE tasks SET status='processing' WHERE id=%s", (task_id,))
    publish_job({"task_id": task_id})
    return {"message": "Job started", "task_id": task_id}
