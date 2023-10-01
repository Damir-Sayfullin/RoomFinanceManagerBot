import time

import telebot
from telebot import types
import sqlite3

from config import BOT_TOKEN
import db_functions

bot = telebot.TeleBot(BOT_TOKEN, skip_pending=True)

var_create_room_name = None
var_join_room_id = None
var_join_room_pass = None
var_join_room_name = None
var_new_admin = None


@bot.message_handler(commands=['start'])
def command_start(message):
    db_functions.create_tables()
    if db_functions.get_user_by_id(message.from_user.id):
        menu_start(message)
    else:
        help_text = ''
        with open("about.txt", "r", encoding='UTF8') as f:
            for line in f.readlines():
                help_text += line
        bot.send_message(message.chat.id, help_text, parse_mode='html', disable_web_page_preview=True)
        bot.send_message(message.chat.id, "Давай знакомиться!\n<b>Введи своё имя "
                                          "(это имя можно будет поменять):</b>", parse_mode='html')
        bot.register_next_step_handler(message, create_new_user)


# создание нового пользователя с введенным именем
def create_new_user(message):
    if message.content_type == 'text':
        db_functions.create_new_user(message)
        bot.send_message(message.chat.id, f"Классное имя, <b>{message.text}</b>! Ты успешно зарегистрирован.",
                         parse_mode='html')
        menu_start(message)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве имени может быть только <b>текст</b>!\n"
                                          f"<b>Введи своё имя:</b>", parse_mode='html')
        bot.register_next_step_handler(message, create_new_user)


# главное меню
def menu_start(message):
    name = db_functions.get_user_by_id(message.from_user.id)[1]
    room = db_functions.get_user_room(message)
    if not room:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔓 Создать новую комнату')
        btn2 = types.KeyboardButton('🔑 Присоединиться к существующей')
        markup.row(btn1, btn2)
        btn3 = types.KeyboardButton('👤 Личные настройки')
        markup.row(btn3)
        btn4 = types.KeyboardButton('🤖 О боте')
        markup.row(btn4)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('*Добавить общую покупку')
        btn2 = types.KeyboardButton('*Подтвердить общую покупку')
        markup.row(btn1, btn2)
        btn3 = types.KeyboardButton('*Мои долги')
        btn4 = types.KeyboardButton('*Общие долги')
        markup.row(btn3, btn4)
        btn5 = types.KeyboardButton('✅ Обязанности')
        btn6 = types.KeyboardButton('🛒 Список покупок')
        markup.row(btn5, btn6)
        btn7 = types.KeyboardButton('👤 Личные настройки')
        btn8 = types.KeyboardButton('⚙️ Настройки комнаты')
        markup.row(btn7, btn8)
        btn9 = types.KeyboardButton('🤖 О боте')
        markup.row(btn9)
    bot.send_message(message.chat.id,
                     f"<u><b>Главное меню</b></u>\n\n"
                     f'Привет, <b>{name}</b>!\n\n'
                     f'<b>Выбери команду из меню:</b>',
                     parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(message, on_click_menu_start)


# обработчик кнопок меню
def on_click_menu_start(message):
    if message.text == '/repair':
        command_repair(message)
    elif message.text == '🔓 Создать новую комнату':
        room = db_functions.get_user_room(message)
        if not room:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton('⬅️ Назад')
            markup.add(btn)
            bot.send_message(message.chat.id, "Хорошо, давай создадим новую комнату!\n"
                                              "<b>Придумай название для комнаты "
                                              "(это название можно будет поменять):</b>",
                             parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, create_new_room_name)
        else:
            bot.send_message(message.chat.id,
                             f'<b>Ошибка!</b> Покинь текущую комнату <b>"{room[0][2]}"</b>, '
                             f'чтобы создать новую.', parse_mode='html')
            menu_start(message)

    elif message.text == '🔑 Присоединиться к существующей':
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
                             f'<b>Ошибка!</b> Покинь текущую комнату <b>"{room[0][2]}"</b>, '
                             f'чтобы присоединиться к новой.', parse_mode='html')
            menu_start(message)

    elif message.text == '⚙️ Настройки комнаты':
        menu_room_info(message)

    elif message.text == '👤 Личные настройки':
        menu_my_settings(message)

    elif message.text == '🛒 Список покупок':
        menu_shopping_list(message)

    elif message.text == '✅ Обязанности':
        menu_tasks_list(message)

    elif message.text == '🤖 О боте':
        help_text = ''
        with open("about.txt", "r", encoding='UTF8') as f:
            for line in f.readlines():
                help_text += line
        bot.send_message(message.chat.id, help_text, parse_mode='html', disable_web_page_preview=True)
        bot.register_next_step_handler(message, on_click_menu_start)

    elif message.text == '/test':
        command_test(message)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> Неизвестная команда. Попробуй еще раз!",
                             parse_mode='html')
        bot.register_next_step_handler(message, on_click_menu_start)


