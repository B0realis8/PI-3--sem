import os
from nicegui.ui import notify
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

def update_produto(nome, tipo, valor_minimo, pais, cidade, id_produto):

    conn = db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE produto SET nome_produto = %s, tipo = %s, valor_minimo = %s, pais = %s, cidade = %s WHERE id_produto = %s",
        (nome, tipo, valor_minimo, pais, cidade, id_produto)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Updated: {id_produto}")

def delete_produto(id_produto):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))
    conn.commit()
    cur.close()
    conn.close()

# ── Orçamento Functions ─────────────────────────────────────────────

def get_orcamentos():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT o.id_orcamento, p.id_produto, o.id_cliente, h.id_hospedagem,h.endereco, h.diaria, h.dias, h.obs, \
                        o.valor_total, p.nome_produto, p.tipo, p.valor_minimo, p.pais, p.cidade, \
                        json_agg(voo.*) FILTER (WHERE ida_volta = 'Ida') AS voo_lista_ida ,\
                        json_agg(voo.*) FILTER (WHERE ida_volta = 'Volta') AS voo_lista_volta, \
                        sum(voo.valor_passagem) FILTER (WHERE ida_volta = 'Ida') AS valor_passagem_ida, \
                        sum(voo.qtd_passagens) FILTER (WHERE ida_volta = 'Ida') AS qtd_passagens_ida, \
                        string_agg(voo.obs,'') FILTER (WHERE ida_volta = 'Ida') AS obs_ida, \
                        sum(voo.valor_passagem) FILTER (WHERE ida_volta = 'Volta') AS valor_passagem_volta, \
                        sum(voo.qtd_passagens) FILTER (WHERE ida_volta = 'Volta') AS qtd_passagens_volta, \
                        string_agg(voo.obs,'') FILTER (WHERE ida_volta = 'Volta') AS obs_volta,  \
                        (SELECT nome_companhia FROM (SELECT comp.nome_companhia, o.id_orcamento,voo.ida_volta FROM companhia_aerea comp LEFT JOIN voo ON comp.id_companhia = voo.id_companhia INNER JOIN orcamento o ON voo.id_orcamento = o.id_orcamento) AS companhia_ida WHERE ida_volta = 'Ida' AND id_orcamento = o.id_orcamento), \
                        (SELECT nome_companhia FROM (SELECT comp.nome_companhia, o.id_orcamento,voo.ida_volta FROM companhia_aerea comp LEFT JOIN voo ON comp.id_companhia = voo.id_companhia INNER JOIN orcamento o ON voo.id_orcamento = o.id_orcamento) AS companhia_volta WHERE ida_volta = 'Volta' AND id_orcamento = o.id_orcamento), \
                        s.id_servico, s.descricao, s.obs_servicos AS obs_servico, \
                        c.nome \
                        FROM {} o \
                        LEFT JOIN {} p ON p.id_produto = o.id_produto \
                        LEFT JOIN {} c ON o.id_cliente = c.id_cliente \
                        LEFT JOIN {} h ON o.id_hospedagem = h.id_hospedagem \
                        LEFT JOIN {} s ON o.id_servico = s.id_servico \
                        LEFT JOIN {} voo ON o.id_orcamento = voo.id_orcamento \
                        LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia \
                        GROUP BY o.id_orcamento, p.id_produto, o.id_cliente, o.valor_total, p.nome_produto, p.tipo, p.valor_minimo, p.pais, p.cidade, c.nome, h.id_hospedagem,h.endereco, h.diaria, h.dias, h.obs, s.id_servico, s.descricao, s.obs_servicos").format(
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
        return orcamentos
    else:
        return []

def get_voos():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier("voo"))
        cur.execute(query)
        voos = cur.fetchall()
        conn.close()
        return voos
    else:
        return []
    
def get_voos_w_id(id):
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT * FROM {} WHERE id_voo = %s").format(sql.Identifier("voo"))
        cur.execute(query, (id,))
        voos = cur.fetchall()
        conn.close()
        return voos
    else:
        return []

def get_clientes():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier("cliente"))
        cur.execute(query)
        clientes = cur.fetchall()
        conn.close()
        return clientes
    else:
        return []
    
def add_cliente(nome, sexo, data_nascimento, cpf, telefone, adicionar_cliente, id_input_cliente):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO cliente (nome, sexo, data_nascimento, cpf, telefone) VALUES (%s, %s, %s, %s, %s) RETURNING id_cliente", (nome, sexo, data_nascimento, cpf, telefone))
    id_cliente = cur.fetchone()[0]
    conn.commit()
    conn.close()
    notify(f"Cliente adicionado com ID: {id_cliente}", type='success', title='Sucesso')
    adicionar_cliente.close()
    id_input_cliente.options = {c['id_cliente']: c['nome'] for c in get_clientes()} if get_clientes() else {}
    id_input_cliente.value = id_cliente


