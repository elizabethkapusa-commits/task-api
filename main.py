from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging

from database import SessionLocal
from models import Task as TaskModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class Task(BaseModel):
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()

@app.post("/tasks")
def create_task(task: Task, db: Session = Depends(get_db)):
    existing = db.query(TaskModel).filter(TaskModel.id == task.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Task ID already exists")

    db_task = TaskModel(id=task.id, title=task.title)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}