# ввод имени для создания комнаты
def create_new_room_name(message):
    if message.content_type == 'text':
        global var_create_room_name
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_start(message)
        else:
            bot.send_message(message.chat.id, f"Прекрасное название для комнаты: \"{message.text}\".\n"
                                              f"<b>Теперь придумай пароль "
                                              "(этот пароль можно будет поменять):</b>", parse_mode='html')
            var_create_room_name = message.text
            bot.register_next_step_handler(message, create_new_room_pass)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве имени комнаты может быть только <b>текст</b>!\n"
                                          f"<b>Введи название комнаты:</b>", parse_mode='html')
        bot.register_next_step_handler(message, create_new_room_name)


# ввод пароля и создание комнаты
def create_new_room_pass(message):
    global var_create_room_name
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_start(message)
        else:
            if len(message.text) >= 6:
                db_functions.create_new_room(message, var_create_room_name)
                bot.send_message(message.chat.id,
                                 f"Комната с названием <b>\"{var_create_room_name}\"</b> успешно создана!",
                                 parse_mode='html')
                var_create_room_name = None
                menu_start(message)
            else:
                bot.send_message(message.chat.id, f"<b>Ошибка!</b> Пароль не может быть короче 6 символов!\n"
                                                  f"<b>Придумай другой пароль:</b>", parse_mode='html')
                bot.register_next_step_handler(message, create_new_room_pass)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве пароля может быть только <b>текст</b>!\n"
                                          f"<b>Придумай пароль:</b>", parse_mode='html')
        bot.register_next_step_handler(message, create_new_room_pass)


# ввод id для присоединения к комнате
def join_new_room_id(message):
    if message.content_type == 'text':
        global var_join_room_id, var_join_room_name, var_join_room_pass
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_start(message)
        else:
            room_info = db_functions.check_room_by_id(message)
            if room_info:
                bot.send_message(message.chat.id, f"Комната <b>\"{room_info[2]}\"</b> найдена!\n"
                                                  f"<b>Введи пароль от комнаты:</b>", parse_mode='html')
                var_join_room_id = message.text
                var_join_room_name = room_info[2]
                var_join_room_pass = room_info[3]
                bot.register_next_step_handler(message, join_new_room_pass)
            else:
                bot.send_message(message.chat.id, f"<b>Ошибка!</b> "
                                                  f"Комната с <b>id={message.text}</b> не найдена.\n"
                                                  f"<b>Введи id для существующей комнаты:</b>", parse_mode='html')
                bot.register_next_step_handler(message, join_new_room_id)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве id может быть только <b>число</b>!\n"
                                          f"<b>Введи id комнаты:</b>", parse_mode='html')
        bot.register_next_step_handler(message, join_new_room_id)


# ввод пароля и присоединение к комнате
def join_new_room_pass(message):
    global var_join_room_id, var_join_room_name, var_join_room_pass
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_start(message)
        else:
            if db_functions.check_pass(message, var_join_room_pass):
                db_functions.join_user_on_room(message, var_join_room_id)
                bot.send_message(message.chat.id,
                                 f"Поздравляю! Ты теперь в комнате <b>\"{var_join_room_name}\"</b>!",
                                 parse_mode='html')
                var_join_room_id = var_join_room_name = var_join_room_pass = None
                menu_start(message)
            else:
                bot.send_message(message.chat.id, f"<b>Ошибка!</b> Неверный пароль!\n"
                                                  f"<b>Попробуй ввести пароль еще раз:</b>", parse_mode='html')
                bot.register_next_step_handler(message, join_new_room_pass)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве пароля может быть только <b>текст</b>!\n"
                                          f"<b>Попробуй ввести пароль еще раз:</b>", parse_mode='html')
        bot.register_next_step_handler(message, join_new_room_pass)


