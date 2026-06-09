# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from nicegui.ui import notify
import pandas as pd
import psycopg2 as pg
import psycopg2.extras
from psycopg2 import sql
from dotenv import load_dotenv
from urllib.parse import urlparse
import asyncio
from sqlalchemy import create_engine, text
import aiopg

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env from this package root so DW_RUI and DB_URI are available
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

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
        conn = pg.connect(**connection_params, options="-c client_encoding=UTF8")
        conn.set_client_encoding('UTF8')
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
        try:
            with conn.cursor(name='produtos_cursor', cursor_factory=pg.extras.RealDictCursor) as cur:
                query = sql.SQL(
                    "SELECT p.*, paises.pais AS nome_pais, c.cidade AS nome_cidade "
                    "FROM {} p LEFT JOIN cidades c ON p.cidade = c.id "
                    "LEFT JOIN paises ON c.id_pais = paises.id"
                ).format(sql.Identifier("produto"))

                cur.itersize = 100
                cur.execute(query)

                return list(cur)  # avoids generator serialization issue

        finally:
            conn.close()
    else:
        return []


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

# def get_orcamentos():
#     conn = db_connection()
#     if conn:
#         cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
#         query = sql.SQL("SELECT o.id_orcamento, p.id_produto, o.id_cliente, h.id_hospedagem,h.endereco, h.diaria, h.dias, h.obs, \
#                         o.valor_total, p.nome_produto, p.tipo, p.valor_minimo, p.pais, p.cidade, \
#                         json_agg(voo.*) FILTER (WHERE ida_volta = 'Ida') AS voo_lista_ida ,\
#                         json_agg(voo.*) FILTER (WHERE ida_volta = 'Volta') AS voo_lista_volta, \
#                         sum(voo.valor_passagem) FILTER (WHERE ida_volta = 'Ida') AS valor_passagem_ida, \
#                         sum(voo.qtd_passagens) FILTER (WHERE ida_volta = 'Ida') AS qtd_passagens_ida, \
#                         string_agg(voo.obs,'') FILTER (WHERE ida_volta = 'Ida') AS obs_ida, \
#                         sum(voo.valor_passagem) FILTER (WHERE ida_volta = 'Volta') AS valor_passagem_volta, \
#                         sum(voo.qtd_passagens) FILTER (WHERE ida_volta = 'Volta') AS qtd_passagens_volta, \
#                         string_agg(voo.obs,'') FILTER (WHERE ida_volta = 'Volta') AS obs_volta,  \
#                         (SELECT nome_companhia FROM (SELECT comp.nome_companhia, o.id_orcamento,voo.ida_volta FROM companhia_aerea comp LEFT JOIN voo ON comp.id_companhia = voo.id_companhia INNER JOIN orcamento o ON voo.id_orcamento = o.id_orcamento) AS companhia_ida WHERE ida_volta = 'Ida' AND id_orcamento = o.id_orcamento) AS companhia_ida, \
#                         (SELECT nome_companhia FROM (SELECT comp.nome_companhia, o.id_orcamento,voo.ida_volta FROM companhia_aerea comp LEFT JOIN voo ON comp.id_companhia = voo.id_companhia INNER JOIN orcamento o ON voo.id_orcamento = o.id_orcamento) AS companhia_volta WHERE ida_volta = 'Volta' AND id_orcamento = o.id_orcamento), \
#                         s.id_servico, s.descricao, s.obs_servicos, s.valor_total_servicos, \
#                         c.nome \
#                         FROM {} o \
#                         LEFT JOIN {} p ON p.id_produto = o.id_produto \
#                         LEFT JOIN {} c ON o.id_cliente = c.id_cliente \
#                         LEFT JOIN {} h ON o.id_hospedagem = h.id_hospedagem \
#                         LEFT JOIN {} s ON o.id_servico = s.id_servico \
#                         LEFT JOIN {} voo ON o.id_orcamento = voo.id_orcamento \
#                         LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia \
#                         GROUP BY o.id_orcamento, p.id_produto, o.id_cliente, o.valor_total, p.nome_produto, p.tipo, p.valor_minimo, p.pais, p.cidade, c.nome, h.id_hospedagem,h.endereco, h.diaria, h.dias, h.obs, s.id_servico, s.descricao, s.obs_servicos, s.valor_total_servicos").format(
#             sql.Identifier("orcamento"),
#             sql.Identifier("produto"),
#             sql.Identifier("cliente"),
#             sql.Identifier("hospedagem"),
#             sql.Identifier("servico"),
#             sql.Identifier("voo"),
#             sql.Identifier("servico"),
#         )
#         cur.execute(query)
#         orcamentos = cur.fetchall()
#         conn.close()
#         return orcamentos
#     else:
#         return []

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
        query = sql.SQL("SELECT {}.*, ci_saida.cidade AS cidade_saida_nome, ci_destino.cidade AS cidade_destino_nome, pais_saida.pais AS pais_saida_nome, pais_destino.pais AS pais_destino_nome FROM {}\
		                    LEFT JOIN cidades ci_saida ON voo.cidade_saida = ci_saida.id\
                            LEFT JOIN cidades ci_destino ON voo.cidade_destino = ci_destino.id\
                            LEFT JOIN paises pais_saida ON pais_saida.id = ci_saida.id_pais\
                            LEFT JOIN paises pais_destino ON pais_destino.id = ci_destino.id_pais\
                            WHERE voo.id_orcamento = %s").format(sql.Identifier("voo"), sql.Identifier("voo"))
        cur.execute(query, (id,))
        voos = cur.fetchall()
        conn.close()
        return voos
    else:
        return []

