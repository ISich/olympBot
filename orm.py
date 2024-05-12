from db import session_factory, sync_engine
from models import Base, UsersOlympiads, UsersInfo, OlympiadsInfo, OlympiadsDates
from sqlalchemy import and_
from parser_1 import parse_first_page, parse_second_page, convert_date


class SyncOrm():
    @staticmethod
    def create_tables() -> None:
        OlympiadsDates.__table__.drop(sync_engine)
        OlympiadsInfo.__table__.drop(sync_engine)
        sync_engine.echo = False
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = True


    @staticmethod
    def add_user_info(tg_id: str, grade: int, subjects: list[str], levels: list[int]) -> None:
        #добавляет пользователя с этими данными в табличку users_info
        with session_factory() as session:
            user = UsersInfo(
                tg_id=tg_id,
                grade=grade,
                subjects=subjects,
                levels=levels
            )
            session.add(user)
            session.commit()

    @staticmethod
    def get_olympiads_interesting_for_user(tg_id: str) -> list[str]:
        #возвращает список названий олимпиад по фильтрам юзера
        with session_factory() as session:
            userInfo = session.query(UsersInfo).filter(UsersInfo.tg_id == tg_id).first()
            subjects = userInfo.subjects
            levels = userInfo.levels
            olymps = [res[0] for res in session.query(OlympiadsInfo.short_name).filter(and_(OlympiadsInfo.subject.in_(subjects),
                                                             OlympiadsInfo.level.in_(levels))).all()]
            return olymps

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
                user = UsersOlympiads(
                    tg_id=tg_id,
                    followed_olymp=olympiad.olymp_id
                )
                session.add(user)
            session.commit()

    @staticmethod
    def get_olympiad_by_name(olympiad_name: str) -> OlympiadsInfo:
        # По имени олимпиады возвращает ее можельку, которую мы на постпроцессинге преобразуем в сообщение
        with session_factory() as session:
            olymp = session.query(OlympiadsInfo).filter(OlympiadsInfo.name == olympiad_name).first()
            return olymp

    @staticmethod
    def subscribe_on_olympiads_by_names(tg_id: str, olympiads_names: list[str]) -> None:
        # По массиву из имен олимпиал подписывает пользователя на олимпиады по имени и фильтрам, те добовляет в таблицу users_olumpiads соответствующие записи
        with session_factory() as session:
            userinfo = session.query(UsersInfo).filter(tg_id=tg_id).first()
            levels = userinfo.levels
            subjects = userinfo.subjects
            olymps = session.query(OlympiadsInfo).filter(OlympiadsInfo.subject.in_(subjects),
                                                         OlympiadsInfo.level.in_(levels)).all()
            for olymp in olymps:
                user = UsersOlympiads(
                    tg_id=tg_id,
                    followed_olymp=olymp.olymp_id
                )
                session.add(user)
            session.commit()
    
    @staticmethod
    def subscribe_on_olympiads_by_ids(tg_id: str, ids: list[int]) -> None:
        # По массиву из имен олимпиал подписывает пользователя на олимпиады по имени и фильтрам, те добовляет в таблицу users_olumpiads соответствующие записи
        with session_factory() as session:
            for id in ids:
                user = UsersOlympiads(
                    tg_id=tg_id,
                    followed_olymp=id
                )
                session.add(user)
            session.commit()

    @staticmethod
    def get_all_user_subscriptions(tg_id : str) -> OlympiadsInfo:
        #Возвращает имена пользовательских олимпиад
        with session_factory() as session:
            all_users_subs = [result[0] for result in session.query(UsersOlympiads.followed_olymp).filter(UsersOlympiads.tg_id==tg_id).all()]
            olymps = session.query(OlympiadsInfo).filter(OlympiadsInfo.olymp_id.in_(all_users_subs)).all()
            return olymps

    @staticmethod
    def get_olympinfo_by_name(name: str) -> str:
        #Возвращает инфу об олимпиаде по ее названию
        with session_factory() as session:
            olymp = session.query(OlympiadsInfo).filter(OlympiadsInfo.name == name).first()
            return f'{olymp.name}\nСсылка:\n{olymp.link}\nУровень: {olymp.level}\nПредмет: {olymp.subject}'
    
    @staticmethod
    def get_olympinfo_by_id(id: int) -> str:
        #Возвращает инфу об олимпиаде по ее id
        with session_factory() as session:
            olymp = session.query(OlympiadsInfo).filter(OlympiadsInfo.olymp_id == id).first()
            return f'{olymp.name}\nСсылка:\n{olymp.link}\nУровень: {olymp.level}\nПредмет: {olymp.subject}'

    @staticmethod
    def get_olymp_model_by_id(id: int) -> OlympiadsInfo:
        with session_factory() as session:
            olymp = session.query(OlympiadsInfo).filter(OlympiadsInfo.olymp_id == id).first()
            return olymp

    @staticmethod
    def get_dates() -> list[OlympiadsDates]:
        with session_factory() as session:
            dates = session.query(OlympiadsDates).all()
            return dates

    @staticmethod
    def get_subs_on_olymp(id: int) -> list[str]:
        with session_factory() as session:
            subs = [res[0] for res in session.query(UsersOlympiads.tg_id).filter(UsersOlympiads.followed_olymp == id).all()]
            return subs

    @staticmethod
    def delete_user(tg_id: str) -> None:
        with session_factory() as session:
            user = session.query(UsersInfo).filter(UsersInfo.tg_id == tg_id).first()
            if user:
                session.delete(user)
                session.commit()

    @staticmethod
    def insert_data() -> None:
        with session_factory() as session:
            for line in parse_first_page():
                info = OlympiadsInfo(
                    olymp_id=int(line[0]),
                    name=line[1],
                    link=line[2],
                    subject=line[3],
                    level=int(line[4]),
                    short_name=line[5]
                )
                session.add(info)
            session.commit()
            for line in parse_second_page():
                date = OlympiadsDates(
                        olymp_id=int(line[0]),
                        stage_name=line[1],
                        date_from=convert_date(line[2]),
                        date_to=convert_date(line[3])
                )
                session.add(date)
            session.commit()