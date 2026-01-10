import os
from pathlib import Path
import mysql.connector
from db.config import (
    host,
    port,
    user,
    password,
    database
)
from logger import get_logger
logger = get_logger(__file__)

def run_migration():
    migrations_dir = Path(__file__).parent/"migrations"
    sql_file = migrations_dir / "001_input_output_table.sql"

    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )

    cursor = conn.cursor()

    try:
        with open(sql_file) as f:
            sql_statements = f.read()
            for statement in sql_statements.split(";"):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            logger.info(f"Completed migration: {sql_file.name}")
    except FileNotFoundError as e:
        logger.error("file not found: %s", e)
        raise
    except Exception as e:
        logger.error("migration error: %s", e)
        raise

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    run_migration()