def get_clientes():
    conn = db_connection()
    if conn:
        try:
            with conn.cursor(name='clientes_cursor', cursor_factory=pg.extras.RealDictCursor) as cur:
                query = sql.SQL(
                    "SELECT cliente.*, cidades.cidade AS nome_cidade "
                    "FROM {} LEFT JOIN cidades ON cliente.cidade = cidades.id"
                ).format(sql.Identifier("cliente"))
                
                cur.itersize = 100  # rows fetched per network roundtrip
                cur.execute(query)
                
                for row in cur:
                    yield row  # process one row at a time
                    
        finally:
            conn.close()

def delete_cliente(id_cliente):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
    conn.commit()
    
def add_cliente(nome, sexo, data_nascimento, cpf, telefone, cidade, estado, adicionar_cliente, id_input_cliente=None):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO cliente (nome, sexo, data_nascimento, cpf, telefone, cidade, estado) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_cliente", (nome, sexo, data_nascimento, cpf, telefone, cidade, estado))
    id_cliente = cur.fetchone()[0]
    conn.commit()
    conn.close()
    notify(f"Cliente adicionado com ID: {id_cliente}", type='success', title='Sucesso')
    adicionar_cliente.close()
    if id_input_cliente:
        id_input_cliente.options = {c['id_cliente']: c['nome'] for c in get_clientes()} if get_clientes() else {}
        id_input_cliente.value = id_cliente

