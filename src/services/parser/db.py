import sqlite3

from config.const import DB_FILE_PATH


class TinyDB():
    def __init__(self):
        self.db_name = DB_FILE_PATH
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Items(track TEXT)")
        self.conn.commit()

    def close_db(self):
        self.cursor.close()
