from contextlib import contextmanager
from mysql.connector import Error, pooling

from db.config import (
    host,
    port,
    user,
    password,
    database,
    database_pool_size,
    database_pool_name,
)
from logger import get_logger

logger = get_logger(__file__)


#pool creation (once, at import time)
def create_db_pool():
    try:
        return pooling.MySQLConnectionPool(
            pool_name=database_pool_name,
            pool_size=database_pool_size,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
    except Error as e:
        logger.error("error creating db pool: %s", e)
        raise


_POOL = create_db_pool()


class DatabaseConnection:
    def __init__(self, pool):
        self.pool = pool

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            logger.error("database error: %s", e)
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()

    @contextmanager
    def get_cursor(self, dictionary=False):
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=dictionary)
            try:
                yield cursor
            finally:
                cursor.close()


#singleton exposed to migrations & repos
database = DatabaseConnection(_POOL)