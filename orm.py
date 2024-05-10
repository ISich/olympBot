from db import session_factory, sync_engine
from models import Base, UsersOlympiads, UsersInfo, OlympiadsInfo, OlympiadsDates
from sqlalchemy import and_
from parser_1 import parse_first_page, parse_second_page, convert_date


class SyncOrm():
    @staticmethod
    def create_tables() -> None:
        Base.metadata.drop_all(sync_engine)
        sync_engine.echo = False
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = False


    @staticmethod
    def add_user_info(tg_id: str, grade: int, subjects: list[str], levels: list[int]) -> None:
        #добавляет пользователя с этими данными в табличку users_info
        with session_factory() as session:
            user = UsersInfo(tg_id=tg_id, grade=grade, subjects=subjects, levels=levels)
            session.add(user)
            session.commit()

    @staticmethod
    def get_olympiads_interesting_for_user(tg_id: str) -> list[str]:
        #возвращает список названий олимпиад по фильтрам юзера
        with session_factory() as session:
            userInfo = session.query(UsersInfo).filter(UsersInfo.tg_id == tg_id).first()
            subjects = userInfo.subjects
            levels = userInfo.levels
            olymps = session.query(OlympiadsInfo).filter(and_(OlympiadsInfo.subject.in_(subjects),
                                                             OlympiadsInfo.level.in_(levels))).all()
            res = list(map(str, olymps))
            return res

    @staticmethod
    def subscibe_on_all_olympiads(tg_id: str) -> None:
        #Должен добавить для конкретного user'a по его tg_id в табличку users_olumpiads все те олимпиады, которые подходят ему по фильтрам из его users_info
        with session_factory() as session:
            user_info = session.query(UsersInfo).filter(UsersInfo.tg_id == tg_id).first()
            subjects = user_info.subjects
            levels = user_info.levels
            olympiads = session.query(OlympiadsInfo).filter(
                OlympiadsInfo.subject.in_(subjects),
                OlympiadsInfo.level.in_(levels)
            ).all()
            for olympiad in olympiads:
                user = UsersOlympiads(tg_id=tg_id, followed_olymp=olympiad.olymp_id)
                session.add(user)
            session.commit()

    @staticmethod
    def get_olympiad_by_name(olympiad_name: str) -> OlympiadsInfo:
        # По имени олимпиады возвращает ее можельку, которую мы на постпроцессинге преобразуем в сообщение
        with session_factory() as session:
            olymp = session.query(OlympiadsInfo).filter(OlympiadsInfo.name == olympiad_name).first()
            return olymp

    @staticmethod
    def subscribe_on_olympiads_by_names(tg_id:str, olympiads_names: list[str]) -> None:
        # По массиву из имен олимпиал подписывает пользователя на олимпиады по имени и фильтрам, те добовляет в таблицу users_olumpiads соответствующие записи
        with session_factory() as session:
            userinfo = session.query(UsersInfo).filter(tg_id=tg_id).first()
            levels = userinfo.levels
            subjects = userinfo.subjects
            olymps = session.query(OlympiadsInfo).filter(OlympiadsInfo.subject.in_(subjects),
                                                         OlympiadsInfo.level.in_(levels)).all()
            for olymp in olymps:
                userinfo.followed_olymp.append(olymp[0])
            session.commit()

    @staticmethod
    def get_all_users_subscriptions() -> list[UsersOlympiads]:
        #Просто возвращает все такие модельки из базы
        with session_factory() as session:
            all_users_subs = session.query(UsersInfo).all()
            return all_users_subs

    @staticmethod
    def insert_data() -> None:
        with session_factory() as session:
            for line in parse_first_page():
                info = OlympiadsInfo(
                    olymp_id=int(line[0]),
                    name=line[1],
                    link=line[2],
                    subject=line[3],
                    level=int(line[4])
                )
                session.add(info)
            session.commit()
            for line in parse_second_page():
                if session.query(OlympiadsInfo).filter_by(olymp_id=int(line[0])).count() > 0:
                    date = OlympiadsDates(
                        olymp_id=int(line[0]),
                        stage_name=line[1],
                        date_from=convert_date(line[2]),
                        date_to=convert_date(line[3])
                    )
                    session.add(date)
                else:
                    print(f"No olymp_id found for {line[1]}")
            session.commit()