# меню информации о комнате
def menu_room_info(message):
    room = db_functions.get_user_room(message)
    if room:
        admin = db_functions.get_admin_by_room_id(room[0][0])
        users = db_functions.get_users_by_room_id(room[0][0])
        users_list = ''
        for user in users:
            users_list += f'[{user[1]}](t.me/{user[3]})\n'

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # если пользователь админ комнаты
        if room[0][1] == message.from_user.id:
            btn1 = types.KeyboardButton('✏️ Изменить название комнаты')
            btn2 = types.KeyboardButton('🔐 Изменить пароль от комнаты')
            btn3 = types.KeyboardButton('👑 Передать роль админа')
            btn4 = types.KeyboardButton('🗑️ Удалить комнату')
            btn5 = types.KeyboardButton('🚫 Покинуть комнату')
            btn6 = types.KeyboardButton('⬅️ Назад')
            markup.add(btn1, btn2)
            markup.add(btn3, btn4)
            markup.add(btn5)
            markup.add(btn6)
        else:
            btn1 = types.KeyboardButton('🚫 Покинуть комнату')
            btn2 = types.KeyboardButton('⬅️ Назад')
            markup.add(btn1)
            markup.add(btn2)

        bot.send_message(message.chat.id, f'__*Настройки комнаты*__\n\n'
                                          f'*Название:* {room[0][2]}\n'
                                          f'*ID:* `{room[0][0]}`\n'
                                          f'_\(нажми на ID, чтобы скопировать\)_\n'
                                          f'*Админ комнаты:* [{admin[1]}](t.me/{admin[3]})\n'
                                          f'*Участники:*\n'
                                          f'{users_list}\n'
                                          f'*Выбери команду из меню:*',
                         parse_mode='MarkdownV2', reply_markup=markup, disable_web_page_preview=True)
        bot.register_next_step_handler(message, on_click_menu_room_info)
    else:
        bot.send_message(message.chat.id,
                         f'<b>Ошибка!</b> У тебя нет комнаты. Создай новую или присоединись к существующей.',
                         parse_mode='html')
        bot.register_next_step_handler(message, on_click_menu_start)


# обработчик кнопок информация о комнате
def on_click_menu_room_info(message):
    if message.text == '/repair':
        command_repair(message)
    elif message.text == '⬅️ Назад':
        menu_start(message)
    elif message.text == '✏️ Изменить название комнаты':
        room = db_functions.get_user_room(message)
        if room[0][1] == message.from_user.id:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton('⬅️ Назад')
            markup.add(btn)
            bot.send_message(message.chat.id, f"Текущее название комнаты: <b>\"{room[0][2]}\"</b>.\n"
                                              f"<b>Введи новое название комнаты:</b>",
                             parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, edit_room_name)
        else:
            bot.send_message(message.chat.id, f"<b>Ошибка!</b> Ты не являешься админом комнаты.",
                             parse_mode='html')
            bot.register_next_step_handler(message, on_click_menu_room_info)

    elif message.text == '🚫 Покинуть комнату':
        room = db_functions.get_user_room(message)
        if not room[0][1] == message.from_user.id:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('🚫 Да, я точно хочу покинуть комнату')
            btn2 = types.KeyboardButton('⬅️ Назад')
            markup.add(btn1)
            markup.add(btn2)
            bot.send_message(message.chat.id, f"Ты действительно хочешь "
                                              f"покинуть комнату <b>\"{room[0][2]}\"</b>?\n"
                                              f"<b>Ты сможешь присоединиться к этой комнате "
                                              f"только зная его id и пароль!</b>",
                             parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, leave_room)
        else:
            bot.send_message(message.chat.id, f"<b>Ошибка!</b> Ты не можешь покинуть комнату, "
                                              f"пока являешься его админом. "
                                              f"Чтобы покинуть комнату, "
                                              f"передай роль админа другому участнику комнаты "
                                              f"или удали эту комнату полностью.", parse_mode='html')
            bot.register_next_step_handler(message, on_click_menu_room_info)

    elif message.text == '👑 Передать роль админа':
        room = db_functions.get_user_room(message)
        if room[0][1] == message.from_user.id:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            users = db_functions.get_users_by_room_id(room[0][0])
            for user in users:
                if user[0] != message.from_user.id:
                    markup.add(types.KeyboardButton(f'{user[1]} ({user[3]})'))
            btn1 = types.KeyboardButton('⬅️ Назад')
            markup.add(btn1)
            bot.send_message(message.chat.id,
                             f"Выбери, кому ты хочешь передать роль админа комнаты <b>\"{room[0][2]}\"</b>:",
                             parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, change_room_admin)
        else:
            bot.send_message(message.chat.id, f"<b>Ошибка!</b> Ты не являешься админом комнаты.",
                             parse_mode='html')
            bot.register_next_step_handler(message, on_click_menu_room_info)

    elif message.text == '🗑️ Удалить комнату':
        room = db_functions.get_user_room(message)
        if room[0][1] == message.from_user.id:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('🗑️ Да, я точно хочу удалить комнату')
            btn2 = types.KeyboardButton('⬅️ Назад')
            markup.add(btn1)
            markup.add(btn2)
            bot.send_message(message.chat.id, f"Ты действительно хочешь удалить комнату <b>\"{room[0][2]}\"</b>?\n"
                                              f"<b>Это действие нельзя будет отменить. "
                                              f"Все участники будут выгнаны и все данные о комнате, "
                                              f"включая покупки и долги будут удалены!</b>",
                             parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, delete_room)
        else:
            bot.send_message(message.chat.id, f"<b>Ошибка!</b> Ты не являешься админом комнаты.",
                             parse_mode='html')
            bot.register_next_step_handler(message, on_click_menu_room_info)

    elif message.text == '🔐 Изменить пароль от комнаты':
        room = db_functions.get_user_room(message)
        if room[0][1] == message.from_user.id:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton('⬅️ Назад')
            markup.add(btn)
            bot.send_message(message.chat.id, f'Смена пароля от комнаты <b>"{room[0][2]}"</b>.\n'
                                              f'<b>Введи новый пароль от комнаты:</b>',
                             parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, edit_room_pass)
        else:
            bot.send_message(message.chat.id, f"<b>Ошибка!</b> Ты не являешься админом комнаты.",
                             parse_mode='html')
            bot.register_next_step_handler(message, on_click_menu_room_info)

    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> Неизвестная команда. Попробуй еще раз!",
                         parse_mode='html')
        bot.register_next_step_handler(message, on_click_menu_room_info)


