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
                'room_id VARCHAR(50),'
                'username VARCHAR(50) NOT NULL)')
    conn.commit()

    cur.execute('CREATE TABLE IF NOT EXISTS rooms ('
                'id INTEGER PRIMARY KEY,'
                'admin_id INTEGER UNIQUE NOT NULL,'
                'name VARCHAR(50) NOT NULL,'
                'password VARCHAR(50) NOT NULL)')
    conn.commit()

    cur.execute('CREATE TABLE IF NOT EXISTS shopping_list ('
                'id INTEGER PRIMARY KEY,'
                'room_id INTEGER NOT NULL,'
                'name VARCHAR(50) NOT NULL,'
                'is_completed BOOLEAN NOT NULL DEFAULT 0)')
    conn.commit()

    cur.execute('CREATE TABLE IF NOT EXISTS tasks_list ('
                'id INTEGER PRIMARY KEY,'
                'room_id INTEGER NOT NULL,'
                'name VARCHAR(50) NOT NULL,'
                'executor_id INTEGER NOT NULL)')
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


def get_user_by_id(user_id):
    """ Поиск пользователя. Возвращает данные о пользователе или False """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    query = cur.fetchall()
    cur.close()
    conn.close()
    return query[0] if query else False


def set_username(message):
    """ Обновление имени пользователя (username) при его смене """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET username=? WHERE id=?", (message.from_user.username, message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()


def get_user_room(message):
    """ Проверка наличия комнаты у пользователя в бд. Возвращает данные о комнате или False """
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
    cur.execute("SELECT * FROM rooms WHERE id=?", (message.text,))
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
    new_password = salt + key
    return new_password


def check_pass_by_room_id(message, room_id):
    """ Проверка пароля по id комнаты. Возвращает True или False """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT password FROM rooms WHERE id=?", (room_id,))
    password = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    true_salt = password[:32]
    true_key = password[32:]
    key = hashlib.pbkdf2_hmac('sha256', message.text.encode('utf-8'), true_salt, 10000)
    return True if true_key == key else False


def get_admin_by_room_id(room_id):
    """ Поиск админа по id комнаты """
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
    """ Получение участников комнаты по id комнаты """
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


def edit_room_pass(message, room_id):
    """ Редактирование пароля от комнаты по его id """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    new_password = hashing_pass(message.text)
    cur.execute("UPDATE rooms SET password=? WHERE id=?", (new_password, room_id))
    conn.commit()
    cur.close()
    conn.close()


def leave_room(message):
    """ Покидание комнаты по его id """
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


def delete_room(message, room_id):
    """ Удаление комнаты по его id """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET room_id=? WHERE room_id=?", (None, room_id))
    conn.commit()
    cur.execute("DELETE FROM rooms WHERE id=?", (room_id,))
    conn.commit()
    cur.execute("DELETE FROM shopping_list WHERE room_id=?", (room_id,))
    conn.commit()
    cur.execute("DELETE FROM tasks_list WHERE room_id=?", (room_id,))
    conn.commit()
    # todo: удалить данные и с других таблиц
    cur.close()
    conn.close()


def edit_name(message):
    """ Редактирование имени """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET name=? WHERE id=?", (message.text, message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()


def delete_user(message):
    """ Удаление профиля """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (message.from_user.id, ))
    conn.commit()
    cur.close()
    conn.close()


def get_shopping_list(room_id):
    """ Получение списка покупок по id комнаты """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM shopping_list WHERE room_id=?", (room_id,))
    shopping_list = cur.fetchall()
    cur.close()
    conn.close()
    return shopping_list


