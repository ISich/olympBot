from db import session_factory, sync_engine
from models import Base


class SyncOrm():
    @staticmethod
    def create_tables():
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = True

    