def edit_room_name(message):
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_room_info(message)
        else:
            room = db_functions.get_user_room(message)
            db_functions.edit_room_name(message, room[0][0])
            bot.send_message(message.chat.id,
                             f"Комната <b>\"{room[0][2]}\"</b> успешно переименована "
                             f"в <b>\"{message.text}\"</b>.\n", parse_mode='html')
            menu_room_info(message)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве имени комнаты "
                                          f"может быть только <b>текст</b>!\n"
                                          f"<b>Введи новое название комнаты:</b>", parse_mode='html')
        bot.register_next_step_handler(message, edit_room_name)


def edit_room_pass(message):
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_room_info(message)
        else:
            if len(message.text) >= 6:
                room = db_functions.get_user_room(message)
                db_functions.edit_room_pass(message, room[0][0])
                bot.send_message(message.chat.id,
                                 f"Пароль от комнаты <b>\"{room[0][2]}\"</b> успешно изменен!\n",
                                 parse_mode='html')
                menu_room_info(message)
            else:
                bot.send_message(message.chat.id, f"<b>Ошибка!</b> Пароль не может быть короче 6 символов!\n"
                                                  f"<b>Придумай другой пароль:</b>", parse_mode='html')
                bot.register_next_step_handler(message, edit_room_pass)
    else:
        bot.send_message(message.chat.id,
                         f"<b>Ошибка!</b> В качестве пароля от комнаты может быть только <b>текст</b>!\n"
                         f"<b>Введи новый пароль от комнаты:</b>", parse_mode='html')
        bot.register_next_step_handler(message, edit_room_pass)


def leave_room(message):
    if message.text == '/repair':
        command_repair(message)
    elif message.text == '⬅️ Назад':
        menu_room_info(message)
    elif message.text == '🚫 Да, я точно хочу покинуть комнату':
        room = db_functions.get_user_room(message)
        db_functions.leave_room(message)
        bot.send_message(message.chat.id,
                         f"Ты покинул комнату <b>\"{room[0][2]}\"</b>!", parse_mode='html')
        menu_start(message)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> Неизвестная команда. Попробуй еще раз!",
                         parse_mode='html')
        bot.register_next_step_handler(message, leave_room)


def change_room_admin(message):
    global var_new_admin
    if message.text == '/repair':
        command_repair(message)
    elif message.text == '⬅️ Назад':
        menu_room_info(message)
    else:
        room = db_functions.get_user_room(message)
        users = db_functions.get_users_by_room_id(room[0][0])
        var_new_admin = None
        for user in users:
            if user[0] != message.from_user.id:
                if message.text == f'{user[1]} ({user[3]})':
                    var_new_admin = user
                    break
        if var_new_admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('👑 Да, я точно хочу передать роль админа')
            btn2 = types.KeyboardButton('⬅️ Назад')
            markup.add(btn1)
            markup.add(btn2)
            bot.send_message(message.chat.id,
                             f'Ты точно хочешь передать роль админа комнаты <b>\"{room[0][2]}\"</b> '
                             f'пользователю <a href="t.me/{var_new_admin[3]}">{var_new_admin[1]}</a>?\n'
                             f'Это действие нельзя будет отменить!',
                             parse_mode='html', reply_markup=markup, disable_web_page_preview=True)
            bot.register_next_step_handler(message, change_room_admin_accept)
        else:
            bot.send_message(message.chat.id, f"<b>Ошибка!</b> Пользователь не найден!\n"
                                              f"<b>Выбери пользователя из меню:</b>", parse_mode='html')
            bot.register_next_step_handler(message, change_room_admin)


