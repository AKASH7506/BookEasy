import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

SECRET_KEY = os.getenv("SECRET_KEY", "bookeasy-development-secret-change-me")
ALGORITHM = "HS256"
EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def hash_password(password): return pwd.hash(password)
def verify_password(password, hashed): return pwd.verify(password, hashed)
def create_token(user):
    return jwt.encode({"sub": str(user.id), "exp": datetime.utcnow()+timedelta(minutes=EXPIRE)}, SECRET_KEY, algorithm=ALGORITHM)

def current_user(token: str = Depends(oauth), db: Session = Depends(get_db)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = int(data["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, uid)
    if not user: raise HTTPException(401, "User not found")
    return user

def admin_user(user=Depends(current_user)):
    if user.role != "admin": raise HTTPException(403, "Admin access required")
    return user
