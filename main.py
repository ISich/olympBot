from orm import SyncOrm

SyncOrm.create_tables()
SyncOrm.add_user(1, [])
print(SyncOrm.select_user(1))