def change_room_admin_accept(message):
    global var_new_admin
    if message.text == '/repair':
        command_repair(message)
    elif message.text == '⬅️ Назад':
        menu_room_info(message)
    elif message.text == '👑 Да, я точно хочу передать роль админа':
        room = db_functions.get_user_room(message)
        db_functions.change_room_admin(message, room[0][0], var_new_admin)
        bot.send_message(message.chat.id,
                         f'Роль админа комнаты <b>\"{room[0][2]}\"</b> была передана '
                         f'пользователю <a href="t.me/{var_new_admin[3]}">{var_new_admin[1]}</a>!',
                         parse_mode='html', disable_web_page_preview=True)
        var_new_admin = None
        menu_room_info(message)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> Неизвестная команда. Попробуй еще раз!",
                         parse_mode='html')
        bot.register_next_step_handler(message, change_room_admin_accept)


def delete_room(message):
    if message.text == '/repair':
        command_repair(message)
    elif message.text == '⬅️ Назад':
        menu_room_info(message)
    elif message.text == '🗑️ Да, я точно хочу удалить комнату':
        room = db_functions.get_user_room(message)
        db_functions.delete_room(message, room[0][0])
        bot.send_message(message.chat.id,
                         f"Комната <b>\"{room[0][2]}\"</b> была полностью удалена!", parse_mode='html')
        menu_start(message)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> Неизвестная команда. Попробуй еще раз!",
                         parse_mode='html')
        bot.register_next_step_handler(message, delete_room)


def menu_my_settings(message):
    name = db_functions.get_user_by_id(message.from_user.id)[1]
    room = db_functions.get_user_room(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('✏️ Изменить имя')
    btn2 = types.KeyboardButton('⬅️ Назад')
    markup.row(btn1)
    markup.row(btn2)
    if not room:
        bot.send_message(message.chat.id,
                         f"__*Личные настройки*__\n\n"
                         f'*Текущее имя:* {name}\n'
                         f'Сейчас ты не состоишь в комнате\.\n\n'
                         f'*Выбери команду из меню:*',
                         parse_mode='MarkdownV2', reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
                         f"__*Личные настройки*__\n\n"
                         f'*Текущее имя:* {name}\n'
                         f'*Текущая комната:* {room[0][2]}\n\n'
                         f'*Выбери команду из меню:*',
                         parse_mode='MarkdownV2', reply_markup=markup)
    bot.register_next_step_handler(message, on_click_menu_my_settings)


def on_click_menu_my_settings(message):
    if message.text == '/repair':
        command_repair(message)
    elif message.text == '⬅️ Назад':
        menu_start(message)
    elif message.text == '✏️ Изменить имя':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('⬅️ Назад')
        markup.add(btn)
        bot.send_message(message.chat.id, f'<b>Введи новое имя:</b>', parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, edit_name)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> Неизвестная команда. Попробуй еще раз!",
                         parse_mode='html')
        bot.register_next_step_handler(message, on_click_menu_my_settings)


def edit_name(message):
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_my_settings(message)
        else:
            name = db_functions.get_user_by_id(message.from_user.id)[1]
            db_functions.edit_name(message)
            bot.send_message(message.chat.id,
                             f'Теперь тебя зовут не <b>"{name}"</b>, а <b>"{message.text}"</b>.\n',
                             parse_mode='html')
            menu_my_settings(message)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве имени может быть только <b>текст</b>!\n"
                                          f"<b>Введи новое имя:</b>", parse_mode='html')
        bot.register_next_step_handler(message, edit_name)


