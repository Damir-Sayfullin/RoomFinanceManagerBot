import hashlib
import os
import sqlite3
from random import randint


def create_tables():
    """ Создает таблицы в бд, если их не существует. """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users ('
                'id INTEGER PRIMARY KEY,'
                'name VARCHAR(50) NOT NULL,'
                'room_id VARCHAR(50),'
                'username VARCHAR(50) NOT NULL)')
    conn.commit()

    cur.execute('CREATE TABLE IF NOT EXISTS rooms ('
                'id INTEGER PRIMARY KEY,'
                'admin_id INTEGER UNIQUE NOT NULL,'
                'name VARCHAR(50) NOT NULL,'
                'password VARCHAR(50) NOT NULL)')
    conn.commit()

    # todo: другие таблицы

    cur.close()
    conn.close()


def create_new_user(message):
    """ Создание нового пользователя """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (id, name, username) VALUES (?, ?, ?)",
                (message.from_user.id, message.text, message.from_user.username))
    conn.commit()
    cur.close()
    conn.close()


def get_user_name(message):
    """ Поиск имени пользователя по ID. Возвращает имя пользователя или False."""
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users  WHERE id=?", (message.from_user.id,))
    query = cur.fetchall()
    cur.close()
    conn.close()
    return query[0][1] if query else False


def get_user_room(message):
    """ Проверка наличия комнаты у пользователя в бд. Возвращает данные о комнате или False. """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute('SELECT room_id FROM users WHERE id=?', (message.from_user.id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    if result[0][0]:
        conn = sqlite3.connect('chatbot.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM rooms WHERE id=?', (result[0][0],))
        result2 = cur.fetchall()
        cur.close()
        conn.close()
        return result2
    else:
        return False


def create_new_room(message, room_name):
    """ Создание новой комнаты """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    # хеширование пароля
    password = hashing_pass(message.text)
    # получение списка существующих id
    cur.execute("SELECT id FROM rooms")
    rooms = cur.fetchall()
    rooms_id_list = []
    for room in rooms:
        rooms_id_list.append(room[0])
    # поиск свободного id
    new_room_id = None
    id_min, id_max = 100000, 1000000  # выбор диапазона id
    while not new_room_id:
        for id in range(id_min, id_max):
            if id not in rooms_id_list:  # если найден свободный id
                new_room_id = id
                break
        if not new_room_id:  # если в выбранном диапазоне не осталось свободных id, диапазон расширяется в 10 раз
            id_min *= 10
            id_max *= 10
    # создание комнаты с полученным названием
    cur.execute("INSERT INTO rooms (id, admin_id, name, password) VALUES (?, ?, ?, ?)",
                (new_room_id, message.from_user.id, room_name, password))
    conn.commit()
    # получение id комнаты
    cur.execute('SELECT id FROM rooms WHERE admin_id=? AND name=?', (message.from_user.id, room_name))
    room_id = cur.fetchall()
    # присвоение id комнаты создателю
    cur.execute("UPDATE users SET room_id=? WHERE id=?", (room_id[0][0], message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()


def check_room_by_id(message):
    """ Поиск комнаты по ID. Возвращает информацию о комнате или False."""
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms  WHERE id=?", (message.text,))
    query = cur.fetchall()
    cur.close()
    conn.close()
    return query[0] if query else False


def join_user_on_room(message, room_id):
    """ Присвоение пользователю комнаты """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET room_id=? WHERE id=?", (room_id, message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()


def hashing_pass(password):
    """ Хеширование пароля. Возвращает соленый ключ """
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 10000)
    storage = salt + key
    return storage


def check_pass(message, password):
    """ Проверка пароля. Возвращает True или False"""
    true_salt = password[:32]
    true_key = password[32:]
    key = hashlib.pbkdf2_hmac('sha256', message.text.encode('utf-8'), true_salt, 10000)
    return True if true_key == key else False


def get_admin_by_room_id(room_id):
    """ Поиск имени админа по id комнаты """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT admin_id FROM rooms WHERE id=?", (room_id,))
    admin_id = cur.fetchall()
    cur.execute("SELECT * FROM users WHERE id=?", (admin_id[0][0],))
    admin = cur.fetchall()
    cur.close()
    conn.close()
    return admin[0]


def get_users_by_room_id(room_id):
    """ Поиск участников комнаты по id комнаты """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE room_id=?", (room_id,))
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users


def edit_room_name(message, room_id):
    """ Редактирование названия комнаты по его id """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("UPDATE rooms SET name=? WHERE id=?", (message.text, room_id))
    conn.commit()
    cur.close()
    conn.close()

def leave_room(message):
    """ Удаление комнаты у пользователя по его id """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET room_id=? WHERE id=?", (None, message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()


def change_room_admin(message, room_id, new_admin_user):
    """ Передача роли админа комнаты по id комнаты и новому админу """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("UPDATE rooms SET admin_id=? WHERE id=?", (new_admin_user[0], room_id))
    conn.commit()
    cur.close()
    conn.close()