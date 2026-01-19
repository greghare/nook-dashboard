import sqlite3

class TodoClient:
    def __init__(self, db_path="todolist.db"):
        self.db_path = db_path
        self._ensure_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self):
        try:
            with self._get_connection() as con:
                cur = con.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS todo(
                        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        title TEXT NOT NULL,
                        state BOOLEAN DEFAULT false
                    )
                """)
        except Exception as ex:
            print(f"Error creating todo table: {ex}")

    def get_all(self):
        try:
            with self._get_connection() as con:
                cur = con.cursor()
                cur.execute("SELECT ID, title, state FROM todo")
                return cur.fetchall()
        except Exception as ex:
            print(f"Error fetching todos: {ex}")
            return []

    def add(self, title):
        try:
            with self._get_connection() as con:
                cur = con.cursor()
                cur.execute("INSERT INTO todo (title, state) VALUES (?, false)", (title,))
                con.commit()
        except Exception as ex:
            print(f"Error adding todo: {ex}")
            

    def delete(self, todo_id):
        try:
            with self._get_connection() as con:
                cur = con.cursor()
                cur.execute("DELETE FROM todo WHERE ID = ?", (todo_id,))
                con.commit()
        except Exception as ex:
            print(f"Error deleting todo: {ex}")
