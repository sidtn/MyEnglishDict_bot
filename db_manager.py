from collections import UserList
import sqlite3
import random
from aiogram.types import user
from gtts import gTTS
import shutil
import os
from tqdm import tqdm




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

    def get_users(self):
         userslist = [user[0] for user in self.__cursor.execute("SELECT user_id FROM users").fetchall()]
         return userslist
                           
    def add_user(self, user_id):
        self.__cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES(?)", (user_id,))
        self.__conn.commit()

    def add_word(self, user_id, word, translate):
        self.__cursor.execute("INSERT OR IGNORE INTO words (user_id, word, translate)"
                              " VALUES(?, ?, ?);", (user_id, word, translate))
        self.__conn.commit()

    def find_word(self, text):
        result = self.__cursor.execute("SELECT word, translate FROM words WHERE word LIKE (?)"
                                       "or translate LIKE (?);", (text, text,))
        return result.fetchone()

    def get_word_for_test(self):
        all_records = self.__cursor.execute("SELECT word, translate FROM words;").fetchall()
        words = random.choices(all_records, k=4)
        variants = [words[0][1], words[1][1], words[2][1], words[3][1]]
        random.shuffle(variants)
        return words[0], tuple(variants)

    def get_words_for_delete(self, user_id):
        words = self.__cursor.execute("SELECT word, translate FROM words WHERE user_id LIKE (?)"
                                      "ORDER BY rowid DESC LIMIT 10;", (user_id,)).fetchall()
        return words

    def del_record(self, word):
        record = self.__cursor.execute("DELETE FROM words WHERE word LIKE (?);", (word,))
        self.__conn.commit()   
     
    def download_audio(self):
        try:
            shutil.rmtree('words_audio')
            os.mkdir('words_audio')
        except OSError:
            os.mkdir('words_audio')           
        all_words = self.__cursor.execute("SELECT word FROM words").fetchall()
        for text in tqdm(all_words, total=len(all_words)):
            tts = gTTS(text=text[0], lang='en')
            tts.save(f'words_audio/{text[0]}.mp3')




# db = DbManage('words.db')
# print(db.get_word_for_test())
