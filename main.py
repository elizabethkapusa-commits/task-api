from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session

from auth import TokenUser, create_access_token, get_current_user, require_role
from database import get_db
from models import User, Task as TaskModel
from security import verify_password


app = FastAPI()


# -----------------------------
# Schemas
# -----------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    completed: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Helpers
# -----------------------------
def get_task_or_404(db: Session, task_id: int) -> TaskModel:
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


def enforce_task_access(task: TaskModel, current_user: TokenUser) -> None:
    if current_user.role == "admin":
        return

    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task",
        )


# -----------------------------
# Routes
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/me")
def me(current_user: Annotated[TokenUser, Depends(get_current_user)]):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }


@app.get("/admin-test")
def admin_test(
    admin_user: Annotated[TokenUser, Depends(require_role("admin"))],
):
    return {
        "ok": True,
        "message": f"{admin_user.email} is an admin",
    }


@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[TokenUser, Depends(get_current_user)],
):
    query = db.query(TaskModel)

    if current_user.role != "admin":
        query = query.filter(TaskModel.owner_id == current_user.id)

    tasks = query.order_by(TaskModel.id.asc()).all()
    return tasks


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[TokenUser, Depends(get_current_user)],
):
    db_task = TaskModel(
        title=payload.title,
        completed=False,
        owner_id=current_user.id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[TokenUser, Depends(get_current_user)],
):
    task = get_task_or_404(db, task_id)
    enforce_task_access(task, current_user)
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[TokenUser, Depends(get_current_user)],
):
    task = get_task_or_404(db, task_id)
    enforce_task_access(task, current_user)

    if payload.title is not None:
        task.title = payload.title

    if payload.completed is not None:
        task.completed = payload.completed

    db.commit()
    db.refresh(task)

    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[TokenUser, Depends(get_current_user)],
):
    task = get_task_or_404(db, task_id)
    enforce_task_access(task, current_user)

    db.delete(task)
    db.commit()

    return {"message": "Task deleted"}
