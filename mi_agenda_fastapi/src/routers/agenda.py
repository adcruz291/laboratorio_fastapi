from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.auth.dependencies import get_current_user
from src.database import get_session
from src.models.agenda import Contacto, ContactoCreate, ContactoRead, ContactoUpdate
from src.models.user import User

router = APIRouter(prefix="/contactos", tags=["contactos"])

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[User, Depends(get_current_user)]


def _get_own(session: Session, contacto_id: int, user: User) -> Contacto:
    contacto = session.get(Contacto, contacto_id)
    if not contacto or contacto.user_id != user.id:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return contacto


@router.get("/", response_model=list[ContactoRead])
def listar(session: SessionDep, user: UserDep):
    return session.exec(select(Contacto).where(Contacto.user_id == user.id)).all()


@router.get("/{contacto_id}", response_model=ContactoRead)
def obtener(contacto_id: int, session: SessionDep, user: UserDep):
    return _get_own(session, contacto_id, user)


@router.post("/", response_model=ContactoRead, status_code=201)
def crear(data: ContactoCreate, session: SessionDep, user: UserDep):
    contacto = Contacto(**data.model_dump(), user_id=user.id)
    session.add(contacto)
    session.commit()
    session.refresh(contacto)
    return contacto


@router.put("/{contacto_id}", response_model=ContactoRead)
def actualizar(contacto_id: int, data: ContactoUpdate, session: SessionDep, user: UserDep):
    contacto = _get_own(session, contacto_id, user)
    contacto.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(contacto)
    session.commit()
    session.refresh(contacto)
    return contacto


@router.delete("/{contacto_id}", status_code=204)
def eliminar(contacto_id: int, session: SessionDep, user: UserDep):
    session.delete(_get_own(session, contacto_id, user))
    session.commit()
