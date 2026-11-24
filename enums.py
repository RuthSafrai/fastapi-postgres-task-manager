from enum import Enum


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Role(str, Enum):
    admin = "admin"          # מנהל: הכול
    secretary = "secretary"  # מזכיר: קריאה בלבד, כל הנתונים
    developer = "developer"  # משתמש רגיל: רק הנתונים שלו