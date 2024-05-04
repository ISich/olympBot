from db import session_factory, sync_engine
from models import Base, UsersOrm, OlympiadsOrm


class SyncOrm():
    @staticmethod
    def create_tables() -> None:
        Base.metadata.drop_all(sync_engine)
        sync_engine.echo = False
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def select_user(tg_id: int) -> list[int]:
        with session_factory() as session:
            user = session.query(UsersOrm).filter(UsersOrm.tg_id == tg_id).first()
            return user.followed_olymps

    @staticmethod
    def add_user(tg_id: int, olymps : list[int] = []) -> None:
        with session_factory() as session:
            try:
                new_user = UsersOrm(tg_id=tg_id, followed_olymps=olymps)
                session.add(new_user)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

    @staticmethod
    def delete_user(tg_id: int) -> None:
        with session_factory() as session:
            try:
                user = session.query(UsersOrm).filter(UsersOrm.tg_id == tg_id).first()
                if user:
                    session.delete(user)
                    session.commit()
                else:
                    print(f"Пользователь с tg_id={tg_id} не найден.")
            except Exception as e:
                session.rollback()
                raise e

    @staticmethod
    def add_user_info(tg_id: str, grade: int, subjects: list[int], levels: list[int]) -> None:
        #добавляет пользователя с этими данными в табличку users_info
        pass


    @staticmethod
    def get_olympiads_interesting_for_user(tg_id: str) -> OlympiadsInfo:
        #Возвращает список олимпиад, по фильтрам, который указал пользователь при регистрации aka предметы, уровень и тд
        pass

    @staticmethod
    def subscibe_on_all_olympiads(tg_id: str) -> None:
        #Должен добавить для конкретного user'a по его tg_id в табличку users_olumpiads все те олимпиады, которые подходят ему по фильтрам из его users_info
        pass

    @staticmethod
    def get_olympiad_by_name(olympiad_name: str) -> OlympiadsInfo:
        # По имени олимпиады возвращает ее можельку, которую мы на постпроцессинге преобразуем в сообщение
        pass

    def subscribe_on_olympiads_by_names(tg_id:str, olympiads_names: list[str]) -> None:
        # По массиву из имен олимпиал подписывает пользователя на олимпиады по имени и фильтрам, те добовляет в таблицу users_olumpiads соответствующие записи
        pass

    def get_all_users_subscriptions() -> list[UsersOlympiads]:
        #Просто возвращает все такие модельки из базы
        pass