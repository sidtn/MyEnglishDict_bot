import sqlite3
import random
from gtts import gTTS
import shutil
import os
from tqdm import tqdm
from get_data_for_base import *


class DbManage:

    def __init__(self, db_name):
        try:
            with sqlite3.connect(db_name) as conn:
                self.__conn = conn
                self.__cursor = conn.cursor()
        except:
            print('no connection to base')

    def create_tables(self):
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS users "
                              "(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE,"
                              "date TEXT DEFAULT CURRENT_TIMESTAMP);")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS words (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                              " user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,"
                              " date TEXT DEFAULT CURRENT_TIMESTAMP, word TEXT, translate TEXT);")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS irregularverb "
                              "(id INTEGER PRIMARY KEY AUTOINCREMENT, form1 TEXT UNIQUE NOT NULL,"
                              " form2 TEXT NOT NULL, form3 TEXT NOT NULL, translate NOT NULL)")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS verbform "
                              "(id INTEGER PRIMARY KEY AUTOINCREMENT, form TEXT NOT NULL)")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS verbs "
                              "(id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT UNIQUE NOT NULL,"
                              "form INTEGER NOT NULL REFERENCES verbform (id) ON DELETE RESTRICT)")

    def get_users(self):
        userslist = [user[0] for user in self.__cursor.execute("SELECT user_id FROM users").fetchall()]
        return userslist
                           
    def add_user(self, user_id):
        self.__cursor.execute("INSERT INTO users (user_id) VALUES(?)", (user_id,))
        self.__conn.commit()

    def add_word(self, user_id, word, translate):
        self.__cursor.execute("INSERT INTO words (user_id, word, translate)"
                              " VALUES(?, ?, ?);", (user_id, word, translate))
        self.__conn.commit()

    def find_word(self, text, user_id=None):
        if user_id:
            result = self.__cursor.execute("SELECT word, translate FROM words"
                                           " WHERE user_id=(?) and word LIKE (?)"
                                           "or translate LIKE (?);", (user_id, text, text,))
        else:
            result = self.__cursor.execute("SELECT word, translate FROM words WHERE word LIKE (?)"
                                           "or translate LIKE (?);", (text, text,))
        return result.fetchone()

    def get_word_for_test(self, for_user=None):
        all_records = self.__cursor.execute("SELECT word, translate FROM words WHERE user_id=(?);", 
                                               (for_user,)).fetchall()
        if len(all_records) >= 4:    
            words = random.choices(all_records, k=4)
            variants = [words[0][0], words[1][0], words[2][0], words[3][0]]
            random.shuffle(variants)
            return words[1], tuple(variants)
        else:
            return ()

    def get_count_words(self, user_id):
        count = self.__cursor.execute("SELECT count(word) FROM words WHERE user_id = (?)", (user_id,)).fetchone()
        return count[0]

    def get_irregular_vebs(self, word):
        result = self.__cursor.execute("SELECT * FROM irregularverb WHERE form1 LIKE (?)"
                                       "OR form2 LIKE (?) OR form3 LIKE (?) OR translate LIKE (?)",
                                       (word.lower(), word.lower(), word.lower(), word.title()))
        return result.fetchone()

    def get_data_from_verbs(self, word):
        result = self.__cursor.execute("SELECT word, verbform.form FROM verbs JOIN verbform ON"
                                       " verbs.form = verbform.id WHERE word LIKE (?);", (word,))
        return result.fetchone()

    def get_words_for_delete(self, user_id):
        words = self.__cursor.execute("SELECT word, translate FROM words WHERE user_id LIKE (?)"
                                      "ORDER BY rowid DESC LIMIT 5;", (user_id,)).fetchall()
        return words

    def del_record(self, word, user_id):
        record = self.__cursor.execute("DELETE FROM words WHERE word LIKE (?) AND user_id = (?);", (word, user_id,))
        self.__conn.commit()   

    def download_audio(self):
        try:
            shutil.rmtree('words_audio')
            os.mkdir('words_audio')
        except OSError:
            os.mkdir('words_audio')
        all_words = set(self.__cursor.execute("SELECT word FROM words").fetchall())
        for text in tqdm(all_words, total=len(all_words)):
            tts = gTTS(text=text[0], lang='en')
            tts.save(f'words_audio/{text[0]}.mp3')


    def insert_data_irregular(self, data):
        for row in data:
            self.__cursor.execute("INSERT OR IGNORE INTO irregularverb"
                "(form1, form2, form3, translate) VALUES(?, ?, ?, ?)", row)
            self.__conn.commit()

    def insert_data_gerund(self, data):
        for num, list_words in enumerate(data, 1):
            for word in list_words:
                self.__cursor.execute("INSERT OR IGNORE INTO verbs(word, form)"
                    " VALUES(?, ?)", (word, num))
                self.__conn.commit()


db = DbManage('words.db')
# db.insert_data_gerund(get_gerund_or_inf())
# db.insert_data_irregular(get_irregular_verbs())
# db.download_audio()
db.get_word_for_test()
