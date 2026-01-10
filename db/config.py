import os
from dotenv import load_dotenv

load_dotenv()
#default values
host = os.getenv("DB_HOST")
port = int(os.getenv("DB_PORT", "3306"))
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")
database_pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
database_pool_name = os.getenv("DB_POOL_NAME")