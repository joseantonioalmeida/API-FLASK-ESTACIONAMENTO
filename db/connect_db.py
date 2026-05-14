import pymysql
import os
from dotenv import load_dotenv


load_dotenv()

def connect_db():
    db_host = os.getenv('db_host', 'change-me')
    db_user = os.getenv('db_user', 'change-me')
    db_password = os.getenv('db_password', 'change-me')
    db_name = os.getenv('db_name', 'change-me')

    db = pymysql.connect(host=db_host, user=db_user, passwd=db_password, database=db_name)
    return db 