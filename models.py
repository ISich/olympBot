import datetime
from sqlalchemy import Integer, String, ARRAY, ForeignKey, ForeignKeyConstraint
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class UsersOlympiads(Base):
    __tablename__ = 'users_olympiads'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column(autoincrement=False)
    followed_olymp: Mapped[int]


class UsersInfo(Base):
    __tablename__ = 'users_info'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str]
    grade: Mapped[int]
    subjects: Mapped[list[str]] = mapped_column(ARRAY(String(256)))
    levels: Mapped[list[int]] = mapped_column(ARRAY(Integer))

class OlympiadsInfo(Base):
    __tablename__ = 'olympiads_info'

    olymp_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    link: Mapped[str]
    level: Mapped[int]
    subject: Mapped[str]

class OlympiadsDates(Base):
    __tablename__ = 'olympiads_dates'

    olymp_id: Mapped[int] = mapped_column(primary_key=True)
    stage_name: Mapped[str]
    date_from: Mapped[datetime.datetime]
    date_to: Mapped[datetime.datetime]

    __table_args__ = (
        ForeignKeyConstraint(['olymp_id'], ['olympiads_info.olymp_id']),
    )
