from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class ContactoBase(SQLModel):
    nombre: str
    telefono: str
    email: Optional[str] = None


class Contacto(ContactoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    owner: Optional["User"] = Relationship(back_populates="contactos")


class ContactoCreate(ContactoBase):
    pass


class ContactoUpdate(SQLModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None


class ContactoRead(ContactoBase):
    id: int
    user_id: int


from src.models.user import User  # noqa: E402
