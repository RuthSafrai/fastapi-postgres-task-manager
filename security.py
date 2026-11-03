import bcrypt



def hash_password(password: str) -> str:
    # bcrypt מוגבל ל-72 בייטים — חותכים כדי למנוע ValueError
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8")[:72], password_hash.encode("utf-8"))