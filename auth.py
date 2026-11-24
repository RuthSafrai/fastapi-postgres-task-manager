from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User
from schemas import Token
from security import verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    username = form_data.username.strip()

    user = (
        db.query(User)
        .filter(
            or_(
                User.userName == username,
                User.email == username,
            )
        )
        .order_by(User.id.desc())   # האחרון שנרשם, לא שרירותי
        .first()
    )

    if user is None or not user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="פרטי התחברות שגויים",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        ok = verify_password(form_data.password, user.password)
    except Exception as e:
        # hash פגום במסד — לא 500, אלא 401 עם לוג
        print("verify_password failed:", e)
        ok = False

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="פרטי התחברות שגויים",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(user.id))
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="טוקן לא תקין או שפג תוקפו",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="משתמש לא קיים")
    return user