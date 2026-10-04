from pathlib import Path
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from src.auth.dependencies import get_current_user_cookie
from src.auth.security import create_access_token, hash_password, verify_password
from src.database import get_session
from src.models.agenda import Contacto
from src.models.user import User

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[Optional[User], Depends(get_current_user_cookie)]


def _login_redirect(username: str) -> RedirectResponse:
    response = RedirectResponse("/agenda", status_code=303)
    response.set_cookie(
        "access_token", create_access_token(username), httponly=True, samesite="lax"
    )
    return response


@router.get("/")
def index():
    return RedirectResponse("/agenda")


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login")
def login(
    request: Request,
    session: SessionDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request, "login.html", {"error": "Usuario o contraseña incorrectos"}, status_code=401
        )
    return _login_redirect(user.username)


@router.post("/registro")
def registro(
    request: Request,
    session: SessionDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    if session.exec(select(User).where(User.username == username)).first():
        return templates.TemplateResponse(
            request, "login.html", {"error": "El usuario ya existe"}, status_code=400
        )
    user = User(username=username, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    return _login_redirect(user.username)


@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/agenda")
def agenda(request: Request, session: SessionDep, user: UserDep):
    if not user:
        return RedirectResponse("/login")
    contactos = session.exec(select(Contacto).where(Contacto.user_id == user.id)).all()
    return templates.TemplateResponse(
        request, "agenda.html", {"user": user, "contactos": contactos}
    )


@router.post("/agenda")
def agregar(
    session: SessionDep,
    user: UserDep,
    nombre: Annotated[str, Form()],
    telefono: Annotated[str, Form()],
    email: Annotated[str, Form()] = "",
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    session.add(
        Contacto(nombre=nombre, telefono=telefono, email=email or None, user_id=user.id)
    )
    session.commit()
    return RedirectResponse("/agenda", status_code=303)
