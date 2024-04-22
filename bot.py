import os
import telebot
from telebot import types

class OlympBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.user_data = {}
        self.subjects = ['Математика', 'Информатика', 'Физика', 'Химия', 'Русский язык']
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.bot.reply_to(message, "Привет! Я - olympHelper - твой олимпиадный информатор.\nЯ расскажу тебе информацию о той или иной олимпиаде и не дам тебе забыть о датах регистрации!")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("9 класса", "10 класса", "11 класса")
            self.bot.send_message(message.chat.id, "Давай знакомиться! Тебя интересуют олимпиады для:", reply_markup=markup)
        
        @self.bot.message_handler(func=lambda message: message.text in ["9 класса", "10 класса", "11 класса"])
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
            # Текущий выбор пользователя
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
            self.bot.send_message(call.message.chat.id, f"Ты закрепил следующие предметы: {types_chosen}", reply_markup=markup)

        @self.bot.message_handler(func=lambda message: message.text == 'Продолжить')
        def when_selected(message):
            self.bot.send_message(message.chat.id, "Выбор подтвержден! Спасибо за использование бота.")

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