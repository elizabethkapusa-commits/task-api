from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()

class Task(BaseModel):
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1)

tasks: List[Task] = []

@app.get("/health")
def health():
    logger.info("Health check called")
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    logger.info("Fetching all tasks")
    return tasks

@app.post("/tasks")
def create_task(task: Task):
    logger.info(f"Creating task with id={task.id}")

    for t in tasks:
        if t.id == task.id:
            logger.warning(f"Duplicate task id={task.id}")
            raise HTTPException(status_code=400, detail="Task ID already exists")

    tasks.append(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    logger.info(f"Deleting task id={task_id}")

    for t in tasks:
        if t.id == task_id:
            tasks.remove(t)
            return {"message": "Task deleted"}

    logger.error(f"Task id={task_id} not found")
    raise HTTPException(status_code=404, detail="Task not found")

