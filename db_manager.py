import sqlite3
import random


class DbManage:

    def __init__(self, db_name):
        try:
            with sqlite3.connect(db_name) as conn:
                self.__conn = conn
                self.__cursor = conn.cursor()
        except:
            print('no connect to base')

    def create_tables(self):
        self.__cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE,"
                              " TEXT DEFAULT CURRENT_TIMESTAMP);")
        self.__cursor.execute("CREATE TABLE words (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                              " user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE RESTRICT,"
                              " date TEXT DEFAULT CURRENT_TIMESTAMP, word TEXT UNIQUE, translate TEXT);")

    def add_user(self, user_id):
        self.__cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES(?)", (user_id,))
        self.__conn.commit()

    def add_word(self, user_id, word, translate):
        self.__cursor.execute("INSERT OR IGNORE INTO words (user_id, word, translate)"
                              " VALUES(?, ?, ?);", (user_id, word, translate))
        self.__conn.commit()

    def find_word(self, text):
        result = self.__cursor.execute(f"SELECT word, translate FROM words WHERE word LIKE '{text}' or translate LIKE '{text}';")
        return result.fetchone()

    def get_word_for_test(self):
        word = self.__cursor.execute("SELECT word, translate FROM words").fetchall()
        words = random.choices(word, k=4)
        variants = [words[0][1], words[1][1], words[2][1], words[3][1]]
        random.shuffle(variants)
        return words[0], tuple(variants)
        



# db = DbManage('words.db')
# print(db.get_word_for_test())      
