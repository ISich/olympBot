import os
import telebot
from telebot import types
from models import OlympiadsDates
from orm import SyncOrm
from datetime import datetime
import asyncio

class OlympBot:
    def __init__(self, bot):
        self.bot = bot
        self.user_data = {}
        self.subjects = ['Математика', 'Информатика', 'Физика', 'Химия']
        self.grades = ["9 класса", "10 класса", "11 класса"]
        self.olymps = []
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            SyncOrm.delete_user(str(message.chat.id))
            self.user_data[message.chat.id] = {}
            self.bot.reply_to(message, "Привет! Я - olympHelper - твой олимпиадный информатор.\nЯ расскажу тебе информацию о той или иной олимпиаде и не дам тебе забыть о датах регистрации!")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*[types.InlineKeyboardButton(s, callback_data=s) for s in self.grades])
            self.bot.send_message(message.chat.id, "Давай знакомиться! Тебя интересуют олимпиады для:", reply_markup=markup)
        
        @self.bot.message_handler(func=lambda message: message.text in self.grades)
        def subject_peeker(message):
            user_id = message.chat.id
            self.user_data[user_id] = {'grade': message.text, 'subjects': {}, 'olymps': {}}
            self.send_subject_selection(message)
    
    def send_subject_selection(self, message):
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [types.InlineKeyboardButton(s, callback_data=s) for s in self.subjects]
        markup.add(*buttons, types.InlineKeyboardButton("✅Подтвердить✅", callback_data="confirm_subj"))        
        self.bot.send_message(message.chat.id, "Выбери тип олимпиады:", reply_markup=markup)

        @self.bot.callback_query_handler(func=lambda call: call.data in self.subjects)
        def toggle_type(call):
            user_id = call.message.chat.id
            type_key = call.data
            if type_key in self.user_data[user_id]['subjects']:
                self.user_data[user_id]['subjects'].pop(type_key)
            else:
                self.user_data[user_id]['subjects'][type_key] = True

            new_markup = types.InlineKeyboardMarkup()
            for s in self.subjects:
                data_key = s
                label = s
                if data_key in self.user_data[user_id]['subjects']:
                    label += " ✅"
                new_button = types.InlineKeyboardButton(label, callback_data=data_key)
                new_markup.add(new_button)
            new_markup.add(types.InlineKeyboardButton("✅Подтвердить✅", callback_data="confirm_subj"))
            self.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=new_markup)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'confirm_subj')
        def confirm_selection(call):
            user_id = call.message.chat.id
            types_chosen = ', '.join(self.user_data[user_id]['subjects'])
            self.bot.answer_callback_query(call.id, f"Ты выбрал: {types_chosen}")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Продолжить', 'Перевыбрать предметы')
            self.bot.send_message(call.message.chat.id, f"Ты закрепил следующие предметы:\n{types_chosen}", reply_markup=markup)

        @self.bot.message_handler(func=lambda message: message.text == 'Продолжить')
        def move_next(message):
            user_id = message.chat.id
            self.user_data[user_id]['levels'] = {}
            self.send_level_selection(message)
        
        @self.bot.message_handler(func=lambda message: message.text == 'Перевыбрать предметы')
        def reselect(message):
            user_id = message.chat.id
            self.user_data[user_id]['subjects'].clear()
            self.send_subject_selection(message)

    def send_level_selection(self, message):
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [types.InlineKeyboardButton(f"Уровень {i + 1}", callback_data=f"level_{i+1}") for i in range(3)]
        confirm_button = types.InlineKeyboardButton("✅Подтвердить✅", callback_data="confirm_level")
        markup.add(*buttons, confirm_button)
        self.bot.send_message(message.chat.id, "Выбери уровень:", reply_markup=markup)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('level_'))
        def send_type_selection(call):
            user_id = call.message.chat.id
            level_key = call.data
            if level_key in self.user_data[user_id]['levels']:
                self.user_data[user_id]['levels'].pop(level_key)
            else:
                self.user_data[user_id]['levels'][level_key] = True

            new_markup = types.InlineKeyboardMarkup()
            for i in range(3):
                data_key = f"level_{i+1}"
                label = f"Уровень {i + 1}"
                if data_key in self.user_data[user_id]['levels']:
                    label += " ✅"
                new_button = types.InlineKeyboardButton(label, callback_data=data_key)
                new_markup.add(new_button)
            new_markup.add(types.InlineKeyboardButton("✅Подтвердить✅", callback_data="confirm_level"))
            self.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=new_markup)

        @self.bot.callback_query_handler(func=lambda call: call.data == "confirm_level")
        def confirm_level(call):
            user_id = call.message.chat.id
            if len(self.user_data[user_id]['levels']) == 0:
                levels_chosen = ''
            else:
                levels_chosen = ', '.join(f"{key.split('_')[1]} уровень" for key in self.user_data[user_id]['levels'])
            self.bot.answer_callback_query(call.id, f"Ты выбрал уровень: {levels_chosen}")
            self.bot.send_message(call.message.chat.id, f"Ты выбрал:\n{levels_chosen}")

            user_id = call.message.chat.id
            user_info = self.user_data[user_id]
            grade = int(user_info['grade'].split()[0])
            subjects = list(map(lambda x: x.lower(), user_info['subjects'].keys()))
            levels = list(map(lambda x: int(x[-1]) , user_info['levels'].keys()))

            SyncOrm.add_user_info(user_id, grade, subjects, levels)
            self.ask_for_notifies(call.message)
    
    def ask_for_notifies(self, message):
        self.bot.send_message(message.chat.id, "По заданным критериям у меня есть информация про следующие олимпиады:")
        user_olymps = SyncOrm.get_olympiads_interesting_for_user(str(message.chat.id))
        text = "".join([f"{o}\n" for o in user_olymps])
        self.bot.send_message(message.chat.id, text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Подписаться на все", "Выбрать конкретные")
        self.bot.send_message(message.chat.id, "Хочешь получать уведомления о всех или каких-то конкретных?", reply_markup=markup)

        @self.bot.message_handler(func=lambda message: message.text == 'Подписаться на все')
        def all_peeked(message):
            SyncOrm.subscibe_on_all_olympiads(str(message.chat.id))
            self.send_final(message)

        @self.bot.message_handler(func=lambda message: message.text == 'Выбрать конкретные')
        def custom_peek(message):
            self.send_olymp_selection(message)
   
    def send_olymp_selection(self, message):
        self.user_olymps = SyncOrm.get_olympiad_models_interesting_for_user(str(message.chat.id))
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [types.InlineKeyboardButton(o.short_name, callback_data=f"peekolymp_{o.olymp_id}") for o in self.user_olymps]
        markup.add(*buttons, types.InlineKeyboardButton("✅Подтвердить✅", callback_data="confirm_olymp"))
        self.user_data[message.chat.id]['olymps_id'] = {}
        self.bot.send_message(message.chat.id, "Выбери интересующие тебя олимпиады:", reply_markup=markup)
    
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('peekolymp_'))
        def remake_olymp_btns(call):
            user_id = call.message.chat.id
            olymp_id = int(call.data.split('_')[1])
            if olymp_id in self.user_data[user_id]['olymps_id']:
                self.user_data[user_id]['olymps_id'].pop(olymp_id)
            else:
                self.user_data[user_id]['olymps_id'][olymp_id] = True

            new_markup = types.InlineKeyboardMarkup()
            for s in self.user_olymps:
                data_key = s.olymp_id
                label = s.short_name
                if data_key in self.user_data[user_id]['olymps_id']:
                    label += " ✅"

                new_button = types.InlineKeyboardButton(label, callback_data=f'peekolymp_{data_key}')
                new_markup.add(new_button)
            new_markup.add(types.InlineKeyboardButton("✅Подтвердить✅", callback_data="confirm_olymp"))
            self.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=new_markup)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'confirm_olymp')
        def confirm_selection(call):
            user_id = call.message.chat.id
            peeked_olymps = []
            for o in self.user_olymps:
                if o.olymp_id in self.user_data[user_id]['olymps_id']:
                    peeked_olymps.append(o.short_name)
            olymps_chosen = ''.join(f"\n{o}" for o in peeked_olymps)
            self.bot.answer_callback_query(call.id, f"Ты выбрал: {olymps_chosen}")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Далее', 'Перевыбрать олимпиады')
            self.bot.send_message(call.message.chat.id, f"Ты выбрал следующие олимпиады:\n{olymps_chosen}", reply_markup=markup)

        @self.bot.message_handler(func=lambda message: message.text == 'Далее')
        def move_next(message):
            SyncOrm.subscribe_on_olympiads_by_ids(str(message.chat.id), self.user_data[message.chat.id]['olymps_id'].keys())
            self.send_final(message)
        
        @self.bot.message_handler(func=lambda message: message.text == 'Перевыбрать олимпиады')
        def reselect_olymps(message):
            user_id = message.chat.id
            self.user_data[user_id]['olymps'].clear()
            self.send_olymp_selection(message)

    def send_final(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Посмотреть информацию об олимпиадах")
        self.bot.send_message(message.chat.id, "Отлично, теперь я полностью готов к работе! Теперь вы можете посмотреть информацию о выбранных олимпиадах. Я же буду напоминать вам за неделю и за день об окончании регистраций", reply_markup=markup)
        
        @self.bot.message_handler(func=lambda message: message.text == 'Посмотреть информацию об олимпиадах')
        def check_info(message):
            user_olymps = SyncOrm.get_all_user_subscriptions(str(message.chat.id))
            markup = types.InlineKeyboardMarkup(row_width=1)
            buttons = [types.InlineKeyboardButton(o.short_name, callback_data=f"checkolymp_{o.olymp_id}") for o in user_olymps]
            markup.add(*buttons)
            self.bot.send_message(message.chat.id, 'Выбери интересующую олимпиаду', reply_markup=markup)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('checkolymp_'))
        def send_info(call):
            olymp_id = int(call.data.split('_')[1])
            info = SyncOrm.get_olympinfo_by_id(olymp_id)
            self.bot.send_message(call.message.chat.id, info)

    def run(self):
        self.bot.polling(none_stop=True)