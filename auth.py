from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db
from models import User


security = HTTPBearer()


class TokenUser(BaseModel):
    id: int
    email: str
    role: str


def create_access_token(user: User) -> str:
    payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        sub = payload.get("sub")
        user_id = payload.get("user_id")
        role = payload.get("role")

        if not sub or user_id is None or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing required claims",
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> TokenUser:
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    email = payload.get("sub")
    role = payload.get("role")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if user.email != email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject does not match user",
        )

    return TokenUser(
        id=user.id,
        email=user.email,
        role=user.role,
    )


def require_role(*allowed_roles: str) -> Callable:
    def _checker(
        current_user: Annotated[TokenUser, Depends(get_current_user)],
    ) -> TokenUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _checker
