import os
from nicegui.ui import notify
import pandas as pd
import psycopg2 as pg
import psycopg2.extras
from psycopg2 import sql
from dotenv import load_dotenv
from urllib.parse import urlparse
import asyncio
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(script_dir, '..', 'src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

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




import intercambio_para_todos.modules as con


# def teste_import_instagram():
#     cur = conn.cursor()

#     cur.execute("DROP TABLE IF EXISTS instagram CASCADE")
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS instagram (
#             post_id SERIAL PRIMARY KEY,
#             account_id INT,
#             account_type VARCHAR(20),
#             follower_count INT,
#             media_type VARCHAR(20),
#             content_category VARCHAR(30),
#             traffic_source VARCHAR(30),
#             has_call_to_action BOOLEAN,
#             post_datetime TIMESTAMP,
#             post_date DATE,
#             post_hour INT,
#             day_of_week VARCHAR(20),
#             likes INT,
#             comments INT,
#             shares INT,
#             saves INT,
#             reach INT,
#             impression INT,
#             engagement_rate NUMERIC,
#             followers_gained INT,
#             caption_length INT,
#             hashtags_count INT,
#             performance_bucket_label VARCHAR(10)
#         )
#     """)

#     with open('databases/output-onlinetools.csv', 'r') as f:
#         next(f)
#         cur.copy_from(f, 'instagram', sep=',', columns=["account_id","account_type","follower_count","media_type","content_category","traffic_source","has_call_to_action","post_datetime","post_date","post_hour","day_of_week","likes","comments","shares","saves","reach","impression","engagement_rate","followers_gained","caption_length","hashtags_count","performance_bucket_label"])

#     conn.commit()
#     conn.close()


#     analytics_data = pd.read_csv('databases/output-onlinetools.csv')
#     print(analytics_data.head())
#     print(analytics_data.shape)

# def update_instagram_table():
#     conn = db_connection()
#     if not conn:
#         return
#     cur = conn.cursor()
#     with open('databases/output-onlinetools.csv', 'r') as f:
#         next(f)
#         cur.copy_from(f, 'instagram', sep=',', columns=["account_id","account_type","follower_count","media_type","content_category","traffic_source","has_call_to_action","post_datetime","post_date","post_hour","day_of_week","likes","comments","shares","saves","reach","impression","engagement_rate","followers_gained","caption_length","hashtags_count","performance_bucket_label"])
#         conn.commit()
#         conn.close()



def teste_import_orcamento():
        
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT o.*, p.*, c.*, h.*, s.*, \
                        json_agg(voo.*) FILTER (WHERE ida_volta = 'Ida') AS voo_lista_ida ,\
                        json_agg(voo.*) FILTER (WHERE ida_volta = 'Volta') AS voo_lista_volta \
                        FROM {} o \
                        LEFT JOIN {} p ON p.id_produto = o.id_produto \
                        LEFT JOIN {} c ON o.id_cliente = c.id_cliente \
                        LEFT JOIN {} h ON o.id_hospedagem = h.id_hospedagem \
                        LEFT JOIN {} s ON o.id_servico = s.id_servico \
                        LEFT JOIN {} voo ON o.id_orcamento = voo.id_orcamento \
                        LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia \
                        LEFT JOIN vendas v ON o.id_orcamento = v.id_orcamento \
                        GROUP BY o.id_orcamento, p.id_produto, o.id_cliente, o.valor_total, p.nome_produto, p.tipo, p.valor_minimo, p.pais, p.cidade, c.nome, h.id_hospedagem,h.endereco, h.diaria, h.dias, h.obs, s.id_servico, s.descricao, s.obs_servicos, s.valor_total_servicos, c.id_cliente, v.id_venda").format(
            sql.Identifier("orcamento"),
            sql.Identifier("produto"),
            sql.Identifier("cliente"),
            sql.Identifier("hospedagem"),
            sql.Identifier("servico"),
            sql.Identifier("voo"),
            sql.Identifier("servico"),
        )
        cur.execute(query)
        orcamentos = cur.fetchall()
        conn.close()
        data = pd.DataFrame(orcamentos)

        columns_ida = pd.json_normalize(data['voo_lista_ida'].explode()).add_suffix('ida_')
        columns_volta = pd.json_normalize(data['voo_lista_volta'].explode()).add_suffix('_volta')
        data = data.join(columns_ida).join(columns_volta).drop(columns=['voo_lista_ida', 'voo_lista_volta'])
        print(data.head())
        data.to_csv('orcamentos_completo.csv', index=False)
        print(data.to_dict(orient='records'))
        print(orcamentos)
        return data.to_dict(orient='records')
    else:
        return []
    
teste_import_orcamento()