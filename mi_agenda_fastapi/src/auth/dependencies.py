from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from src.auth.security import decode_token
from src.database import get_session
from src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _get_user(session: Session, token: str | None) -> User | None:
    username = decode_token(token) if token else None
    if not username:
        return None
    return session.exec(select(User).where(User.username == username)).first()


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    user = _get_user(session, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user_cookie(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> User | None:
    return _get_user(session, request.cookies.get("access_token"))