def update_cliente(nome, sexo, data_nascimento, cpf, telefone, cidade, estado, id_cliente):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE cliente SET nome = %s, sexo = %s, data_nascimento = %s, cpf = %s, telefone = %s, cidade = %s, estado = %s WHERE id_cliente = %s", (nome, sexo, data_nascimento, cpf, telefone, cidade, estado, id_cliente))
    conn.commit()
    conn.close()



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

    cur.execute("INSERT INTO voo (pais_saida, cidade_saida, aeroporto_saida, dt_hr_saida, pais_destino, cidade_destino, aeroporto_destino, dt_hr_chegada, valor_passagem,qtd_passagens, id_companhia, obs, id_orcamento, ida_volta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (pais_saida_ida, cidade_saida_ida, aeroporto_saida_ida, dt_hr_saida_ida, pais_destino_ida, cidade_destino_ida, aeroporto_destino_ida, dt_hr_chegada_ida, valor_passagem_ida, qtd_passagens_ida, id_companhia_ida, obs_ida, id_orcamento, 'Ida'))

    cur.execute("INSERT INTO voo (pais_saida, cidade_saida, aeroporto_saida, dt_hr_saida, pais_destino, cidade_destino, aeroporto_destino, dt_hr_chegada, valor_passagem,qtd_passagens, id_companhia, obs, id_orcamento, ida_volta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (pais_saida_volta, cidade_saida_volta, aeroporto_saida_volta, dt_hr_saida_volta, pais_destino_volta, cidade_destino_volta, aeroporto_destino_volta, dt_hr_chegada_volta, valor_passagem_volta, qtd_passagens_volta, id_companhia_volta, obs_volta, id_orcamento, 'Volta'))

    conn.commit()
    conn.close()

def update_orcamento(id_produto,
                     id_cliente,
                     id_orcamento,

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

                     id_hospedagem,
                     endereco_hospedagem,
                     diaria,
                     qtd_dias,
                     obs_hospedagem,

                     id_servico,
                     descricao_servico,
                     valor_total_servicos,
                     obs_servicos,

                     valor_total):
    conn = db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE voo SET pais_saida = %s, cidade_saida = %s, aeroporto_saida = %s, dt_hr_saida = %s, pais_destino = %s, cidade_destino = %s, aeroporto_destino = %s, dt_hr_chegada = %s, valor_passagem = %s, qtd_passagens = %s, id_companhia = %s, obs = %s WHERE id_orcamento = %s AND ida_volta = 'Ida'", (pais_saida_ida, cidade_saida_ida, aeroporto_saida_ida, dt_hr_saida_ida, pais_destino_ida, cidade_destino_ida, aeroporto_destino_ida, dt_hr_chegada_ida, valor_passagem_ida, qtd_passagens_ida, id_companhia_ida, obs_ida, id_orcamento))

    cur.execute("UPDATE voo SET pais_saida = %s, cidade_saida = %s, aeroporto_saida = %s, dt_hr_saida = %s, pais_destino = %s, cidade_destino = %s, aeroporto_destino = %s, dt_hr_chegada = %s, valor_passagem = %s, qtd_passagens = %s, id_companhia = %s, obs = %s WHERE id_orcamento = %s AND ida_volta = 'Volta'", (pais_saida_volta, cidade_saida_volta, aeroporto_saida_volta, dt_hr_saida_volta, pais_destino_volta, cidade_destino_volta, aeroporto_destino_volta, dt_hr_chegada_volta, valor_passagem_volta, qtd_passagens_volta, id_companhia_volta, obs_volta, id_orcamento))

    cur.execute("UPDATE hospedagem SET endereco = %s, diaria = %s, dias = %s, obs = %s WHERE id_hospedagem = %s", (endereco_hospedagem, diaria, qtd_dias, obs_hospedagem, id_hospedagem))

    cur.execute("UPDATE servico SET descricao = %s, valor_total_servicos = %s, obs_servicos = %s WHERE id_servico = %s", (descricao_servico, valor_total_servicos, obs_servicos, id_servico))

    cur.execute(
        "UPDATE orcamento SET id_produto = %s, id_cliente = %s, valor_total = %s WHERE id_orcamento = %s",
        (id_produto, id_cliente, valor_total, id_orcamento)
    )


    conn.commit()
    cur.close()
    conn.close()

def delete_orcamento(id_orcamento, id_hospedagem, id_servico):
    conn = db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM voo WHERE id_orcamento = %s", (id_orcamento,))
    cur.execute("DELETE FROM orcamento WHERE id_orcamento = %s", (id_orcamento,))
    cur.execute("DELETE FROM hospedagem WHERE id_hospedagem = %s", (id_hospedagem,))
    cur.execute("DELETE FROM servico WHERE id_servico = %s", (id_servico,))
    
    conn.commit()
    cur.close()
    conn.close()


def get_companhias():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT companhia_aerea.*, paises.pais AS nome_pais, paises.id AS pais FROM {} LEFT JOIN paises ON companhia_aerea.pais = paises.id").format(sql.Identifier("companhia_aerea"))
        cur.execute(query)
        companhias = cur.fetchall()
        conn.close()
        return companhias
    else:
        return []

def delete_companhia(id_companhia):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM companhia_aerea WHERE id_companhia = %s", (id_companhia,))
    conn.commit()
    cur.close()
    conn.close()

def add_companhia(nome_companhia, pais):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO companhia_aerea (nome_companhia, pais) VALUES (%s, %s)", (nome_companhia, pais))
    conn.commit()
    conn.close()
    

# Vendas ---------------

def get_vendas():
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT v.*, c.*, o.* FROM {} v LEFT JOIN orcamento o ON v.id_orcamento = o.id_orcamento LEFT JOIN cliente c ON o.id_cliente = c.id_cliente").format(sql.Identifier("vendas"))
        cur.execute(query)
        vendas = cur.fetchall()
        conn.close()
        return vendas
    else:
        return []
    
def add_venda(data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO vendas (data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao))
    conn.commit()
    conn.close()
    update_dw()

def update_venda(data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao, id_venda, valor_total_gasto):

    conn = db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE vendas SET data_venda = %s, id_orcamento = %s, forma_pgto = %s, valor_final = %s, entrada = %s, n_parcelas = %s, valor_parcelas = %s, comissao = %s, valor_total_gasto = %s WHERE id_venda = %s",
        (data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao, valor_total_gasto, id_venda)
    )
    conn.commit()
    cur.close()

    update_dw()

    conn.close()

def update_status_venda(status_venda, id_venda):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE vendas SET status_venda = %s WHERE id_venda = %s",
        (status_venda, id_venda)
    )
    conn.commit()
    cur.close()
    conn.close()

