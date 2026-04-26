import os
import pandas as pd
import psycopg2 as pg
import psycopg2.extras
from psycopg2 import sql
from dotenv import load_dotenv
from urllib.parse import urlparse
import asyncio

load_dotenv()

def db_connection():

    db_uri = os.getenv("DB_URI")

    connection = urlparse(db_uri)

    connection_params = {
        'dbname': connection.path[1:],
        'user': connection.username,
        'password': connection.password,
        'host': connection.hostname,
        'port': connection.port
    }

    try:
        conn = pg.connect(**connection_params)
        print("Conexão bem-sucedida!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def get_data_from_db():

    conn= db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.DictCursor)
        query = sql.SQL("SELECT * FROM {} LIMIT 20").format(sql.Identifier("instagram"))
        cur.execute(query)
        rows = cur.fetchall()
        posts = []
        for row in rows:
            posts.append(dict(row))
        print(type(posts))
        cur.connection.close()
        return posts
    else:
        return []


def get_produtos():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier("produto"))
        cur.execute(query)
        produtos = cur.fetchall()
        conn.close()
        return produtos
    else:
        return []

async def update_instagram_table():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        with open('./databases/Instagram Analytics.csv', 'r') as f:
            next(f)
            cur.copy_from(f, 'instagram', sep=',', columns=["account_id","account_type","follower_count","media_type","content_category","traffic_source","has_call_to_action","post_datetime","post_date","post_hour","day_of_week","likes","comments","shares","saves","reach","impression","engagement_rate","followers_gained","caption_length","hashtags_count","performance_bucket_label"])
            conn.commit()
            conn.close()
    else:
        print("Não foi possível conectar ao banco de dados para atualizar a tabela Instagram.")

async def add_user(account_id, account_type, follower_count, media_type, content_category, traffic_source, has_call_to_action, post_datetime, post_date, post_hour, day_of_week, likes, comments, shares, saves, reach, impression, engagement_rate, followers_gained, caption_length, hashtags_count, performance_bucket_label   ):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO instagram (account_id, account_type, follower_count, media_type, content_category, traffic_source, has_call_to_action, post_datetime, post_date, post_hour, day_of_week, likes, comments, shares, saves, reach, impression, engagement_rate, followers_gained, caption_length, hashtags_count, performance_bucket_label) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s， %s， %s， %s， %s， %s， %s， %s， %s， %s， %s， %s)", 
                (account_id, account_type, follower_count, media_type, content_category, traffic_source, has_call_to_action, post_datetime, post_date,
                 post_hour,
                 day_of_week,
                 likes,
                 comments,
                 shares,
                 saves,
                 reach,
                 impression,
                 engagement_rate,
                 followers_gained,
                 caption_length,
                 hashtags_count,
                 performance_bucket_label))
    conn.commit()
    conn.close()


def add_produto(nome, tipo, valor_minimo, pais, cidade):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO produto (nome_produto, tipo, valor_minimo, pais, cidade) VALUES (%s, %s, %s, %s, %s)", (nome, tipo, valor_minimo, pais, cidade))
    conn.commit()
    conn.close()

def update_produto(row_data):

    conn = db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE produto SET nome_produto = %s, tipo = %s, valor_minimo = %s, pais = %s, cidade = %s WHERE id_produto = %s",
        (row_data["nome_produto"], row_data["tipo"], row_data["valor_minimo"], row_data["pais"], row_data["cidade"], row_data["id_produto"])
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Updated: {row_data}")

def delete_produto(id_produto):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))
    conn.commit()
    cur.close()
    conn.close()