def menu_shopping_list(message):
    room = db_functions.get_user_room(message)
    if room:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('📝 Добавить продукт')
        btn2 = types.KeyboardButton('🗑️ Удалить продукт')
        btn3 = types.KeyboardButton('🔄 Переключить статус')
        btn4 = types.KeyboardButton('⬅️ Назад')
        markup.row(btn1, btn2)
        markup.row(btn3)
        markup.row(btn4)
        # получение списка продуктов
        shopping_list = db_functions.get_shopping_list(room[0][0])
        if shopping_list:
            output_shopping_list = '<u><b>Список покупок</b></u>\n\n'
            for buy in shopping_list:
                output_shopping_list += f'🆔 {buy[0]} 📦 {buy[2]} '
                if buy[3] == 1:
                    output_shopping_list += '✅\n'
                else:
                    output_shopping_list += '❌\n'
        else:
            output_shopping_list = '<u><b>Список покупок пуст</b></u>\n'
        output_shopping_list += '\n<b>Выбери команду из меню:</b>'
        bot.send_message(message.chat.id, f'{output_shopping_list}', parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, on_click_menu_shopping_list)
    else:
        bot.send_message(message.chat.id,
                         f'<b>Ошибка!</b> Пользоваться списком покупок можно только внутри комнаты. '
                         f'Создай новую или присоединись к существующей.', parse_mode='html')
        bot.register_next_step_handler(message, on_click_menu_start)


def on_click_menu_shopping_list(message):
    if message.text == '/repair':
        command_repair(message)
    elif message.text == '⬅️ Назад':
        menu_start(message)

    elif message.text == '📝 Добавить продукт':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('⬅️ Назад')
        markup.add(btn)
        bot.send_message(message.chat.id, f"Что нужно купить?\n"
                                          f"<b>Введи название продукта:</b>", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, add_product)

    elif message.text == '🗑️ Удалить продукт':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('⬅️ Назад')
        markup.add(btn)
        bot.send_message(message.chat.id, f"Какой продукт нужно удалить из списка?\n"
                                          f"<b>Введи ID продукта:</b>", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, delete_product)

    elif message.text == '🔄 Переключить статус':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('⬅️ Назад')
        markup.add(btn)
        bot.send_message(message.chat.id, f"У какого продукта нужно переключить статус?\n"
                                          f"<b>Введи ID продукта:</b>", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, switch_product)

    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> Неизвестная команда. Попробуй еще раз!",
                         parse_mode='html')
        bot.register_next_step_handler(message, on_click_menu_shopping_list)


def add_product(message):
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_shopping_list(message)
        else:
            room = db_functions.get_user_room(message)
            db_functions.add_product(message, room[0][0])
            bot.send_message(message.chat.id,
                             f"Продукт <b>\"{message.text}\"</b> добавлен "
                             f"в список покупок комнаты <b>\"{room[0][2]}\"</b>.", parse_mode='html')
            menu_shopping_list(message)
    else:
        bot.send_message(message.chat.id,
                         f"<b>Ошибка!</b> В качестве названия продукта может быть только <b>текст</b>!\n"
                         f"<b>Введи название продукта:</b>", parse_mode='html')
        bot.register_next_step_handler(message, add_product)


def delete_product(message):
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_shopping_list(message)
        else:
            room = db_functions.get_user_room(message)
            deleted_product = db_functions.delete_product(message, room[0][0])
            if deleted_product:
                bot.send_message(message.chat.id,
                                 f"Продукт <b>\"{deleted_product}\"</b> был удален "
                                 f"из списка покупок комнаты <b>\"{room[0][2]}\"</b>.", parse_mode='html')
                menu_shopping_list(message)
            else:
                bot.send_message(message.chat.id,
                                 f"<b>Ошибка!</b> Продукт c <b>ID={message.text}</b> не был найден "
                                 f"в списке покупок комнаты <b>\"{room[0][2]}\"</b>.\n"
                                 f"<b>Введи ID продукта еще раз:</b>", parse_mode='html')
                bot.register_next_step_handler(message, delete_product)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве ID продукта "
                                          f"может быть только <b>число</b>!\n"
                                          f"<b>Введи ID продукта:</b>", parse_mode='html')
        bot.register_next_step_handler(message, delete_product)


def switch_product(message):
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_shopping_list(message)
        else:
            room = db_functions.get_user_room(message)
            switch_result = db_functions.switch_product(message, room[0][0])
            if switch_result:
                if switch_result[1]:
                    bot.send_message(message.chat.id,
                                     f"Продукт <b>\"{switch_result[0]}\"</b> был отмечен как <b>купленный</b>.",
                                     parse_mode='html')
                else:
                    bot.send_message(message.chat.id,
                                     f"Продукт <b>\"{switch_result[0]}\"</b> был отмечен как <b>не купленный</b>.",
                                     parse_mode='html')
                menu_shopping_list(message)
            else:
                bot.send_message(message.chat.id,
                                 f"<b>Ошибка!</b> Продукт c <b>ID={message.text}</b> не был найден "
                                 f"в списке покупок комнаты <b>\"{room[0][2]}\"</b>.\n"
                                 f"<b>Введи ID продукта еще раз:</b>", parse_mode='html')
                bot.register_next_step_handler(message, switch_product)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве ID продукта "
                                          f"может быть только <b>число</b>!\n"
                                          f"<b>Введи ID продукта:</b>", parse_mode='html')
        bot.register_next_step_handler(message, switch_product)