def add_orcamento(id_produto,
                  id_cliente,
                  pais_saida_ida,
                  cidade_saida_ida,
                  aeroporto_saida_ida,
                  dt_hr_saida_ida,
                  pais_destino_ida,
                  cidade_destino_ida,
                  aeroporto_destino_ida,
                  dt_hr_chegada_ida,
                  valor_passagem_ida,
                  qtd_passagens_ida,
                  id_companhia_ida,
                  obs_ida,
                  pais_saida_volta,
                  cidade_saida_volta,
                  aeroporto_saida_volta,
                  dt_hr_saida_volta,
                  pais_destino_volta,
                  cidade_destino_volta,
                  aeroporto_destino_volta,
                  dt_hr_chegada_volta,
                  valor_passagem_volta,
                  qtd_passagens_volta,
                  id_companhia_volta,
                  obs_volta,

                  endereco_hospedagem,
                  diaria,
                  qtd_dias,
                  obs_hospedagem,

                  descricao_servico,
                  valor_total_servicos,
                  obs_servicos,

                  valor_total

                  ):
    
    conn = db_connection()
    cur = conn.cursor()

    

    cur.execute("INSERT INTO hospedagem (endereco, diaria, dias, obs) VALUES (%s, %s, %s, %s) RETURNING id_hospedagem", (endereco_hospedagem, diaria, qtd_dias, obs_hospedagem))
    id_hospedagem = cur.fetchone()[0]

    cur.execute("INSERT INTO servico (descricao, valor_total_servicos, obs_servicos) VALUES (%s, %s, %s) RETURNING id_servico", (descricao_servico, valor_total_servicos, obs_servicos))
    id_servico = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO orcamento (id_produto, id_cliente, id_hospedagem, id_servico, valor_total) VALUES (%s, %s, %s, %s, %s) RETURNING id_orcamento",
        (id_produto, id_cliente, id_hospedagem, id_servico, valor_total)
    )

    id_orcamento = cur.fetchone()[0]

    cur.execute("INSERT INTO voo (pais_saida, cidade_saida, aeroporto_saida, dt_hr_saida, pais_destino, cidade_destino, aeroporto_destino, dt_hr_chegada, valor_passagem,qtd_passagens, id_companhia, obs, id_orcamento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (pais_saida_ida, cidade_saida_ida, aeroporto_saida_ida, dt_hr_saida_ida, pais_destino_ida, cidade_destino_ida, aeroporto_destino_ida, dt_hr_chegada_ida, valor_passagem_ida, qtd_passagens_ida, id_companhia_ida, obs_ida, id_orcamento))

    cur.execute("INSERT INTO voo (pais_saida, cidade_saida, aeroporto_saida, dt_hr_saida, pais_destino, cidade_destino, aeroporto_destino, dt_hr_chegada, valor_passagem,qtd_passagens, id_companhia, obs, id_orcamento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (pais_saida_volta, cidade_saida_volta, aeroporto_saida_volta, dt_hr_saida_volta, pais_destino_volta, cidade_destino_volta, aeroporto_destino_volta, dt_hr_chegada_volta, valor_passagem_volta, qtd_passagens_volta, id_companhia_volta, obs_volta, id_orcamento))

    conn.commit()
    conn.close()

def update_orcamento(id_produto, pais_saida, cidade_saida, aeroporto_saida, dt_hr_saida, pais_destino, cidade_destino, aeroporto_destino, dt_hr_chegada, valor_passagem, qtd_passagens, id_companhia, id_cliente, valor_total, id_orcamento, id_voo, obs):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE voo SET pais_saida = %s, cidade_saida = %s, aeroporto_saida = %s, dt_hr_saida = %s, pais_destino = %s, cidade_destino = %s, aeroporto_destino = %s, dt_hr_chegada = %s, valor_passagem = %s, qtd_passagens = %s, id_companhia = %s, obs = %s WHERE id_voo = %s", (pais_saida, cidade_saida, aeroporto_saida, dt_hr_saida, pais_destino, cidade_destino, aeroporto_destino, dt_hr_chegada, valor_passagem, qtd_passagens, id_companhia, obs, id_voo))
    cur.execute(
        "UPDATE orcamento SET id_produto = %s, id_cliente = %s, valor_total = %s WHERE id_orcamento = %s",
        (id_produto, id_cliente, valor_total, id_orcamento)
    )
    conn.commit()
    cur.close()
    conn.close()

def delete_orcamento(id_orcamento):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM orcamento WHERE id_orcamento = %s", (id_orcamento,))
    conn.commit()
    cur.close()
    conn.close()


def get_companhias():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier("companhia_aerea"))
        cur.execute(query)
        companhias = cur.fetchall()
        conn.close()
        return companhias
    else:
        return []
    

# Vendas ---------------

def get_vendas():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier("vendas"))
        cur.execute(query)
        vendas = cur.fetchall()
        conn.close()
        return vendas
    else:
        return []

def update_venda(data_venda, id_orcamento, quantidade, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao, lucro_total, id_venda):

    conn = db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE vendas SET data_venda = %s, id_orcamento = %s, quantidade = %s, forma_pgto = %s, valor_final = %s, entrada = %s, n_parcelas = %s, valor_parcelas = %s, comissao = %s, lucro_total = %s WHERE id_venda = %s",
        (data_venda, id_orcamento, quantidade, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao, lucro_total, id_venda)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Updated: {id_venda}")

def get_orcamento_vendas():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT * FROM {} \
                        LEFT JOIN {} USING (id_produto)\
                        LEFT JOIN {} USING (id_voo)\
                        LEFT JOIN {} USING (id_companhia)\
                        LEFT JOIN {} USING (id_cliente)")\
        .format(sql.Identifier("orcamento"), sql.Identifier("produto"), sql.Identifier("voo"), sql.Identifier("companhia_aerea"), sql.Identifier("cliente"))
        cur.execute(query)
        orcamentos_venda = cur.fetchall()
        conn.close()
        return orcamentos_venda
    else:
        return []