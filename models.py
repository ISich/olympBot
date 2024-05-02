import datetime
from sqlalchemy import Integer, String, ARRAY
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class UsersOrm(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    followed_olymps: Mapped[list[int]] = mapped_column(ARRAY(Integer))


class OlympiadsOrm(Base):
    __tablename__ = 'olymps'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    level: Mapped[int] = mapped_column(default=0)
    subject: Mapped[str] = mapped_column(String(256), nullable=False)
    selections_start: Mapped[datetime.datetime]
    selections_end: Mapped[datetime.datetime]
    final_start: Mapped[datetime.datetime]
    final_end: Mapped[datetime.datetime]
    count_selections: Mapped[int]