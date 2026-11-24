from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from enums import TaskStatus, TaskPriority
import auth
import models
import schemas
from database import get_db
from security import hash_password
app = FastAPI(title="מערכת ניהול משימות")


# ---------- Users ----------
@app.post("/users",response_model=schemas.UserOut,status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="האימייל כבר קיים")
    existing_username = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if existing_username:
        raise HTTPException(status_code=400, detail="שם המשתמש כבר קיים")
    new_user = models.User(
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        username=user.username,
        password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users", response_model=list[schemas.UserOut])
def get_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return db.query(models.User).order_by(models.User.id).offset(skip).limit(limit).all()


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="המשתמש לא נמצא")
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="המשתמש לא נמצא")
    has_tasks = db.query(models.Task).filter(models.Task.user_id == user_id).first()
    has_comments = (
        db.query(models.Comment).filter(models.Comment.user_id == user_id).first()
    )
    if has_tasks or has_comments:
        raise HTTPException(
            status_code=409,
            detail="לא ניתן למחוק משתמש שיש לו משימות או תגובות",
        )
    db.delete(user)
    db.commit()
    return {"message": "המשתמש נמחק"}


# ---------- Projects ----------
@app.post("/projects", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    new_project = models.Project(**project.model_dump())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@app.get("/projects", response_model=list[schemas.ProjectOut])
def get_projects(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return (
        db.query(models.Project)
        .order_by(models.Project.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

@app.get("/projects/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="הפרויקט לא נמצא")
    return project


# ---------- Tasks ----------
@app.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    # בדיקת קיום הישויות המקושרות לפני יצירה
    if task.user_id is not None and not db.get(models.User, task.user_id):
        raise HTTPException(status_code=404, detail="המשתמש לא נמצא")
    if task.project_id is not None and not db.get(models.Project, task.project_id):
        raise HTTPException(status_code=404, detail="הפרויקט לא נמצא")

    new_task = models.Task(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks", response_model=list[schemas.TaskOut])
def get_tasks(
    db: Session = Depends(get_db),
    status_filter: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    user_id: int | None = None,
    project_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    query = db.query(models.Task)
    if status_filter is not None:
        query = query.filter(models.Task.status == status_filter.value)
    if priority is not None:
        query = query.filter(models.Task.priority == priority.value)
    if user_id is not None:
        query = query.filter(models.Task.user_id == user_id)
    if project_id is not None:
        query = query.filter(models.Task.project_id == project_id)
    return query.order_by(models.Task.id).offset(skip).limit(limit).all()

@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="המשימה לא נמצאה")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task_in: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="המשימה לא נמצאה")

    data = task_in.model_dump(exclude_unset=True)
    if "user_id" in data and data["user_id"] is not None and not db.get(models.User, data["user_id"]):
        raise HTTPException(status_code=404, detail="המשתמש לא נמצא")
    if "project_id" in data and data["project_id"] is not None and not db.get(models.Project, data["project_id"]):
        raise HTTPException(status_code=404, detail="הפרויקט לא נמצא")

    for field, value in data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="המשימה לא נמצאה")
    db.delete(task)
    db.commit()
    return {"message": "המשימה נמחקה"}


# ---------- Comments ----------
@app.post("/tasks/{task_id}/comments", response_model=schemas.CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(task_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    if not db.get(models.Task, task_id):
        raise HTTPException(status_code=404, detail="המשימה לא נמצאה")
    if not db.get(models.User, comment.user_id):
        raise HTTPException(status_code=404, detail="המשתמש לא נמצא")

    new_comment = models.Comment(
        content=comment.content, task_id=task_id, user_id=comment.user_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@app.get("/tasks/{task_id}/comments", response_model=list[schemas.CommentOut])
def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    if not db.get(models.Task, task_id):
        raise HTTPException(status_code=404, detail="המשימה לא נמצאה")
    return (
        db.query(models.Comment)
        .filter(models.Comment.task_id == task_id)
        .order_by(models.Comment.created_at.asc(), models.Comment.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

app.include_router(auth.router)
