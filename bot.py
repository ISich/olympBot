import os
import telebot
from telebot import types

class OlympBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.user_data = {}
        self.subjects = ['Математика', 'Информатика', 'Физика', 'Химия', 'Русский язык']
        self.grades = ["9 класса", "10 класса", "11 класса"]
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.bot.reply_to(message, "Привет! Я - olympHelper - твой олимпиадный информатор.\nЯ расскажу тебе информацию о той или иной олимпиаде и не дам тебе забыть о датах регистрации!")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*[types.InlineKeyboardButton(s, callback_data=s) for s in self.grades])
            self.bot.send_message(message.chat.id, "Давай знакомиться! Тебя интересуют олимпиады для:", reply_markup=markup)
        
        @self.bot.message_handler(func=lambda message: message.text in self.grades)
        def subject_peeker(message):
            user_id = message.chat.id
            self.user_data[user_id] = {'grade': message.text, 'subjects': {}}
            self.send_subject_selection(message)
    
    def send_subject_selection(self, message):
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [types.InlineKeyboardButton(s, callback_data=s) for s in self.subjects]
        markup.add(*buttons, types.InlineKeyboardButton("✅Подтвердить✅", callback_data="confirm"))        
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
            new_markup.add(types.InlineKeyboardButton("✅Подтвердить✅", callback_data="confirm"))
            self.bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=new_markup)
        
        @self.bot.callback_query_handler(func=lambda call: call.data == 'confirm')
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

        @self.bot.callback_query_handler(func=lambda call: call.data == 'confirm_level')
        def confirm_level(call):
            user_id = call.message.chat.id
            if len(self.user_data[user_id]['levels']) == 0:
                levels_chosen = ''
            else:
                levels_chosen = ', '.join(f"{key.split('_')[1]} уровень" for key in self.user_data[user_id]['levels'])
            self.bot.answer_callback_query(call.id, f"Ты выбрал уровень: {levels_chosen}")
            self.bot.send_message(call.message.chat.id, f"Ты выбрал:\n{levels_chosen}")
            self.ask_for_notifies(call.message)
    
    def ask_for_notifies(self, message):
        self.bot.send_message(message.chat.id, "По заданным критериям у меня есть информация про следующие олимпиады:")
        #def_obrasheniye_k_bd()
        self.bot.send_dice(message.chat.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Подписаться на все", "Выбрать конкретные")
        self.bot.send_message(message.chat.id, "Хочешь получать уведомления о всех или каких-то конкретных?", reply_markup=markup)

        @self.bot.message_handler(func=lambda message: message.text == 'Подписаться на все')
        def all_peeked(message):
            self.send_final(message)

        @self.bot.message_handler(func=lambda message: message.text == 'Выбрать конкретные')
        def custom_peek(message):
            #from olymps in db_callback:
            #inline_knopki add olymp
            #self.user_data['chosen_olymps'].add(all_from_peeked_knopki)
            #markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            #markup.add(knopki)
            self.bot.send_message(message.chat.id,"Вот список с олимпиадами по отдельности")
            self.bot.send_dice(message.chat.id)
            self.send_final(message)
    
    def send_final(self, message):
        self.user_data['chosen_olymps'] = {}
        #self.user_data['chosen_olymps'].add(all_from_callback)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Посмотреть информацию об олимпиадах")
        self.bot.send_message(message.chat.id, "Отлично, теперь я полностью готов к работе! Теперь вы можете посмотреть информацию о выбранных олимпиадах. Я же буду напоминать вам за неделю и за день об окончании регистраций", reply_markup=markup)
        
        @self.bot.message_handler(func=lambda message: message.text == 'Посмотреть информацию об олимпиадах')
        def check_info(message):
            #создать кнопки с каждой олимпой из словаря юзера
            markup = types.InlineKeyboardMarkup()
            self.bot.send_message(message.chat.id, 'Выбери интересуемую олимпиаду', reply_markup=markup)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('olymp_'))
        def send_info(call):
            self.bot.send_message(call.message.chat.id, "huy") #информация из бд

    def run(self):
        self.bot.polling(none_stop=True)

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_TOKEN")
    my_bot = OlympBot(token)
    my_bot.run()