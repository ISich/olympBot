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
            markup.add(*[types.InlineKeyboardButton(s, callback_data=s) for s in self.subjects])
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
        self.bot.send_message(message.chat.id, "Выберите тип олимпиады:", reply_markup=markup)

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
            self.bot.answer_callback_query(call.id, f"Вы выбрали: {types_chosen}")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Продолжить', 'Перевыбрать предметы')
            self.bot.send_message(call.message.chat.id, f"Ты закрепил следующие предметы:\n{types_chosen}", reply_markup=markup)

        @self.bot.message_handler(func=lambda message: message.text == 'Продолжить')
        def move_next(message):
            user_id = message.chat.id
            self.user_data[user_id]['levels'] = {}
            self.send_level_selection(message)

    def send_level_selection(self, message):
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [types.InlineKeyboardButton(f"Уровень {i + 1}", callback_data=f"level_{i+1}") for i in range(3)]
        confirm_button = types.InlineKeyboardButton("✅Подтвердить✅", callback_data="confirm_level")
        markup.add(*buttons, confirm_button)
        self.bot.send_message(message.chat.id, "Выберите уровень:", reply_markup=markup)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('level_'))
        def toggle_level(call):
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
            self.bot.answer_callback_query(call.id, f"Вы выбрали уровень: {levels_chosen}")
            self.bot.send_message(call.message.chat.id, f"Вы выбрали:\n{levels_chosen}")
            self.bot.send_message(call.message.chat.id, "Здесь мои полномочия все")


        @self.bot.message_handler(func=lambda message: message.text == 'Перевыбрать предметы')
        def reselect(message):
            user_id = message.chat.id
            self.user_data[user_id]['subjects'].clear()
            self.send_type_selection(message)

    def run(self):
        self.bot.polling(none_stop=True)


if __name__ == '__main__':
    token = os.getenv("TELEGRAM_TOKEN")
    my_bot = OlympBot(token)
    my_bot.run()