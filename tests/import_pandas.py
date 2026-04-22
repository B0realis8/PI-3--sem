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

conn = pg.connect(host=db_host,
                       dbname=db_name,
                       user=username,
                       password=pswrd,
                       port=_port) 
cur = conn.cursor()

sql = "DROP TABLE IF EXISTS instagram CASCADE; CREATE TABLE IF NOT EXISTS instagram (post_id SERIAL PRIMARY KEY,account_id INT account_type VARCHAR(20),follower_count INT,media_type VARCHAR(20),content_category VARCHAR(30),traffic_source VARCHAR(30),has_call_to_action BOOLEAN,post_datetime TIMESTAMP,post_date DATE,post_hour INT,day_of_week VARCHAR(20),likes INT,comments INT,shares INT,saves INT,reach INT,impression INT,engagement_rate NUMERIC,followers_gained INT,caption_length INT,hashtags_count INT,performance_bucket_label VARCHAR(10))"

with open('databases/output-onlinetools.csv', 'r') as f:
    next(f)
    cur.copy_from(f, 'instagram', sep=',', columns=["account_id","account_type","follower_count","media_type","content_category","traffic_source","has_call_to_action","post_datetime","post_date","post_hour","day_of_week","likes","comments","shares","saves","reach","impression","engagement_rate","followers_gained","caption_length","hashtags_count","performance_bucket_label"])
    conn.commit()
    conn.close()


analytics_data = pd.read_csv('databases/output-onlinetools.csv')
print(analytics_data.head())
print(analytics_data.shape)

def update_instagram_table():
    conn = pg.connect(host=db_host,
                       dbname=db_name,
                       user=username,
                       password=pswrd,
                       port=_port) 
    cur = conn.cursor()
    with open('databases/output-onlinetools.csv', 'r') as f:
        next(f)
        cur.copy_from(f, 'instagram', sep=',', columns=["account_id","account_type","follower_count","media_type","content_category","traffic_source","has_call_to_action","post_datetime","post_date","post_hour","day_of_week","likes","comments","shares","saves","reach","impression","engagement_rate","followers_gained","caption_length","hashtags_count","performance_bucket_label"])
        conn.commit()
        conn.close()

