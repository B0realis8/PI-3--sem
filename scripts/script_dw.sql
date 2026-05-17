DROP TABLE IF EXISTS cliente CASCADE;
CREATE TABLE cliente(

id_cliente INT PRIMARY KEY,
sexo CHAR(1) CHECK (sexo IN ('M','F')),
data_nascimento DATE,
cidade VARCHAR(50),
estado CHAR(2)

);

DROP TABLE IF EXISTS produto CASCADE;
CREATE TABLE produto(

id_produto INT PRIMARY KEY,
nome_produto VARCHAR(100),
tipo VARCHAR(20),
valor_minimo NUMERIC(10,2),
pais VARCHAR(50),
cidade VARCHAR(50)

);



DROP TABLE IF EXISTS servicos CASCADE;
CREATE TABLE servicos (

id_servico INT PRIMARY KEY,
valor_total_servicos NUMERIC(10,2)

);

DROP TABLE IF EXISTS hospedagem CASCADE;
CREATE TABLE hospedagem (

id_hospedagem INT PRIMARY KEY,
valor_total_hospedagem NUMERIC

);



DROP TABLE IF EXISTS vendas CASCADE;
CREATE TABLE vendas(

id_venda INT PRIMARY KEY,
data_venda DATE,
id_produto INT REFERENCES produto(id_produto) ON DELETE CASCADE,
id_cliente INT REFERENCES cliente(id_cliente) ON DELETE CASCADE,
id_orcamento INT UNIQUE,
id_servico INT REFERENCES servicos(id_servico) ON DELETE CASCADE,
id_hospedagem INT REFERENCES hospedagem (id_hospedagem) ON DELETE CASCADE,
comissao NUMERIC(10,2),
valor_final NUMERIC(10,2)

);

DROP TABLE IF EXISTS voo CASCADE;
CREATE TABLE voo (

id_voo INT PRIMARY KEY,
valor_passagem NUMERIC(10,2),
qtd_passagens INT,
id_companhia INT,
nome_companhia VARCHAR,
id_orcamento INT REFERENCES vendas(id_orcamento) ON DELETE CASCADE

);