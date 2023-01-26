import sqlite3


class SQL:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()  # работа с БД

    def get_session(self):
        try:
            answer = self.__cur.execute(f"SELECT * FROM session_result ORDER BY ID DESC").fetchall()
            return answer
        except sqlite3.Error as e:
            print("(get_session) Ошибка получения запроса в БД:\n" + str(e))
            return []

    def add_session(self, score, levels, time, rating, mode):
        try:
            self.__cur.execute(f"INSERT INTO session_result VALUES (NULL, ?, ?, ?, ?, ?)",
                               (score, levels, time, rating, mode))
            self.__db.commit()
        except sqlite3.Error as e:
            print("(add_session) Ошибка запроса:\n" + str(e))