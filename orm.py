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

