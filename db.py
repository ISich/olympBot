from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Olymp(Base):
    __tablename__ = 'olymps'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    level = Column(Integer)
    subject = Column(String(100))
    count_selections = Column('count selections', Integer)

    @classmethod
    def get_all_olymps(cls, session):
        return session.query(cls).all()

    @classmethod
    def get_olymps_by_subject(cls, session, subject):
        return session.query(cls).filter_by(subject=subject).all()

class Date(Base):
    __tablename__ = 'dates'

    id = Column(Integer, primary_key=True)
    selections_start = Column(Date)
    selections_end = Column(Date)
    final_start = Column(Date)
    final_end = Column(Date)

    @classmethod
    def get_all_dates(cls, session):
        return session.query(cls).all()


engine = create_engine('postgresql://postgres:postgres@localhost:5433/olympiads')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

all_olymps = Olymp.get_all_olymps(session)
for olymp in all_olymps:
    print(f'{olymp.name}, {olymp.subject}')

# Многострочные комментарии не нужны, так как строки кода уже закомментированы
# math_olymps = Olymp.get_olymps_by_subject(session, "Mathematics")
# for olymp in math_olymps:
#     print(f'{olymp.name}, Level: {olymp.level}')

# all_dates = Date.get_all_dates(session)
# for date in all_dates:
#     print(f'Start: {date.selections_start}, End: {date.final_end}')
