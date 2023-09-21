import telebot
from telebot import types
import sqlite3

from config import BOT_TOKEN
import db_functions

# bot = telebot.TeleBot('6216891307:AAGzqwiMXr5TkTBJifKyuAd06z7l8_R0uCI')
bot = telebot.TeleBot(BOT_TOKEN)

var_create_room_name = ''
var_join_room_id = None
var_join_room_pass = None
var_join_room_name = None


@bot.message_handler(commands=['start'])
def command_start(message):
    db_functions.create_tables()  # создание таблиц
    if db_functions.get_user_name(message):
        start_menu(message)
    else:
        help_text = ''
        with open("about.txt", "r", encoding='UTF8') as f:
            for line in f.readlines():
                help_text += line
        bot.send_message(message.chat.id, help_text, parse_mode='html', disable_web_page_preview=True)
        bot.send_message(message.chat.id, "Давай знакомиться!\n<b>Введи своё имя:</b>", parse_mode='html')
        bot.register_next_step_handler(message, create_new_user)


# создание нового пользователя с введенным именем
def create_new_user(message):
    db_functions.create_new_user(message)
    start_menu(message)


# вывод меню в зависимости от наличия комнаты
def start_menu(message):
    name = db_functions.get_user_name(message)
    room = db_functions.get_user_room(message)
    if not room:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Создать новую комнату')
        btn2 = types.KeyboardButton('Присоединиться к существующей')
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id,
                         f"Привет, <b>{name}</b>!\n"
                         f"Сейчас ты не состоишь ни в одной комнате.\n"
                         f"<b>Выбери команду из меню:</b>",
                         parse_mode='html', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Добавить покупку')
        btn2 = types.KeyboardButton('Подтвердить покупку')
        markup.row(btn1, btn2)
        btn3 = types.KeyboardButton('Мои долги')
        btn4 = types.KeyboardButton('Общие долги')
        markup.row(btn3, btn4)
        btn5 = types.KeyboardButton('График обязанностей')
        btn6 = types.KeyboardButton('Информация о текущей комнате')
        markup.add(btn5)
        markup.add(btn6)
        bot.send_message(message.chat.id,
                         f'Привет, <b>{name}</b>!\n'
                         f'Текущая комната: <b>"{room[0][2]}"</b>.\n'
                         f'<b>Выбери команду из меню:</b>',
                         parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(message, on_click_menu_commands)


# обработчик кнопок меню
def on_click_menu_commands(message):
    if message.text == 'Создать новую комнату':
        room = db_functions.get_user_room(message)
        if not room:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton('⬅️ Назад')
            markup.add(btn)
            bot.send_message(message.chat.id, "Хорошо, давай создадим новую комнату!\n"
                                              "<b>Введи название для комнаты:</b>",
                             parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, create_new_room_name)
        else:
            bot.send_message(message.chat.id,
                             f'Ошибка! Покиньте текущую комнату <b>"{room[0][2]}"</b>, чтобы создать новую.',
                             parse_mode='html')
            start_menu(message)

    elif message.text == 'Присоединиться к существующей':
        room = db_functions.get_user_room(message)
        if not room:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton('⬅️ Назад')
            markup.add(btn)
            bot.send_message(message.chat.id, "<b>Введи id для существующей комнаты:</b>",
                             parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, join_new_room_id)
        else:
            bot.send_message(message.chat.id,
                             f'Ошибка! Покиньте текущую комнату <b>"{room[0][2]}"</b>, чтобы присоединиться к новой.',
                             parse_mode='html')
            start_menu(message)

    elif message.text == 'Информация о текущей комнате':
        room = db_functions.get_user_room(message)
        if room:
            admin_name = db_functions.get_admin_name_by_room_id(room[0][0])
            admin_username = db_functions.get_admin_username_by_room_id(room[0][0])
            users_list = db_functions.get_users_by_room_id(room[0][0])
            bot.send_message(message.chat.id, f'***** <b>Комната {room[0][2]}</b> *****\n\n'
                                              f'<b>ID:</b> {room[0][0]}\n'
                                              f'<b>Название:</b> {room[0][2]}\n'
                                              f'<b>Админ комнаты:</b> <a href="t.me/{admin_username}">{admin_name}</a>\n'
                                              f'<b>Участники:</b>\n'
                                              f'{users_list}\n',
                             parse_mode='html', disable_web_page_preview=True)
            start_menu(message)
        else:
            bot.send_message(message.chat.id,
                             f'Ошибка! У вас нет комнаты. Создайте новую или присоединитесь к существующей.',
                             parse_mode='html')
            start_menu(message)

    elif message.text == '/test':
        test(message)
    else:
        bot.send_message(message.chat.id, f"Неизвестная команда. Попробуй еще раз!")
        start_menu(message)


# ввод имени для создания комнаты
def create_new_room_name(message):
    global var_create_room_name
    if message.text == '⬅️ Назад':
        start_menu(message)
    else:
        bot.send_message(message.chat.id, f"Прекрасное название для комнаты: \"{message.text}\".\n"
                                          f"<b>Теперь придумай пароль:</b>", parse_mode='html')
        var_create_room_name = message.text
        bot.register_next_step_handler(message, create_new_room_pass)


# ввод пароля и создание комнаты
def create_new_room_pass(message):
    if message.text == '⬅️ Назад':
        start_menu(message)
    else:
        if len(message.text) >= 6:
            db_functions.create_new_room(message, var_create_room_name)
            bot.send_message(message.chat.id,
                             f"Комната с названием <b>\"{var_create_room_name}\"</b> успешно создана!",
                             parse_mode='html')
            start_menu(message)
        else:
            bot.send_message(message.chat.id, f"Пароль не может быть короче 6 символов!\n"
                                              f"<b>Придумай другой пароль:</b>", parse_mode='html')
            bot.register_next_step_handler(message, create_new_room_pass)


# ввод id для присоединения к комнате
def join_new_room_id(message):
    global var_join_room_id, var_join_room_name, var_join_room_pass
    if message.text == '⬅️ Назад':
        start_menu(message)
    else:
        room_info = db_functions.check_room_by_id(message)
        if room_info:
            bot.send_message(message.chat.id, f"Комната <b>\"{room_info[2]}\"</b> найдена!\n"
                                              f"<b>Введите пароль от комнаты:</b>", parse_mode='html')
            var_join_room_id = message.text
            var_join_room_name = room_info[2]
            var_join_room_pass = room_info[3]
            bot.register_next_step_handler(message, join_new_room_pass)
        else:
            bot.send_message(message.chat.id, f"Комната с <b>id={message.text}</b> не найдена.\n"
                                              f"<b>Введи id для существующей комнаты:</b>", parse_mode='html')
            bot.register_next_step_handler(message, join_new_room_id)


# ввод пароля и присоединение к комнате
def join_new_room_pass(message):
    if message.text == '⬅️ Назад':
        start_menu(message)
    else:
        if db_functions.check_pass(message, var_join_room_pass):
            db_functions.join_user_on_room(message, var_join_room_id)
            bot.send_message(message.chat.id,
                             f"Вы успешно присоединились к комнате <b>\"{var_join_room_name}\"</b>!",
                             parse_mode='html')
            start_menu(message)
        else:
            bot.send_message(message.chat.id, f"Неверный пароль!\n"
                                              f"<b>Попробуй ввести пароль еще раз:</b>", parse_mode='html')
            bot.register_next_step_handler(message, join_new_room_pass)


# тестовый обработчик
@bot.message_handler(commands=['test'])
def test(message):
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    info = 'Таблица "users"\n\n'
    for el in users:
        info += f'id: {el[0]}, name: {el[1]}, room_id: {el[2]}\n'
    bot.send_message(message.chat.id, info)

    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms")
    users = cur.fetchall()
    cur.close()
    conn.close()
    info = 'Таблица "rooms"\n\n'
    for el in users:
        info += f'id: {el[0]}, admin_id: {el[1]}, name: {el[2]}, pass: {el[3]}\n'
    bot.send_message(message.chat.id, info)


# обработка остального текста
@bot.message_handler()
def other_messages(message):
    command_start(message)


bot.infinity_polling()
