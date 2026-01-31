from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config import DEMO_USERNAME, DEMO_PASSWORD_HASH
from security import verify_password
from auth import create_access_token, get_current_user

from database import SessionLocal
from models import Task as TaskModel

app = FastAPI()


# ----------------------------
# DB dependency
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Schemas (data shapes only)
# ----------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TaskCreate(BaseModel):
    id: int = Field(..., ge=0)
    title: str = Field(..., min_length=1)


# ----------------------------
# Routes
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    # 1) Username check
    if payload.username != DEMO_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # 2) Password check (plain password vs stored hash)
    if not DEMO_PASSWORD_HASH or not verify_password(payload.password, DEMO_PASSWORD_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # 3) Role (demo behavior)
    role = "admin"   # since this is your demo user

    # 4) Create token (MATCH auth.py signature)
    token = create_access_token(payload.username, role)

    return {"access_token": token, "token_type": "bearer"}


# PROTECTED endpoint example:
# If the token is missing/invalid, request will fail automatically.
@app.get("/me")
def me(user=Depends(get_current_user)):
    return {"user": user}


# Protect tasks endpoints too (recruiters LOVE seeing this)
@app.get("/tasks")
def get_tasks(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return db.query(TaskModel).all()


@app.post("/tasks")
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    existing = db.query(TaskModel).filter(TaskModel.id == task.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Task ID already exists")

    db_task = TaskModel(id=task.id, title=task.title)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}

