from db import session_factory, sync_engine
from models import Base, UsersOlympiads, UsersInfo, OlympiadsInfo, OlympiadsDates
from sqlalchemy import or_


class SyncOrm():
    @staticmethod
    def create_tables() -> None:
        Base.metadata.drop_all(sync_engine)
        sync_engine.echo = False
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = True


    @staticmethod
    def add_user_info(tg_id: str, grade: int, subjects: list[int], levels: list[int]) -> None:
        #добавляет пользователя с этими данными в табличку users_info
        with session_factory() as session:
            try:
                user = UsersInfo(tg_id=tg_id, grade=grade, subjects=subjects, levels=levels)
                session.add(user)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

    @staticmethod
    def get_olympiads_interesting_for_user(tg_id: str) -> list[OlympiadsInfo]:
        with session_factory() as session:
            userInfo = session.query(UsersInfo).filter(UsersInfo.tg_id == tg_id).first()
            if userInfo:
                subjects = userInfo.subjects
                levels = userInfo.levels
                olymps = session.query(OlympiadsInfo).filter(or_(OlympiadsInfo.subject.in_(subjects),
                                                                 OlympiadsInfo.level.in_(levels))).all()
                return olymps
            else:
                return []

    @staticmethod
    def subscibe_on_all_olympiads(tg_id: str) -> None:
        #Должен добавить для конкретного user'a по его tg_id в табличку users_olumpiads все те олимпиады, которые подходят ему по фильтрам из его users_info
        with session_factory() as session:
            user_info = session.query(UsersInfo).filter(UsersInfo.tg_id == tg_id).first()
            if user_info:
                subjects = user_info.subjects
                levels = user_info.levels
                olympiads = session.query(OlympiadsInfo).filter(
                    OlympiadsInfo.subject.in_(subjects),
                    OlympiadsInfo.level.in_(levels)
                ).all()
                for olympiad in olympiads:
                    user_info.followed_olymp.append(olympiad[0])
                session.commit()
            else:
                print("Пользователь с таким tg_id не найден.")

    @staticmethod
    def get_olympiad_by_name(olympiad_name: str) -> OlympiadsInfo:
        # По имени олимпиады возвращает ее можельку, которую мы на постпроцессинге преобразуем в сообщение
        with session_factory() as session:
            olymp = session.query(OlympiadsInfo).filter(OlympiadsInfo.name == olympiad_name).first()
            if olymp:
                return olymp
            print("Олимпиада с таким именем не найдена")

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


