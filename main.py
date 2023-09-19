import telebot
import sqlite3
from config import BOT_TOKEN
import db_functions

# bot = telebot.TeleBot('6216891307:AAGzqwiMXr5TkTBJifKyuAd06z7l8_R0uCI')
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    db_functions.create_tables()  # создание таблиц
    if db_functions.is_user_have_in_db(message):
        start_menu(message)
    else:
        help_text = ''
        with open("welcome.txt", "r", encoding='UTF8') as f:
            for line in f.readlines():
                help_text += line
        bot.send_message(message.chat.id, help_text, parse_mode='html', disable_web_page_preview=True)
        bot.send_message(message.chat.id, "<b>Введите ваше имя:</b>", parse_mode='html')
        bot.register_next_step_handler(message, create_new_user)


def create_new_user(message):
    db_functions.create_new_user(message)
    start_menu(message)


def start_menu(message):
    name = db_functions.get_user_name(message)
    bot.send_message(message.chat.id, f"Добро пожаловать, <b>{name}</b>!", parse_mode='html')


# тестовый обработчик
@bot.message_handler(commands=['test'])
def test(message):
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    info = ''
    for el in users:
        info += f'ID: {el[0]}, имя: {el[1]}, комната: {el[2]}\n'
    bot.send_message(message.chat.id, info)
    print(message.from_user.id)


bot.infinity_polling()
