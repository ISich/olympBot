import datetime
from sqlalchemy import Integer, String, ARRAY, ForeignKey
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class UsersInfo(Base):
    __tablename__ = 'users_info'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column()
    grade: Mapped[int]
    subjects: Mapped[list[str]] = mapped_column(ARRAY(String(256)))
    levels: Mapped[list[int]] = mapped_column(ARRAY(Integer))

    olympiads = relationship("UsersOlympiads", back_populates="user", cascade="all, delete-orphan")


class UsersOlympiads(Base):
    __tablename__ = 'users_olympiads'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column(ForeignKey(UsersInfo.tg_id))
    followed_olymp: Mapped[int]

    user = relationship("UsersInfo", back_populates="olympiads")


class OlympiadsInfo(Base):
    __tablename__ = 'olympiads_info'

    olymp_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    link: Mapped[str]
    level: Mapped[int]
    subject: Mapped[str]


class OlympiadsDates(Base):
    __tablename__ = 'olympiads_dates'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    olymp_id: Mapped[int] = mapped_column(ForeignKey(OlympiadsInfo.olymp_id))
    stage_name: Mapped[str]
    date_from: Mapped[datetime.datetime]
    date_to: Mapped[datetime.datetime]
