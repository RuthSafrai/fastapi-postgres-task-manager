from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import schemas

app = FastAPI(title="מערכת ניהול משימות")


# תלות: פותחת סשן לכל בקשה וסוגרת בסיומה
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Users ----------
@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="האימייל כבר קיים")
    new_user = models.User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users", response_model=list[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


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
    db.delete(user)
    db.commit()
    return {"message": "המשתמש נמחק"}