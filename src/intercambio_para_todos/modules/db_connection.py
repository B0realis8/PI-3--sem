import os
import pandas as pd
import psycopg2 as pg
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def db_connection():

    db_config = {
    'db_name': os.getenv("DB_NAME"),
    'username': os.getenv("USER"),
    '_port': os.getenv("PORT"),
    'pswrd': os.getenv("PASSWORD"),
    'db_host': os.getenv("DB_HOST")
    }

    print(db_config['db_name'])
    
    try:
        conn = pg.connect(host=db_config['db_host'],
                       dbname=db_config['db_name'],
                       user=db_config['username'],
                       password=db_config['pswrd'],
                       port=db_config['_port']) 
        print("Conexão bem-sucedida!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def get_data_from_db():

    conn= db_connection()
    if conn:
        cur = conn.cursor()
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier("instagram"))
        cur.execute(query)
        posts = cur.fetchall()
        cur.connection.close()
        return posts
    else:
        return []


def get_produtos():
    conn = db_connection()
    if conn:
        cur = conn.cursor()
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier("produto"))
        cur.execute(query)
        produtos = cur.fetchall()
        conn.close()
        return produtos
    else:
        return []

def update_instagram_table():
    conn = db_connection()
    if conn:
        cur = conn.cursor()
        with open('./databases/Instagram Analytics.csv', 'r') as f:
            next(f)
            cur.copy_from(f, 'instagram', sep=',', columns=["account_id","account_type","follower_count","media_type","content_category","traffic_source","has_call_to_action","post_datetime","post_date","post_hour","day_of_week","likes","comments","shares","saves","reach","impression","engagement_rate","followers_gained","caption_length","hashtags_count","performance_bucket_label"])
            conn.commit()
            conn.close()
    else:
        print("Não foi possível conectar ao banco de dados para atualizar a tabela Instagram.")
