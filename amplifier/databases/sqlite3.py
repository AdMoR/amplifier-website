import sqlite3


class SQLiteDB:

    def __init__(self, path='example.db'):
        self.path = path
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()

        self.table_exists = \
            lambda table_name: cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".\
                format(table_name)).fetchone()

        if not self.table_exists("templates"):
            cursor.execute(
                '''CREATE TABLE templates
                 (category_id int,category text, adapted_category text, template text)
                '''
            )
        conn.close()

    def get_template(self, table, category):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        t = (table, category)
        cursor.execute('SELECT * FROM ? WHERE symbol=?', t)
        rez = cursor.fetchone()[3]
        conn.close()
        return rez

    def add_template(self, category , adapted_category, template, category_id=None):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO templates VALUES (?, ?, ?, ?)",
                            (0 if not category_id else category_id, category, adapted_category, template))
        conn.close()
