"""unique username and comments cascade

Revision ID: 178bfc0cb4ab
Revises: 98ddc5a303aa
Create Date: 2026-11-24 22:17:29.034430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '178bfc0cb4ab'
down_revision: Union[str, Sequence[str], None] = '98ddc5a303aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. שינוי שם העמודה, בלי לאבד נתונים
    op.alter_column("users", "userName", new_column_name="username")

    # 2. ניקוי נתונים שיפרו את האילוצים: NULL וכפילויות
    #    כל שורה כזאת מקבלת שם ייחודי לפי ה-id שלה (user_5)
    op.execute("""
        UPDATE users
        SET username = 'user_' || id
        WHERE username IS NULL
           OR username IN (
               SELECT username FROM users GROUP BY username HAVING COUNT(*) > 1
           )
    """)

    # 3. חובה וייחודי
    op.alter_column("users", "username", existing_type=sa.String(), nullable=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # 4. מחיקה בשרשרת: מחיקת משימה מוחקת את התגובות שלה
    op.drop_constraint("comments_task_id_fkey", "comments", type_="foreignkey")
    op.create_foreign_key(
        "comments_task_id_fkey", "comments", "tasks",
        ["task_id"], ["id"], ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("comments_task_id_fkey", "comments", type_="foreignkey")
    op.create_foreign_key(
        "comments_task_id_fkey", "comments", "tasks", ["task_id"], ["id"]
    )

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.alter_column("users", "username", existing_type=sa.String(), nullable=True)
    op.alter_column("users", "username", new_column_name="userName")