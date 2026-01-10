from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Data model
class Task(BaseModel):
    id: int
    title: str

# In-memory storage (temporary)
tasks: List[Task] = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.post("/tasks")
def create_task(task: Task):
    # Prevent duplicate IDs
    for t in tasks:
        if t.id == task.id:
            raise HTTPException(status_code=400, detail="Task ID already exists")

    tasks.append(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for t in tasks:
        if t.id == task_id:
            tasks.remove(t)
            return {"message": "Task deleted"}

    raise HTTPException(status_code=404, detail="Task not found")