def delete_venda(id_venda):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM vendas WHERE id_venda = %s", (id_venda,))
    conn.commit()
    cur.close()
    conn.close()
    update_dw()

# def get_orcamentos_vendas():
#     conn = db_connection()
#     if conn:
#         cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
#         query = sql.SQL("SELECT o.id_orcamento, p.id_produto, h.id_hospedagem,h.endereco, h.diaria, h.dias, h.obs, \
#                         o.valor_total, p.nome_produto, p.tipo, p.valor_minimo, p.pais, p.cidade, \
#                         json_agg(voo.*) FILTER (WHERE ida_volta = 'Ida') AS voo_lista_ida ,\
#                         json_agg(voo.*) FILTER (WHERE ida_volta = 'Volta') AS voo_lista_volta, \
#                         sum(voo.valor_passagem) FILTER (WHERE ida_volta = 'Ida') AS valor_passagem_ida, \
#                         sum(voo.qtd_passagens) FILTER (WHERE ida_volta = 'Ida') AS qtd_passagens_ida, \
#                         string_agg(voo.obs,'') FILTER (WHERE ida_volta = 'Ida') AS obs_ida, \
#                         sum(voo.valor_passagem) FILTER (WHERE ida_volta = 'Volta') AS valor_passagem_volta, \
#                         sum(voo.qtd_passagens) FILTER (WHERE ida_volta = 'Volta') AS qtd_passagens_volta, \
#                         string_agg(voo.obs,'') FILTER (WHERE ida_volta = 'Volta') AS obs_volta,  \
#                         (SELECT nome_companhia FROM (SELECT comp.nome_companhia, o.id_orcamento,voo.ida_volta FROM companhia_aerea comp LEFT JOIN voo ON comp.id_companhia = voo.id_companhia INNER JOIN orcamento o ON voo.id_orcamento = o.id_orcamento) AS companhia_ida WHERE ida_volta = 'Ida' AND id_orcamento = o.id_orcamento) AS companhia_ida, \
#                         (SELECT nome_companhia FROM (SELECT comp.nome_companhia, o.id_orcamento,voo.ida_volta FROM companhia_aerea comp LEFT JOIN voo ON comp.id_companhia = voo.id_companhia INNER JOIN orcamento o ON voo.id_orcamento = o.id_orcamento) AS companhia_volta WHERE ida_volta = 'Volta' AND id_orcamento = o.id_orcamento) AS companhia_volta, \
#                         s.id_servico, s.descricao, s.obs_servicos, s.valor_total_servicos, \
#                         c.*,  \
#                         (SELECT voo.pais_saida FROM voo WHERE ida_volta = 'Ida' AND voo.id_orcamento = o.id_orcamento) AS pais_saida_ida,\
#                         (SELECT voo.cidade_saida FROM voo WHERE ida_volta = 'Ida' AND voo.id_orcamento = o.id_orcamento) AS cidade_saida_ida, \
#                         (SELECT voo.aeroporto_saida FROM voo WHERE ida_volta = 'Ida' AND voo.id_orcamento = o.id_orcamento) AS aeroporto_saida_ida, \
#                         (SELECT voo.pais_destino FROM voo WHERE ida_volta = 'Ida' AND voo.id_orcamento = o.id_orcamento) AS pais_destino_ida, \
#                         (SELECT voo.cidade_destino FROM voo WHERE ida_volta = 'Ida' AND voo.id_orcamento = o.id_orcamento) AS cidade_destino_ida, \
#                         (SELECT voo.aeroporto_destino FROM voo WHERE ida_volta = 'Ida' AND voo.id_orcamento = o.id_orcamento) AS aeroporto_destino_ida, \
#                         (SELECT voo.pais_saida FROM voo WHERE ida_volta = 'Volta' AND voo.id_orcamento = o.id_orcamento) AS pais_saida_volta, \
#                         (SELECT voo.cidade_saida FROM voo WHERE ida_volta = 'Volta' AND voo.id_orcamento = o.id_orcamento) AS cidade_saida_volta, \
#                         (SELECT voo.aeroporto_saida FROM voo WHERE ida_volta = 'Volta' AND voo.id_orcamento = o.id_orcamento) AS aeroporto_saida_volta, \
#                         (SELECT voo.pais_destino FROM voo WHERE ida_volta = 'Volta' AND voo.id_orcamento = o.id_orcamento) AS pais_destino_volta, \
#                         (SELECT voo.cidade_destino FROM voo WHERE ida_volta = 'Volta' AND voo.id_orcamento = o.id_orcamento) AS cidade_destino_volta, \
#                         (SELECT voo.aeroporto_destino FROM voo WHERE ida_volta = 'Volta' AND voo.id_orcamento = o.id_orcamento) AS aeroporto_destino_volta, \
#                         v.id_venda, v.data_venda, v.forma_pgto, v.valor_final, v.entrada, v.n_parcelas, v.valor_parcelas, v.comissao \
#                         FROM {} o \
#                         LEFT JOIN {} p ON p.id_produto = o.id_produto \
#                         LEFT JOIN {} c ON o.id_cliente = c.id_cliente \
#                         LEFT JOIN {} h ON o.id_hospedagem = h.id_hospedagem \
#                         LEFT JOIN {} s ON o.id_servico = s.id_servico \
#                         LEFT JOIN {} voo ON o.id_orcamento = voo.id_orcamento \
#                         LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia \
#                         LEFT JOIN vendas v ON o.id_orcamento = v.id_orcamento \
#                         GROUP BY o.id_orcamento, p.id_produto, o.id_cliente, o.valor_total, p.nome_produto, p.tipo, p.valor_minimo, p.pais, p.cidade, c.nome, h.id_hospedagem,h.endereco, h.diaria, h.dias, h.obs, s.id_servico, s.descricao, s.obs_servicos, s.valor_total_servicos, c.id_cliente, v.id_venda").format(
#             sql.Identifier("orcamento"),
#             sql.Identifier("produto"),
#             sql.Identifier("cliente"),
#             sql.Identifier("hospedagem"),
#             sql.Identifier("servico"),
#             sql.Identifier("voo"),
#             sql.Identifier("servico"),
#         )
#         cur.execute(query)
#         orcamentos = cur.fetchall()
#         conn.close()
#         return orcamentos
#     else:
#         return []
    
