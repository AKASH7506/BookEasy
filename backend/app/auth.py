
import os
from datetime import datetime, timedelta
from types import SimpleNamespace

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from .firestore_db import get_all_documents


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "bookeasy-development-secret-change-me"
)
ALGORITHM = "HS256"
EXPIRE = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)

pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth = OAuth2PasswordBearer(
    tokenUrl="api/auth/login"
)


def hash_password(password):
    return pwd.hash(password)


def verify_password(password, hashed):
    return pwd.verify(password, hashed)


def create_token(user):
    return jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.utcnow() + timedelta(minutes=EXPIRE)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def current_user(token: str = Depends(oauth)):
    try:
        data = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        uid = str(data["sub"])

    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    users = get_all_documents("users")

    for user in users:
        if (
            str(user.get("id")) == uid
            or user.get("_doc_id") == uid
        ):
            return SimpleNamespace(**user)

    raise HTTPException(
        status_code=401,
        detail="User not found"
    )


def admin_user(user=Depends(current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user
