
DROP TABLE IF EXISTS paises CASCADE;
CREATE TABLE paises (

id INT PRIMARY KEY,
pais VARCHAR,
pais_en VARCHAR

);

DROP TABLE IF EXISTS cidades CASCADE;
CREATE TABLE cidades (

pais VARCHAR,
cidade VARCHAR,
id INT PRIMARY KEY,
id_pais INT REFERENCES paises(id)

)

SELECT * FROM paises
SELECT * FROM cidades LEFT JOIN paises ON cidades.id_pais = paises.id
UPDATE cidades SET id_pais = p.id FROM paises p WHERE cidades.pais = p.pais_en

SELECT * FROM vendas