def teste_get_orcamentos():
        
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        query = sql.SQL("SELECT o.*, p.*, c.*, h.*, s.*,v.id_venda, v.data_venda, v.comissao, v.valor_final, v.status_venda, v.valor_total_gasto, v.forma_pgto, v.entrada, v.n_parcelas, v.valor_parcelas, paises.pais AS pais_nome, cidades.cidade AS cidade_nome, \
                        json_agg(voo_lista.*) FILTER (WHERE voo_lista.ida_volta = 'Ida') AS voo_lista_ida ,\
                        json_agg(voo_lista.*) FILTER (WHERE voo_lista.ida_volta = 'Volta') AS voo_lista_volta \
                        FROM {} o \
                        LEFT JOIN (SELECT voo.*, comp.*, ci_saida.cidade AS cidade_saida_nome, ci_destino.cidade AS cidade_destino_nome, pais_saida.pais AS pais_saida_nome, pais_destino.pais AS pais_destino_nome FROM voo \
                            LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia\
							LEFT JOIN cidades ci_saida ON voo.cidade_saida = ci_saida.id\
							LEFT JOIN cidades ci_destino ON voo.cidade_destino = ci_destino.id\
							LEFT JOIN paises pais_saida ON pais_saida.id = ci_saida.id_pais\
							LEFT JOIN paises pais_destino ON pais_destino.id = ci_destino.id_pais) AS voo_lista ON voo_lista.id_orcamento = o.id_orcamento\
                        LEFT JOIN {} p ON p.id_produto = o.id_produto \
                        LEFT JOIN {} c ON o.id_cliente = c.id_cliente \
                        LEFT JOIN {} h ON o.id_hospedagem = h.id_hospedagem \
                        LEFT JOIN {} s ON o.id_servico = s.id_servico \
                        LEFT JOIN vendas v ON o.id_orcamento = v.id_orcamento \
                        LEFT JOIN paises ON paises.id = p.pais \
                        LEFT JOIN cidades ON cidades.id = p.cidade \
                        GROUP BY o.id_orcamento, p.id_produto, o.id_cliente, o.valor_total, p.nome_produto, p.tipo, p.valor_minimo, p.pais, p.cidade, c.nome, h.id_hospedagem,h.endereco, h.diaria, h.dias, h.obs, s.id_servico, s.descricao, s.obs_servicos, s.valor_total_servicos, c.id_cliente, v.id_venda, paises.id, cidades.id").format(
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
        columns_ida = pd.json_normalize(data['voo_lista_ida'].explode()).add_suffix('_ida')
        columns_volta = pd.json_normalize(data['voo_lista_volta'].explode()).add_suffix('_volta')
        data = data.join(columns_ida).join(columns_volta)
        #data.to_csv('orcamentos_completo.csv', index=False)
        return data.to_dict("records")
    else:
        return []
    
def get_orcamento_simplificado(id_orcamento=None):
    conn = db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)
        if id_orcamento is not None:
            query = sql.SQL("SELECT o.id_orcamento,c.nome FROM {} o LEFT JOIN cliente c ON o.id_cliente = c.id_cliente WHERE o.id_orcamento NOT IN (SELECT id_orcamento FROM vendas) OR o.id_orcamento = %s").format(sql.Identifier("orcamento"))
            cur.execute(query, (id_orcamento,))
        else:
            query = sql.SQL("SELECT o.id_orcamento,c.nome FROM {} o LEFT JOIN cliente c ON o.id_cliente = c.id_cliente WHERE o.id_orcamento NOT IN (SELECT id_orcamento FROM vendas)").format(sql.Identifier("orcamento"))
            cur.execute(query)
        orcamentos = cur.fetchall()
        conn.close()
        return orcamentos
    else:
        return []
    
