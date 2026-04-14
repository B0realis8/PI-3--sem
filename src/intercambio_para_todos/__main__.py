import os
import pandas as pd
import psycopg2 as pg
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()
db_name = os.getenv("DB_NAME")
username = os.getenv("USER")
_port = os.getenv("PORT")
pswrd = os.getenv("PASSWORD")
db_host = os.getenv("DB_HOST")

print(db_name)

conn = pg.connect(host=db_host,
                       dbname=db_name,
                       user=username,
                       password=pswrd,
                       port=_port) 

cur = conn.cursor()

query = sql.SQL("SELECT * FROM {}").format(sql.Identifier("instagram"))
cur.execute(query)