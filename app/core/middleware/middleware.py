from infrastructure.configuration.cors_config import get_cors_middleware


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Dict
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/amin-travels-hajj-core/api/v1/public/login")  # or wherever your login endpoint is

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def configure_middleware(app):
    get_cors_middleware(app)


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )