from db.engine import database


class BaseRepository:
    def __init__(self, table_name: str, pk_column: str):
        self.table = table_name
        self.pk = pk_column

    def create(self, data: dict) -> int:
        if not data:
            raise ValueError("no data provided")

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"

        with database.get_cursor() as cursor:
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid

    def find_by_id(self, pk_value):
        query = f"SELECT * FROM {self.table} WHERE {self.pk} = %s"

        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (pk_value,))
            return cursor.fetchone()

    def find_all(self, limit=50):
        query = f"SELECT * FROM {self.table} LIMIT %s"

        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (limit,))
            return cursor.fetchall()

    def update(self, pk_value, data: dict) -> int:
        if not data:
            return 0

        set_clause = ", ".join(f"{k} = %s" for k in data)
        query = f"UPDATE {self.table} SET {set_clause} WHERE {self.pk} = %s"
        values = tuple(data.values()) + (pk_value,)

        with database.get_cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount

    def delete_by_id(self, pk_value) -> bool:
        query = f"DELETE FROM {self.table} WHERE {self.pk} = %s"

        with database.get_cursor() as cursor:
            cursor.execute(query, (pk_value,))
            return cursor.rowcount > 0