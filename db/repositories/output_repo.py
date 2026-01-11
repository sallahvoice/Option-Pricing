from typing import Dict, List

from db.engine import database
from db.repositories.base_repo import BaseRepository


class OutputRepository(BaseRepository):
    def __init__(self):
        super().__init__("BlackScholesOutputs", pk_column="CalculationOutputId")

    def create_outputs_batch(self, calculation_id: int, rows: List[Dict]):
        columns = ", ".join(rows[0].keys())
        placeholders = ", ".join(["%s"] * len(rows[0]))

        query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        values = [tuple(row.values()) for row in rows]

        with database.get_cursor() as cursor:
            cursor.executemany(query, values)
            return cursor.rowcount

    def get_one_row_by_input(self, calculation_output_id: int):
        query = f"SELECT * FROM {self.table} WHERE CalculationOutputId = %s"

        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (calculation_output_id,))
            return cursor.fetchone()

    def get_outputs_by_input(self, calculation_id: int):
        query = f"SELECT * FROM {self.table} WHERE CalculationId = %s"

        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (calculation_id,))
            return cursor.fetchall()

    def get_outputs_by_scenario(
        self, calculation_id: int, vol_shock: float, stock_shock: float
    ):
        query = (f"SELECT * FROM {self.table}" 
        "WHERE CalculationId = %s"
        "AND VolatilityShock = %s"
        "AND StockPriceShock = %s"
        )

        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (calculation_id, vol_shock, stock_shock))
            return cursor.fetchall()

    def get_call_or_put_outputs(self, calculation_id: int, is_call: int):
        query = f"SELECT * FROM {self.table} WHERE CalculationId = %s AND IsCall = %s"

        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (calculation_id, is_call))
            return cursor.fetchall()

    def delete_outputs_by_input(self, calculation_id: int):
        query = f"DELETE FROM {self.table} WHERE CalculationId = %s"

        with database.get_cursor() as cursor:
            cursor.execute(query, (calculation_id,))
            return cursor.rowcount


# delete_outputs_by_scenario(calculation_id: int, vol_shock: float, stock_shock: float)
#(min, max, avg, count of outputs given a calc id)
# aggregate_option_prices_by_input(calculation_id: int)
