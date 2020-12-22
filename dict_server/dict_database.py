"""
数据库交互
"""
import pymysql


class Database:
    def __init__(self):
        self.db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", database="dict",
                                  charset="utf8")

    def cursor(self):
        self.cur = self.db.cursor()

    def register(self, name, psw):
        sql = "insert into users(name,password) values(%s,%s)"
        try:
            self.cur.execute(sql, [name, psw])
            self.db.commit()
            return True
        except Exception:
            return False

    def login(self, name, psw):
        sql = "select name from users where binary name = %s and binary password = %s"
        self.cur.execute(sql, [name, psw])
        if self.cur.fetchone():
            return True
        else:
            return False

    def query(self, name, word):
        sql = "select mean from words where word = %s"
        if self.cur.execute(sql, [word]):
            mean = self.cur.fetchone()[0]
            user_id = self.__get_user_id(name)
            word_id = self.__get_word_id(word)
            self.__add_history(user_id, word_id)
            self.db.commit()
            return mean
        else:
            return False

    def __get_user_id(self, name):
        sql = "select id from users where name = %s"
        self.cur.execute(sql, [name])
        return self.cur.fetchone()[0]

    def __get_word_id(self, word):
        sql = "select id from words where word = %s"
        self.cur.execute(sql, [word])
        return self.cur.fetchone()[0]

    def __add_history(self, user_id, word_id):
        sql = "insert into history(user_id,word_id) values(%s,%s)"
        self.cur.execute(sql, [user_id, word_id])

    def history(self, name1):
        sql = "select name,word,time from history left join users on users.id = history.user_id left join words on history.word_id = words.id where name = %s order by time desc limit 10;"
        if self.cur.execute(sql, [name1]):
            return self.cur.fetchall()
        else:
            return

    def close(self):
        self.db.close()