# меню обязанностей
def menu_tasks_list(message):
    room = db_functions.get_user_room(message)
    if room:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if room[0][1] == message.from_user.id:
            btn1 = types.KeyboardButton('📝 Добавить задачу')
            btn2 = types.KeyboardButton('🗑️ Удалить задачу')
            markup.row(btn1, btn2)
        btn3 = types.KeyboardButton('☑️ Отметить как выполненную')
        btn4 = types.KeyboardButton('⬅️ Назад')
        markup.row(btn3)
        markup.row(btn4)
        # получение списка продуктов
        tasks_list = db_functions.get_tasks_list(room[0][0])
        if tasks_list:
            output_tasks_list = '<u><b>График обязанностей</b></u>\n\n'
            for task in tasks_list:
                output_tasks_list += f'{task}\n'
        else:
            output_tasks_list = '<u><b>Список задач пуст</b></u>\n'
        output_tasks_list += '\n<b>Выбери команду из меню:</b>'
        bot.send_message(message.chat.id, f'{output_tasks_list}', parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, on_click_menu_tasks_list)
    else:
        bot.send_message(message.chat.id,
                         f'<b>Ошибка!</b> Пользоваться списком задач можно только внутри комнаты. '
                         f'Создай новую или присоединись к существующей.', parse_mode='html')
        bot.register_next_step_handler(message, on_click_menu_start)


def on_click_menu_tasks_list(message):
    if message.text == '/repair':
        command_repair(message)
    elif message.text == '⬅️ Назад':
        menu_start(message)

    elif message.text == '📝 Добавить задачу':
        room = db_functions.get_user_room(message)
        if room[0][1] == message.from_user.id:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton('⬅️ Назад')
            markup.add(btn)
            bot.send_message(message.chat.id, f"Какую задачу хочешь добавить?\n"
                                              f"<b>Введи название задачи:</b>", parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, add_task)
        else:
            bot.send_message(message.chat.id, f"<b>Ошибка!</b> Добавлять задачи может только админ комнаты.",
                             parse_mode='html')
            bot.register_next_step_handler(message, menu_tasks_list)

    elif message.text == '🗑️ Удалить задачу':
        room = db_functions.get_user_room(message)
        if room[0][1] == message.from_user.id:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton('⬅️ Назад')
            markup.add(btn)
            bot.send_message(message.chat.id, f"Какую задачу хочешь удалить?\n"
                                              f"<b>Введи ID задачи:</b>", parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(message, delete_task)
        else:
            bot.send_message(message.chat.id, f"<b>Ошибка!</b> Удалять задачи может только админ комнаты.",
                             parse_mode='html')
            bot.register_next_step_handler(message, on_click_menu_room_info)

    elif message.text == '☑️ Отметить как выполненную':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('⬅️ Назад')
        markup.add(btn)
        bot.send_message(message.chat.id, f"Какую задачу нужно отметить как выполненную?\n"
                                          f"<b>Введи ID задачи:</b>", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, switch_task)

    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> Неизвестная команда. Попробуй еще раз!",
                         parse_mode='html')
        bot.register_next_step_handler(message, on_click_menu_tasks_list)


def add_task(message):
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_tasks_list(message)
        else:
            room = db_functions.get_user_room(message)
            next_executor = db_functions.add_task(message, room[0][0])
            bot.send_message(message.chat.id,
                             f"Задача <b>\"{message.text}\"</b> была добавлена "
                             f"в список задач комнаты <b>\"{room[0][2]}\"</b>.\n"
                             f"Следующий выполняющий этой задачи: "
                             f"<a href='t.me/{next_executor[1]}'>{next_executor[0]}</a>",
                             parse_mode='html', disable_web_page_preview=True)
            menu_tasks_list(message)
    else:
        bot.send_message(message.chat.id,
                         f"<b>Ошибка!</b> В качестве названия задачи может быть только <b>текст</b>!\n"
                         f"<b>Введи название задачи:</b>", parse_mode='html')
        bot.register_next_step_handler(message, add_task)


