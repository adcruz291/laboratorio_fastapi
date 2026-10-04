from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    contactos: list["Contacto"] = Relationship(back_populates="owner")


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class Token(SQLModel):
    access_token: str
    token_type: str


from src.models.agenda import Contacto  # noqa: E402
