import hashlib
import os
import sqlite3


def create_tables():
    """ Создает таблицы в бд, если их не существует. """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users ('
                'id INTEGER PRIMARY KEY,'
                'name VARCHAR(50) NOT NULL,'
                'room_id VARCHAR(50))')
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
    cur.execute("INSERT INTO users (id, name) VALUES (?, ?)", (message.from_user.id, message.text))
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
    # todo: проверка на наличие комнаты с таким же именем
    # хеширование пароля
    password = hashing_pass(message.text)
    # создание комнаты с полученным названием
    cur.execute("INSERT INTO rooms (admin_id, name, password) VALUES (?, ?, ?)",
                (message.from_user.id, room_name,  password))
    conn.commit()
    # получение id комнаты
    cur.execute('SELECT id FROM rooms WHERE admin_id=? AND name=?', (message.from_user.id, room_name))
    room_id = cur.fetchall()
    # присвоение id комнаты создателю
    cur.execute("UPDATE users SET room_id=? WHERE id=?", (room_id[0][0], message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()


def hashing_pass(password):
    # Пример генерации
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 1000)

    storage = salt + key
    return storage