def delete_task(message):
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_tasks_list(message)
        else:
            room = db_functions.get_user_room(message)
            deleted_task = db_functions.delete_task(message, room[0][0])
            if deleted_task:
                bot.send_message(message.chat.id,
                                 f"Задача <b>\"{deleted_task}\"</b> была удалена "
                                 f"из списка задач комнаты <b>\"{room[0][2]}\"</b>.", parse_mode='html')
                menu_tasks_list(message)
            else:
                bot.send_message(message.chat.id,
                                 f"<b>Ошибка!</b> Задача c <b>ID={message.text}</b> не была найдена "
                                 f"в списке задач комнаты <b>\"{room[0][2]}\"</b>.\n"
                                 f"<b>Введи ID задачи еще раз:</b>", parse_mode='html')
                bot.register_next_step_handler(message, delete_task)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве ID задачи "
                                          f"может быть только <b>число</b>!\n"
                                          f"<b>Введи ID задачи:</b>", parse_mode='html')
        bot.register_next_step_handler(message, delete_task)


def switch_task(message):
    if message.content_type == 'text':
        if message.text == '/repair':
            command_repair(message)
        elif message.text == '⬅️ Назад':
            menu_tasks_list(message)
        else:
            room = db_functions.get_user_room(message)
            switch_result = db_functions.switch_task(message, room[0][0])
            if switch_result:
                if switch_result != 'error':
                    bot.send_message(message.chat.id,
                                     f"Задача <b>\"{switch_result[0][2]}\"</b> была выполнена пользователем "
                                     f"<a href='t.me/{switch_result[1][3]}'>{switch_result[1][1]}</a>.\n"
                                     f"Следующий выполняющий этой задачи: "
                                     f"<a href='t.me/{switch_result[2][3]}'>{switch_result[2][1]}</a>.",
                                     parse_mode='html', disable_web_page_preview=True)
                else:
                    bot.send_message(message.chat.id,
                                     f"Ты не можешь отметить задачу как выполненная, так как она принадлежит вам.\n"
                                     f"<b>Это должен сделать кто-то другой!</b>",
                                     parse_mode='html', disable_web_page_preview=True)
                menu_tasks_list(message)
            else:
                bot.send_message(message.chat.id,
                                 f"<b>Ошибка!</b> Задача c <b>ID={message.text}</b> не была найдена "
                                 f"в списке задач комнаты <b>\"{room[0][2]}\"</b>.\n"
                                 f"<b>Введи ID задачи еще раз:</b>", parse_mode='html')
                bot.register_next_step_handler(message, switch_product)
    else:
        bot.send_message(message.chat.id, f"<b>Ошибка!</b> В качестве ID задачи "
                                          f"может быть только <b>число</b>!\n"
                                          f"<b>Введи ID задачи:</b>", parse_mode='html')
        bot.register_next_step_handler(message, switch_task)


# тестовый обработчик
@bot.message_handler(commands=['test'])
def command_test(message):
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    info = 'Таблица "users"\n\n'
    for el in users:
        info += f'id: {el[0]}, name: {el[1]}, room_id: {el[2]}\n\n'
    bot.send_message(message.chat.id, info)

    cur.execute("SELECT * FROM rooms")
    rooms = cur.fetchall()
    info = 'Таблица "rooms"\n\n'
    for el in rooms:
        info += f'id: {el[0]}, admin_id: {el[1]}, name: {el[2]}, pass: {el[3]}\n\n'
    bot.send_message(message.chat.id, info)

    cur.execute("SELECT * FROM shopping_list")
    shopping_list = cur.fetchall()
    info = 'Таблица "shopping_list"\n\n'
    for el in shopping_list:
        info += f'id: {el[0]}, room_id: {el[1]}, name: {el[2]}, is_completed: {el[3]}\n\n'
    bot.send_message(message.chat.id, info)

    cur.execute("SELECT * FROM tasks_list")
    tasks_list = cur.fetchall()
    info = 'Таблица "tasks_list"\n\n'
    for el in tasks_list:
        info += f'id: {el[0]}, room_id: {el[1]}, name: {el[2]}, executer: {el[3]}\n\n'
    bot.send_message(message.chat.id, info)

    cur.close()
    conn.close()


# обработка команды repair
@bot.message_handler(commands=['repair'])
def command_repair(message):
    bot.send_message(message.chat.id, 'Бот был починен. <b>Отправь любое сообщение, чтобы продолжить.</b>',
                     parse_mode='html')


# обработка остального текста
@bot.message_handler()
def other_messages(message):
    menu_start(message)


print("Бот запущен...")
bot.infinity_polling(skip_pending=True, timeout=10, long_polling_timeout=5)