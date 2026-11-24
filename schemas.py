from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, date


# ---------- Users ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "developer"
    is_active: bool = True
    userName: Optional[str] = None
    password: str



class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    userName: Optional[str] = None

    class Config:
        from_attributes = True

class UserResponse (BaseModel):
    id: int
    username: str

# ---------- Projects ----------
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Tasks ----------
class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "low"
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    due_date: date
    estimated_hours: int = Field(gt=0)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = Field(default=None, gt=0)

    # שדות NOT NULL במסד: אפשר לא לשלוח אותם, אבל אי אפשר לשלוח null
    @field_validator("title", "status", "priority", "due_date", "estimated_hours")
    @classmethod
    def not_null(cls, value):
        if value is None:
            raise ValueError("השדה לא יכול להיות null")
        return value


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    created_at: datetime
    due_date: date
    estimated_hours: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
# ---------- Comments ----------
class CommentCreate(BaseModel):
    content: str
    user_id: int


class CommentOut(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True