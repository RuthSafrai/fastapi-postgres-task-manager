from fastapi import HTTPException, status

from enums import Role
from models import User, Task


def is_admin(user: User) -> bool:
    return user.role == Role.admin


def can_read_all(user: User) -> bool:
    return user.role in (Role.admin, Role.secretary)


def forbidden(detail: str = "אין הרשאה לפעולה זו") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def ensure_can_read_task(task: Task, user: User) -> None:
    if not can_read_all(user) and task.user_id != user.id:
        raise forbidden()


def ensure_can_write_task(task: Task, user: User) -> None:
    # מזכיר לא כותב בכלל; משתמש רגיל כותב רק במשימות שלו; מנהל בכל מקום
    if is_admin(user):
        return
    if user.role == Role.secretary or task.user_id != user.id:
        raise forbidden()