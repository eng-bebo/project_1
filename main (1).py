from typing import Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import Task
from backend.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Tracker API",
    description=(
        
    ),
    version="1.0.0",
)


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    tags=["Tasks"],
)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:

    new_task = Task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)  
    return new_task

@app.get(
    "/tasks",
    response_model=TaskListResponse,
    summary="List all tasks",
    tags=["Tasks"],
)
def list_tasks(
    priority: Optional[Literal["low", "medium", "high"]] = Query(
        default=None,
        description="Filter by priority level.",
    ),
    completed: Optional[bool] = Query(
        default=None,
        description="Filter by completion status.",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Maximum number of tasks to return (1–200).",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of tasks to skip (for pagination).",
    ),
    db: Session = Depends(get_db),
) -> dict:

    query = db.query(Task)

    if priority is not None:
        query = query.filter(Task.priority == priority)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    return {"total": total, "tasks": tasks}

@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    tags=["Tasks"],
)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    """Return a single task or raise **404** if it does not exist."""
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} was not found.",
        )
    return task

@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    tags=["Tasks"],
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
) -> Task:
    """
    Partially update an existing task.

    Only the fields present in the request body are changed;
    omitted fields retain their current values.
    """
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} was not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    tags=["Tasks"],
)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} was not found.",
        )
    db.delete(task)
    db.commit()

@app.get("/", tags=["Health"], summary="Health check")
def root() -> dict:
    return {"status": "ok", "message": "Task Tracker API is running."}
