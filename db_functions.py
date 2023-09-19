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
    # todo: другие таблицы
    cur.close()
    conn.close()


def is_user_have_in_db(message):
    """ Проверка наличия пользователя в бд. Возвращает True или False. """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id=?', (message.from_user.id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return False if not result else True


def create_new_user(message):
    """ Создание нового пользователя """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (id, name) VALUES (?, ?)", (message.from_user.id, message.text))
    conn.commit()
    cur.close()
    conn.close()


def get_user_name(message):
    """ Поиск имени пользователя по ID """
    conn = sqlite3.connect('chatbot.db')
    cur = conn.cursor()
    cur.execute("SELECT name FROM users  WHERE id=?", (message.from_user.id,))
    query = cur.fetchall()
    cur.close()
    conn.close()
    return query[0][0]


def is_user_have_room(message):
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
        print(result2)
        cur.close()
        conn.close()
        return result2
    else:
        return False
