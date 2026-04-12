DROP TABLE IF EXISTS vendas;
CREATE TABLE vendas (

);

DROP TABLE IF EXISTS cliente;
CREATE TABLE cliente (

id_cliente SERIAL PRIMARY KEY ,
nome VARCHAR(100) NOT NULL,
cpf CHAR(11) NOT NULL UNIQUE

);


DROP TABLE IF EXISTS produto;
CREATE TABLE produto (

id_produto SERIAL PRIMARY KEY,
nome_produto VARCHAR(100),
tipo VARCHAR(20),
valor_minimo NUMERIC(10,2),
pais VARCHAR(50),
cidade VARCHAR(50)

);


DROP TABLE IF EXISTS servico;
CREATE TABLE servico (

id_servico SERIAL PRIMARY KEY,
nome_servico VARCHAR(100),
descricao TEXT,
valor NUMERIC(10,2)

);


DROP TABLE IF EXISTS companhia_aerea;
CREATE TABLE companhia_aerea (

id_companhia SERIAL PRIMARY KEY,
nome_companhia VARCHAR(50),
pais VARCHAR(50)

);


DROP TABLE IF EXISTS voo;
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

DROP TABLE IF EXISTS orcamento;
CREATE TABLE orcamento (

id_orcamento SERIAL PRIMARY KEY,
id_produto INT REFERENCES produto(id_produto) ON DELETE CASCADE,
id_voo INT REFERENCES voo(id_voo),
id_cliente INT REFERENCES cliente(id_cliente),
valor_total NUMERIC (20,2)
);


DROP TABLE IF EXISTS join_servicos_orcamento;
CREATE TABLE join_servicos_orcamento (

PRIMARY KEY(id_servico, id_orcamento),
id_servico INT REFERENCES servico(id_servico) ON DELETE CASCADE,
id_orcamento INT REFERENCES orcamento(id_orcamento) ON DELETE CASCADE,
quantidade INT
	
);

SELECT * FROM orcamento JOIN join_servicos_orcamento USING (id_orcamento)
SELECT * FROM orcamento JOIN voo USING (id_voo)
SELECT o.id_orcamento, v.id_voo FROM orcamento o JOIN voo v USING (id_voo)
