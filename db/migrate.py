import os
from pathlib import Path
import mysql.connector
from db.config import host, port, user, password, database

def run_migration():
    migrations_dir = Path(__file__).parent/"migrations"

    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )

    cursor = conn.cursor()

    for sql_file in sorted(migrations_dir.glob("*.sql")):
        with open(sql_file) as f:
            sql_statements = f.read()
            for result in cursor.execute(sql_statements, multi=True):
                if result.with_rows:
                    cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()


if __name__ = "__main__":
    run_migration()