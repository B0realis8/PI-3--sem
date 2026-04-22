-- Active: 1776135066399@@127.0.0.1@5432@PI 3 SEM
-- Active: 1776135066399@@127.0.0.1@5432@PI - 3ºsem
DROP TABLE IF EXISTS vendas CASCADE;
CREATE TABLE vendas (

id_venda SERIAL PRIMARY KEY,
data_venda DATE NOT NULL,
id_orcamento INT REFERENCES orcamento(id_orcamento),
quantidade INT,
forma_pgto VARCHAR(20),
valor_total NUMERIC(20,2),
entrada NUMERIC(20,2),
n_parcelas INT,
valor_parcelas NUMERIC(10,2),
comissao NUMERIC,
lucro_total NUMERIC,

);

DROP TABLE IF EXISTS cliente CASCADE;
CREATE TABLE cliente (

id_cliente SERIAL PRIMARY KEY ,
nome VARCHAR(100) NOT NULL,
sexo CHAR(1) CHECK (sexo in('F','M')),
data_nascimento DATE,
cpf CHAR(11) NOT NULL UNIQUE

);


DROP TABLE IF EXISTS produto CASCADE;
CREATE TABLE produto (

id_produto SERIAL PRIMARY KEY,
nome_produto VARCHAR(100),
tipo VARCHAR(20),
valor_minimo NUMERIC(10,2),
pais VARCHAR(50),
cidade VARCHAR(50)

);


DROP TABLE IF EXISTS servico CASCADE;
CREATE TABLE servico (

id_servico SERIAL PRIMARY KEY,
nome_servico VARCHAR(100),
descricao TEXT,
valor NUMERIC(10,2)

);


DROP TABLE IF EXISTS companhia_aerea CASCADE;
CREATE TABLE companhia_aerea (

id_companhia SERIAL PRIMARY KEY,
nome_companhia VARCHAR(50),
pais VARCHAR(50)

);


DROP TABLE IF EXISTS voo CASCADE;
CREATE TABLE voo (

id_voo SERIAL PRIMARY KEY,
pais_saida VARCHAR(50),
cidade_saida VARCHAR(50),
aeroporto_saida CHAR(3),
dt_hr_saida TIMESTAMP,
pais_destino VARCHAR(50),
cidade_destino VARCHAR(50),
aeroporto_destino CHAR(3),
dt_hr_chegada TIMESTAMP,
valor_passagem NUMERIC(10,2),
id_companhia INT REFERENCES companhia_aerea(id_companhia),
obs TEXT

);

DROP TABLE IF EXISTS orcamento CASCADE;
CREATE TABLE orcamento (

id_orcamento SERIAL PRIMARY KEY,
id_produto INT REFERENCES produto(id_produto) ON DELETE CASCADE,
id_voo INT REFERENCES voo(id_voo),
id_cliente INT REFERENCES cliente(id_cliente),
valor_total NUMERIC (20,2)
);


DROP TABLE IF EXISTS join_servicos_orcamento CASCADE;
CREATE TABLE join_servicos_orcamento (

PRIMARY KEY(id_servico, id_orcamento),
id_servico INT REFERENCES servico(id_servico) ON DELETE CASCADE,
id_orcamento INT REFERENCES orcamento(id_orcamento) ON DELETE CASCADE,
quantidade INT
	
);


DROP TABLE IF EXISTS instagram CASCADE;
CREATE TABLE instagram (

post_id SERIAL PRIMARY KEY,
account_id INT UNIQUE,
account_type VARCHAR(20),
follower_count INT,
media_type VARCHAR(20),
content_category VARCHAR(30),
traffic_source VARCHAR(30),
has_call_to_action BOOLEAN,
post_datetime TIMESTAMP,
post_date DATE,
post_hour INT,
day_of_week VARCHAR(20),
likes INT,
comments INT,
shares INT,
saves INT,
reach INT,
impression INT,
engagement_rate NUMERIC,
followers_gained INT,
caption_length INT,
hashtags_count INT,
performance_bucket VARCHAR(10),
produto_id INT REFERENCES produto(id_produto)

)