#------------------------------------------------------------------------------DW

def dw_connection():

    dw_uri = os.getenv("DW_RUI")

    connection = urlparse(dw_uri)

    connection_params = {
        'dbname': connection.path[1:],
        'user': connection.username,
        'password': connection.password,
        'host': connection.hostname,
        'port': connection.port
    }

    try:
        conn = pg.connect(**connection_params, options="-c client_encoding=UTF8")
        conn.set_client_encoding('UTF8')
        print("Conexão bem-sucedida!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao data warehouse: {e}")
        return None
    
def update_dw(conn=None):

    engine = create_engine(os.getenv("DW_RUI"))

    if not conn:
        conn = db_connection()
        conn.set_client_encoding('UTF8')

    if conn:

        cur = conn.cursor(cursor_factory=pg.extras.RealDictCursor)

        cur.execute("SELECT id_cliente, sexo, data_nascimento FROM cliente")
        clientes = cur.fetchall()
        clientes_df = pd.DataFrame(clientes)
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE cliente RESTART IDENTITY CASCADE;"))
            conn.commit()
        clientes_df.to_sql('cliente', engine, if_exists='append', index=False)

        cur.execute("SELECT id_produto, nome_produto, tipo, valor_minimo, pais, cidade FROM produto")
        produtos = cur.fetchall()
        produtos_df = pd.DataFrame(produtos)
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE produto RESTART IDENTITY CASCADE;"))
            conn.commit()
        produtos_df.to_sql('produto', engine, if_exists='append', index=False)

        

        cur.execute("SELECT id_servico, valor_total_servicos FROM servico")
        servicos = cur.fetchall()
        servicos_df = pd.DataFrame(servicos)
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE servicos RESTART IDENTITY CASCADE;"))
            conn.commit()
        servicos_df.to_sql('servicos', engine, if_exists='append', index=False)

        cur.execute("SELECT id_hospedagem, diaria, dias FROM hospedagem")
        hospedagem = cur.fetchall()
        hospedagem_df = pd.DataFrame(hospedagem)

        hospedagem_df['valor_total_hospedagem'] = hospedagem_df['diaria'] * hospedagem_df['dias']
        hospedagem_df.drop(columns=['diaria', 'dias'], inplace=True)
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE hospedagem RESTART IDENTITY CASCADE;"))
            conn.commit()
        hospedagem_df.to_sql('hospedagem', engine, if_exists='append', index=False)

        cur.execute("SELECT id_cliente, sexo, data_nascimento, cidade, estado FROM cliente")
        cliente = cur.fetchall()
        cliente_df = pd.DataFrame(cliente)

        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE cliente RESTART IDENTITY CASCADE;"))
            conn.commit()
        cliente_df.to_sql('cliente', engine, if_exists='append', index=False)

        cur.execute("SELECT v.id_venda, v.data_venda, o.id_produto, c.id_cliente, o.id_orcamento, o.id_servico, o.id_hospedagem, v.comissao, v.valor_final, v.status_venda, v.valor_total_gasto FROM" \
        " vendas v LEFT JOIN orcamento o ON v.id_orcamento = o.id_orcamento" \
        " LEFT JOIN cliente c ON o.id_cliente = c.id_cliente")
        vendas = cur.fetchall()
        vendas_df = pd.DataFrame(vendas)

        cur.execute("SELECT v.id_voo, v.valor_passagem, v.qtd_passagens, comp.id_companhia, comp.nome_companhia, v.id_orcamento FROM voo v LEFT JOIN companhia_aerea comp ON comp.id_companhia = v.id_companhia WHERE v.id_orcamento IN (SELECT id_orcamento FROM vendas)")
        voo = cur.fetchall()
        voo_df = pd.DataFrame(voo)

        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE voo RESTART IDENTITY CASCADE;"))
            conn.execute(text("TRUNCATE TABLE vendas RESTART IDENTITY CASCADE;"))
            conn.commit()
        vendas_df.to_sql('vendas', engine, if_exists='append', index=False)
        voo_df.to_sql('voo', engine, if_exists='append', index=False)
               
    else:
        print("Erro ao conectar ao banco de dados")

    conn.close()
    return


def search_database_paises(search_query: str) -> dict:
    if not search_query or len(search_query) < 2:
        return {}  # Avoid searching for single characters to save database load
        
    conn = db_connection()
    cur = conn.cursor() # Fast standard tuple cursor
    
    # Use ILIKE for case-insensitive matching; % formats the wildcard
    sql = "SELECT id, pais FROM paises WHERE pais ILIKE %s LIMIT 50"
    cur.execute(sql, (f"%{search_query}%",))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Fast CPython dictionary comprehension
    return {str(row[0]): row[1] for row in rows}


def search_database_cidades(search_query: str, pais: str) -> dict:
    if not search_query or len(search_query) < 2:
        return {}  # Avoid searching for single characters to save database load
        
    conn = db_connection()
    cur = conn.cursor() # Fast standard tuple cursor
    
    # Use ILIKE for case-insensitive matching; % formats the wildcard
    sql = "SELECT id, cidade FROM cidades WHERE cidade ILIKE %s AND id_pais = %s LIMIT 50"
    cur.execute(sql, (f"%{search_query}%", pais))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Fast CPython dictionary comprehension
    return {str(row[0]): row[1] for row in rows}





