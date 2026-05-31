SELECT * FROM paises ORDER BY id DESC
SELECT * FROM cidades LEFT JOIN paises ON cidades.id_pais = paises.id WHERE cidades.pais LIKE '%Italy%'
SELECT * FROM cidades LEFT JOIN paises ON cidades.id_pais = paises.id AND paises.pais = 'Brasil' AND cidades.cidade = 'Mauá' ORDER BY paises.id
UPDATE cidades SET id_pais = p.id FROM paises p WHERE cidades.pais = p.pais_en

SELECT c.pais
FROM cidades c
LEFT JOIN paises p ON c.pais = p.pais_en
WHERE p.id IS NULL
LIMIT 50;

SELECT o.*, p.*, c.*, h.*, s.*,
json_agg(voo_lista.*) FILTER (WHERE voo_lista.ida_volta = 'Ida') AS voo_lista_ida,
json_agg(voo_lista.*) FILTER (WHERE voo_lista.ida_volta = 'Volta') AS voo_lista_volta
FROM orcamento o
LEFT JOIN (SELECT voo.*, comp.* FROM voo LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia) AS voo_lista ON voo_lista.id_orcamento = o.id_orcamento
LEFT JOIN produto p ON p.id_produto = o.id_produto
LEFT JOIN cliente c ON o.id_cliente = c.id_cliente
LEFT JOIN hospedagem h ON o.id_hospedagem = h.id_hospedagem
LEFT JOIN servico s ON o.id_servico = s.id_servico
LEFT JOIN vendas v ON o.id_orcamento = v.id_orcamento
GROUP BY o.id_orcamento, p.id_produto, o.id_cliente, o.valor_total, p.nome_produto, p.tipo, p.valor_minimo, p.pais, p.cidade, c.nome, h.id_hospedagem,h.endereco, h.diaria, h.dias, h.obs, s.id_servico, s.descricao, s.obs_servicos, s.valor_total_servicos, c.id_cliente, v.id_venda

SELECT json_agg(json_build_object('voo_lista_ida', (SELECT voo.*, comp.* FROM voo LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia WHERE ida_volta = 'Ida'))) AS voo_lista_ida

SELECT orcamento.*, (json_agg(voo.*) FILTER (WHERE ida_volta = 'Ida') AS voo_lista_ida FROM (SELECT voo.*, comp.* FROM voo LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia) AS voo) FROM orcamento o LEFT JOIN voo v on v.id_orcamento = o.id_orcamento

SELECT json_agg(voo_ida.*) FILTER (WHERE ida_volta = 'Ida') AS voo_lista_ida FROM (SELECT voo.*, comp.* FROM voo LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia) AS voo_ida

SELECT voo.*, comp.* FROM voo LEFT JOIN companhia_aerea comp ON voo.id_companhia = comp.id_companhia