def add_product(message, room_id):
    """ Добавление продукта в список покупок """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    # получение списка существующих id
    cur.execute("SELECT id FROM shopping_list")
    products = cur.fetchall()
    products_id_list = []
    for product in products:
        products_id_list.append(product[0])
    # поиск свободного id
    new_product_id = None
    id_min, id_max = 1, 10  # выбор диапазона id
    while not new_product_id:
        for id in range(id_min, id_max):
            if id not in products_id_list:  # если найден свободный id
                new_product_id = id
                break
        if not new_product_id:  # если в выбранном диапазоне не осталось свободных id, диапазон расширяется в 10 раз
            id_min *= 10
            id_max *= 10
    # добавление продукта
    cur.execute("INSERT INTO shopping_list (id, room_id, name) VALUES (?, ?, ?)",
                (new_product_id, room_id, message.text))
    conn.commit()
    cur.close()
    conn.close()


def delete_product(buy_id):
    """ Удаление продукта из списка покупок """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM shopping_list WHERE id=? ", str(buy_id))
    conn.commit()
    cur.close()
    conn.close()


def switch_product(buy_id):
    """ Смена статуса продукта в списке покупок """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM shopping_list")
    shopping_list = cur.fetchall()
    for buy in shopping_list:
        if buy[0] == buy_id:
            if buy[3]:
                cur.execute("UPDATE shopping_list SET is_completed=0 WHERE id=?", (buy_id, ))
            else:
                cur.execute("UPDATE shopping_list SET is_completed=1 WHERE id=?", (buy_id,))
            conn.commit()
    cur.close()
    conn.close()


def get_tasks_list(room_id):
    """ Получение списка задач по id комнаты """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks_list WHERE room_id=?", (room_id,))
    tasks_list = cur.fetchall()
    cur.close()
    conn.close()
    return tasks_list


def add_task(message, room_id):
    """ Добавление задачи в список задач. Возвращает id и username следующего выполняющего """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    # получение списка существующих id
    cur.execute("SELECT id FROM tasks_list")
    tasks = cur.fetchall()
    tasks_id_list = []
    for task in tasks:
        tasks_id_list.append(task[0])
    # поиск свободного id
    new_task_id = None
    id_min, id_max = 1, 10  # выбор диапазона id
    while not new_task_id:
        for id in range(id_min, id_max):
            if id not in tasks_id_list:  # если найден свободный id
                new_task_id = id
                break
        if not new_task_id:  # если в выбранном диапазоне не осталось свободных id, диапазон расширяется в 10 раз
            id_min *= 10
            id_max *= 10
    # получение списка участников комнаты
    users = get_users_by_room_id(room_id)
    # добавление задачи
    cur.execute("INSERT INTO tasks_list (id, room_id, name, executor_id) VALUES (?, ?, ?, ?)",
                (new_task_id, room_id, message.text, users[0][0]))
    conn.commit()
    cur.close()
    conn.close()
    return users[0][1], users[0][3]


def delete_task(task_id):
    """ Удаление задачи из списка задач """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks_list WHERE id=? ", str(task_id))
    conn.commit()
    cur.close()
    conn.close()


def get_next_user(user_id, room_id):
    """ Принимает текущего пользователя и id комнаты. Возвращает следующего пользователя в комнате """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    users = get_users_by_room_id(room_id)
    need_next_user = False
    next_user = None
    for user in users:
        if need_next_user:
            next_user = user
            break
        if user[0] == user_id:
            if user == users[-1]:
                next_user = users[0]
                break
            else:
                need_next_user = True
    cur.close()
    conn.close()
    return next_user


def switch_task(task_id, room_id):
    """ Смена выполняющего задачи. Возвращает текущего и следующего выполняющего """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    # получение списка задач
    cur.execute("SELECT * FROM tasks_list")
    tasks = cur.fetchall()
    # получение списка участников комнаты
    users = get_users_by_room_id(room_id)
    for task in tasks:
        if task[0] == task_id:
            for user in users:
                if user[0] == task[3]:
                    next_executor = get_next_user(user[0], room_id)
                    cur.execute("UPDATE tasks_list SET executor_id=? WHERE id=?",
                                (next_executor[0], task[0]))
                    conn.commit()
                    cur.close()
                    conn.close()
                    return task[2], user, next_executor
