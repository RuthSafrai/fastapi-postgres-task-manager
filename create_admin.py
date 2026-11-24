"""יוצר מנהל ראשון, או מקדם משתמש קיים למנהל.

הרצה: python create_admin.py
(יוצרים את המנהל הראשון כאן, כי יצירת משתמשים דורשת מנהל.)
"""
from getpass import getpass

import models
from database import SessionLocal
from enums import Role
from security import hash_password


def main() -> None:
    db = SessionLocal()
    try:
        username = input("שם משתמש: ").strip()
        user = db.query(models.User).filter(models.User.username == username).first()

        if user:
            user.role = Role.admin.value
            db.commit()
            print(f"המשתמש '{username}' קודם למנהל.")
            return

        name = input("שם מלא: ").strip()
        email = input("אימייל: ").strip()
        password = getpass("סיסמה: ")
        db.add(
            models.User(
                name=name,
                email=email,
                username=username,
                password=hash_password(password),
                role=Role.admin.value,
            )
        )
        db.commit()
        print(f"נוצר מנהל חדש: '{username}'.")
    finally:
        db.close()


if __name__ == "__main__":
    main()