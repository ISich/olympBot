from datetime import datetime
from orm import SyncOrm
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from models import OlympiadsDates


class Notificator:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.check_olympiads_dates, 'cron', minute='*')

    def send_message_to_all_users_subscribed_on(self, olymp_id: int, message: str) -> None:
        all_users_subscribed = SyncOrm.get_subs_on_olymp(olymp_id)
        for user_chat_id in all_users_subscribed:
            self.bot.send_message(user_chat_id, message)

    def send_messages_one_day_left_not_interval(self, olympiad_date: OlympiadsDates) -> None:
        olymp_id = olympiad_date.id
        olympiad_info = SyncOrm.get_olymp_model_by_id(olymp_id)
        message = f'Привет! \nНапоминаю, что у олимпиады {olympiad_info.name}\n до окончания этапа {olympiad_date.stage_name} остался всего один день!\n\n Ссылка на сайт олимпиады: {olympiad_info.link}'
        self.send_message_to_all_users_subscribed_on(olymp_id, message)

    def send_message_one_week_left_not_interval(self, olympiad_date: OlympiadsDates) -> None:
        olymp_id = olympiad_date.id
        olympiad_info = SyncOrm.get_olymp_model_by_id(olymp_id)
        message = f'Привет! \nНапоминаю, что у олимпиады {olympiad_info.name}\n до окончания этапа {olympiad_date.stage_name} осталась всего неделя!\n\n Ссылка на сайт олимпиады: {olympiad_info.link}'
        self.send_message_to_all_users_subscribed_on(olymp_id, message)

    def send_message_one_day_left_interval(self, olympiad_date: OlympiadsDates, is_start_time: bool) -> None:
        olymp_id = olympiad_date.id
        olympiad_info = SyncOrm.get_olymp_model_by_id(olymp_id)
        if is_start_time:
            message = f'Привет! \nНапоминаю, что у олимпиады {olympiad_info.name}\n до начала этапа {olympiad_date.stage_name} остался всего один день!\n\n Ссылка на сайт олимпиады: {olympiad_info.link}'
        else:
             message = f'Привет! \nНапоминаю, что у олимпиады {olympiad_info.name}\n до окончания этапа {olympiad_date.stage_name} остался всего один день!\n\n Ссылка на сайт олимпиады: {olympiad_info.link}'
        self.send_message_to_all_users_subscribed_on(olymp_id, message)


    def send_message_one_week_left_interval(self, olympiad_date: OlympiadsDates) -> None:
        olymp_id = olympiad_date.id
        olympiad_info = SyncOrm.get_olymp_model_by_id(olymp_id)
        message = f'Привет! \nНапоминаю, что у олимпиады {olympiad_info.name}\n до окончания этапа {olympiad_date.stage_name} осталась всего неделя!\n\n Ссылка на сайт олимпиады: {olympiad_info.link}'
        self.send_message_to_all_users_subscribed_on(olymp_id, message)


    def check_olympiads_dates(self) -> None:
        print("Я работаю мать твою")
        olympiads_dates = SyncOrm.get_dates()
        time_now = datetime.now()
        seconds_in_day = 24 * 60 * 60
        seven_days_seconds = seconds_in_day * 7
        six_days_seconds = seconds_in_day * 6
        for olympiad in olympiads_dates:
            date_from_difference = olympiad.date_from - time_now
            date_to_difference = olympiad.date_to - time_now
            if olympiad.date_from == olympiad.date_to:
                if date_from_difference.seconds() < seconds_in_day:
                    self.send_messages_one_day_left_not_interval(olympiad)
                elif date_from_difference.seconds() < seven_days_seconds and \
                    date_from_difference.seconds() > six_days_seconds:
                    self.send_message_one_week_left_not_interval(olympiad)
            else:
                if date_from_difference.seconds() < seconds_in_day:
                    self.send_message_one_day_left_interval(olympiad.olymp_id, is_start_time=True)
                elif date_to_difference.seconds() < seconds_in_day:
                    self.send_message_one_day_left_interval(olympiad.olymp_id, is_start_time=False)
                elif date_to_difference.seconds() < seven_days_seconds and \
                    date_to_difference.seconds() > six_days_seconds:
                    self.send_message_one_week_left_interval(olympiad.olymp_id)

    def run(self):
        self.scheduler.start()
        print("Вот тут я работаю")
