import os
from pathlib import Path
import mysql.connector

load_dotenv()

def run_migration():
    migrations_dir = Path(__file__).parent/"migrations"

    conn = mysql.connector.connect(
        host=os.getenv("DB-HOST")
        port=int(os.getenv("DB-PORT"), 3306),
        user=os.getenv("DB-USER"),
        password=os.getenv("DB-PASSWORD"),
        database=os.getenv("DB-NAME")
    )

    cursor = conn.cursor()

    for sql_file in sorted(migrations_dir.glob("*.sql")):
        with open(sql_file) as f:
            sql_statements = f.read()
            for result in cursor.excute(sql_statements, multi=true):
                if result.with_rows:
                    cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()


if __name__ = "__main__":
    run_migration()