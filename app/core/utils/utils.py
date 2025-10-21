import os
from datetime import datetime, timedelta
from typing import Union, Any, Dict, Optional

import bcrypt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/amin-travels-hajj-core/api/v1/public/login")
RESERVED_CLAIMS = {"exp", "iat", "nbf", "jti"}

# Load environment variables safely
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")


# Password hashing functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return pwd_context.verify(password, hashed_pass)


# Token creation
def create_access_token(subject: Union[str, Any], role: str, agency_name: str = None,
                        expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject), "role": role, "agency_name": agency_name}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: Union[str, Any], role: str, agency_name: str = None,
                         expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject), "role": role, "agency_name": agency_name}
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def _now_utc() -> datetime:
    return datetime.utcnow()


def _strip_reserved(claims: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in claims.items() if k not in RESERVED_CLAIMS}


def rotate_tokens(
        refresh_token: str,
        access_expires: Optional[timedelta] = None,
        refresh_expires: Optional[timedelta] = None
) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            refresh_token,
            JWT_REFRESH_SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    base_claims = _strip_reserved(payload)

    now = _now_utc()
    access_exp = now + (access_expires or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_exp = now + (refresh_expires or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))

    new_access_token = jwt.encode(
        {**base_claims, "exp": access_exp},
        JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )
    new_refresh_token = jwt.encode(
        {**base_claims, "exp": refresh_exp},
        JWT_REFRESH_SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_exp.timestamp() - now.timestamp()),
    }


def verify_pilgrim_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token_for_pilgrim(subject: Union[str, Any], mobile_no: str, tracking_id: str,
                                    expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject), "mobile_no": mobile_no, "tracking_id": tracking_id}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token_for_pilgrim(subject: Union[str, Any], mobile_no: str, tracking_id: str,
                                     expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject), "mobile_no": mobile_no, "tracking_id": tracking_id}
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def create_access_token_for_admin_user(subject: Union[str, Any], role: str, mobile_no: str, code: str, email: str,
                                       agency_name: str, expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject), "role": role, "agency_name": agency_name, "mobile_no": mobile_no,
                 "code": code, "email": email}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token_for_admin_user(subject: Union[str, Any], role: str, mobile_no: str, code: str, email: str,
                                        agency_name: str, expires_delta: timedelta = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject), "role": role, "agency_name": agency_name, "mobile_no": mobile_no,
                 "code": code, "email": email}
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
