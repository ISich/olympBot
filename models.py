import datetime
from sqlalchemy import Integer, String, ARRAY, ForeignKey
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class UsersOrm(Base):
    __tablename__ = 'users_olympiads'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column(autoincrement=False)
    followed_olymp: Mapped[int]


class UsersInfo(Base):
    __tablename__ = 'users_info'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str]
    grade: Mapped[int]
    subjects: Mapped[list[str]]
    levels: Mapped[list[int]]

class OlympiadsInfo(Base):
    __tablename__ = 'olympiads_info'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    olymp_id: Mapped[int]
    name: Mapped[str]
    levels: Mapped[list[int]]
    subjects: Mapped[list[str]]


class OlympiadsDates(Base):
    __tablename__ = 'olympiads_dates'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    olymp_id: Mapped[int] = mapped_column(ForeignKey='olympiads_info.olymp_id')
    stage_name: Mapped[str]
    date_from: Mapped[datetime.datetime]
    date_to: Mapped[datetime.datetime]