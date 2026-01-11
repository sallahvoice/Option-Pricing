from typing import Dict

from db.engine import database
from db.repositories.base_repo import BaseRepository


class InputRepository(BaseRepository):
    def __init__(self):
        super().__init__("BlackScholesInputs", pk_column="CalculationId")

    def create_input(self, inputs: Dict[str, float]):
        columns = ", ".join(inputs.keys())
        placeholders = ", ".join(["%s"] * len(inputs))
        query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"

        with database.get_cursor() as cursor:
            cursor.execute(query, tuple(inputs.values()))
            return cursor.lastrowid

    def list_recent_inputs(self, limit: int = 5):
        query = f"SELECT * FROM {self.table} ORDER BY created_at DESC LIMIT %s"

        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (limit,))
            return cursor.fetchall()

    def find_inputs_by_time_to_expiry(self, time_to_expiry):
        query = f"SELECT * FROM {self.table} WHERE TimeToExpiry = %s"

        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (time_to_expiry,))
            return cursor.fetchall()

    def find_inputs_by_vol_range(self, upper_vol, lower_vol):
        query = f"SELECT * FROM {self.table} WHERE Volatility BETWEEN %s AND %s"

        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (lower_vol, upper_vol))
            return cursor.fetchall()
