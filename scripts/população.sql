BEGIN;
TRUNCATE TABLE cliente RESTART IDENTITY CASCADE;
INSERT INTO cliente (nome, sexo, data_nascimento, cpf, telefone, cidade, estado) VALUES
('Ana Paula Silva', 'F', '1985-03-12', '12345678901', '(11)98765-4321', 1076532519, 'SP'),
('Bruno Costa Santos', 'M', '1990-07-25', '23456789012', '(21)99876-5432', 1076532519, 'SP'),
('Carla Mendes Lima', 'F', '1978-11-05', '34567890123', '(31)99765-4321',1076532519, 'SP'),
('Daniel Oliveira Souza', 'M', '1995-02-18', '45678901234', '(41)99654-3210', 1076532519, 'SP'),
('Eduarda Ferreira Rocha', 'F', '1982-09-30', '56789012345', '(51)99543-2109', 1076532519, 'SP'),
('Fernando Alves Pinto', 'M', '1988-06-14', '67890123456', '(61)99432-1098', 1076532519, 'SP'),
('Gabriela Nunes Castro', 'F', '1992-12-01', '78901234567', '(71)99321-0987', 1076532519, 'SP'),
('Henrique Martins Dias', 'M', '1980-04-22', '89012345678', '(81)99210-9876', 1076532519, 'SP'),
('Isabela Correia Gomes', 'F', '1997-08-09', '90123456789', '(85)99109-8765', 1076532519, 'SP'),
('João Pedro Barbosa', 'M', '1983-10-17', '01234567890', '(91)99098-7654', 1076532519, 'SP'),
('Karina Lopes Teixeira', 'F', '1991-05-28', '11223344557', '(92)98987-6543', 1076532519, 'SP'),
('Leonardo Sousa Ribeiro', 'M', '1975-01-19', '22334455668', '(27)98876-5432', 1076532519, 'SP'),
('Mariana Cardoso Neves', 'F', '1989-07-07', '33445566779', '(82)98765-4321', 1076532519, 'SP'),
('Nícolas Rocha Mendonça', 'M', '1993-03-03', '44556677880', '(79)98654-3210', 1076625886, 'SP'),
('Olivia Batista Pires', 'F', '1986-12-12', '55667788997', '(86)98543-2109', 1076625886, 'SP'),
('Paulo Henrique Silva', 'M', '1979-09-21', '66778899002', '(84)98432-1098', 1076625886, 'SP'),
('Quintino Alves Moura', 'M', '1984-02-14', '77889900113', '(68)98321-0987', 1076625886, 'SP'),
('Rafaela Cunha Vidal', 'F', '1996-11-26', '88990011224', '(69)98210-9876', 1076477498, 'SP'),
('Samuel Ferreira Leite', 'M', '1987-04-05', '99001122335', '(95)98109-8765', 1076477498, 'SP'),
('Tatiane Gonçalves Maia', 'F', '1994-08-19', '00112233446', '(63)98098-7654', 1076967355, 'MG'),
('Ubiratan Castro Melo', 'M', '1977-06-30', '11223344558', '(67)97987-6543', 1076967355, 'MG'),
('Valéria Souza Cruz', 'F', '1998-01-11', '22334455669', '(62)97876-5432', 1076887657, 'RJ'),
('Wagner Lima Barros', 'M', '1981-10-09', '33445566770', '(11)97765-4321', 1076793227, 'SP'),
('Xênia Carvalho Duarte', 'F', '1990-05-20', '44556677881', '(21)97654-3210',1076887657, 'RJ'),
('Yuri Santos Oliveira', 'M', '1985-12-25', '55667788992', '(31)97543-2109', 1076793227, 'SP'),
('Zuleide Pereira Araújo', 'F', '1976-03-08', '66778899003', '(41)97432-1098', 1076701712, 'PR');


INSERT INTO produto (nome_produto, tipo, valor_minimo, pais, cidade) VALUES
('Pacote de viagem Canadá - Montreal', 'Pacote de viagem', 4250.00, 39, 1124586170),
('Intercâmbio Argentina - Buenos Aires', 'Intercâmbio', 3800.00, 11, 1032717330),
('Pacote de viagem Portugal - Lisboa', 'Pacote de viagem', 5200.00, 177, 1620619017),
('Intercâmbio Inglaterra - Londres', 'Intercâmbio', 8900.00, 232, 1826645935),
('Pacote de viagem França - Paris', 'Pacote de viagem', 6700.00, 75, 1250015082),
('Intercâmbio Espanha - Madrid', 'Intercâmbio', 4500.00, 207, 1724616994),
('Pacote de viagem Itália - Roma', 'Pacote de viagem', 5900.00, 107, 1380382862),
('Intercâmbio Alemanha - Berlim', 'Intercâmbio', 7200.00, 82, 1276451290),
('Pacote de viagem Estados Unidos - Orlando', 'Pacote de viagem', 5300.00, 233, 1840034016),
('Intercâmbio Irlanda - Dublin', 'Intercâmbio', 6800.00, 156, 1528355309),
('Pacote de viagem Japão - Tóquio', 'Pacote de viagem', 2600.00, 55, 1152554349),
('Intercâmbio Austrália - Sydney', 'Intercâmbio', 3500.00, 173, 1604162901);


TRUNCATE TABLE servico RESTART IDENTITY CASCADE;
INSERT INTO servico (descricao, valor_total_servicos, obs_servicos) VALUES
('Chip internacional para Europa com 10GB de dados', 189.90, 'Válido por 30 dias. Inclui chamadas locais e internacionais para fixos.'),
('Seguro viagem assistência médica e odontológica', 450.00, 'Cobertura de US$ 100 mil por 15 dias. Inclui cancelamento de voos.'),
('Pacote de passeios completos - Tour pela cidade', 350.00, 'Inclui guia bilíngue, transporte e entradas de museus. Duração aproximada de 8h.'),
('Assessoria para visto americano', 299.00, 'Inclui preenchimento de formulários, agendamento e simulação de entrevista.'),
('Traslado aeroporto - hotel (ida e volta)', 180.00, 'Veículo compartilhado. Disponível 24h. Inclui 1 bagagem por pessoa.'),
('Chip internacional para América do Norte', 199.90, '15GB de dados válidos por 30 dias. Ativação automática no destino.'),
('Pacote de passeios - Vinícolas no Chile', 520.00, 'Visita a 3 vinícolas com degustação premium e almoço incluso.'),
('Assessoria para passaporte', 150.00, 'Inclui agendamento, orientação sobre documentos e revisão da solicitação.'),
('Aluguel de carro por 7 dias', 840.00, 'Categoria econômica com câmbio manual, seguro básico incluso e quilometragem livre.'),
('Tour gastronômico pela Itália', 680.00, 'Visita a 5 restaurantes típicos com menu degustação e traslado incluso.'),
('Chip internacional para Ásia', 229.90, '8GB de dados para 20 dias. Funciona no Japão, Coreia, China e Sudeste Asiático.'),
('Guia de turismo privativo por 3 dias', 1200.00, 'Guia fluente em português. Horário flexível. Inclui traslado particular.'),
('Pacote de mergulho - Caribe', 890.00, '2 mergulhos guiados com equipamento completo e certificação inclusa para iniciantes.'),
('Assessoria para intercâmbio', 1990.00, 'Inclui orientação para escolha de curso, universidade, visto e acomodação.'),
('Traslado de luxo por 5 dias', 2500.00, 'Veículo premium com motorista particular, água e Wi-Fi disponíveis a bordo.'),
('Chip internacional - Pacote América do Sul', 149.90, '10GB de dados válidos por 30 dias. Cobertura em Argentina, Chile, Uruguai e Peru.'),
('Pacote de fotos profissional', 499.00, 'Ensaio fotográfico de 2h nos principais pontos turísticos da cidade.'),
('Aluguel de equipamento de inverno', 300.00, 'Inclui jaqueta, calça, luvas e botas por até 7 dias. Tamanhos do PP ao XGG.'),
('Pacote de passeios ecológicos - Costa Rica', 750.00, 'Visita a 2 parques nacionais, trilhas guiadas e observação de animais.'),
('Assessoria para câmbio de moeda', 0.00, 'Serviço gratuito para clientes com pacotes acima de R$ 5.000. Taxas especiais.'),
('Sala VIP em aeroportos (5 entradas)', 550.00, 'Válido por 12 meses em mais de 50 aeroportos no mundo. Inclui bebidas e petiscos.'),
('Pacote de passeios românticos - Paris', 980.00, 'Jantar no Seine, piquenique na Torre Eiffel e passeio de barco. Inclui fotógrafo.'),
('Chip internacional com plano família', 349.90, '4 chips com 15GB cada. Compartilhamento de dados entre os membros.'),
('Assessoria para viagem com pets', 280.00, 'Orientações sobre documentação, vacinas, caixa de transporte e companhias aéreas pet-friendly.'),
('Pacote de ingressos rápidos para atrações', 420.00, 'Skip-the-line em 5 principais atrações do destino (Disney, museus, parques).');

TRUNCATE TABLE hospedagem RESTART IDENTITY CASCADE;
INSERT INTO hospedagem (endereco, diaria, dias, obs) VALUES
('1235 Boulevard Saint-Germain, 6th Arrondissement, Paris, France', 520.00, 5, 'Café da manhã incluso. Vista para o Sena. Check-out às 12h. Academia disponível.'),
('45 Calle de Alcalá, Centro, Madrid, Spain', 380.00, 4, 'Próximo ao Museu do Prado. Quartos com isolamento acústico. Estacionamento conveniado.'),
('789 Collins Avenue, Miami Beach, FL, USA', 680.00, 3, 'Frente para o mar. Piscina rooftop com bar. Aceita pets mediante taxa.'),
('22 Baker Street, Marylebone, London, United Kingdom', 750.00, 6, 'Hotel boutique histórico. Inclui serviço de concierge 24h. Proibido fumar.'),
('150 Gran Vía, Centro, Madrid, Spain', 450.00, 2, 'Suíte luxo com hidromassagem. Café da manhã servido no quarto.'),
('55 Rue Sainte-Catherine, Quartier Latin, Bordeaux, France', 290.00, 7, 'Hostel compartilhado. Café da manhã simples incluso. Wi-Fi gratuito.'),
('888 Ocean Drive, South Beach, Miami Beach, FL, USA', 850.00, 3, 'Pé na areia. Serviço de praia com cadeiras e guarda-sol. Valet parking.'),
('10 Downing Street, Westminster, London, United Kingdom', 420.00, 5, 'Próximo ao Big Ben e Parlamento. Arquitetura georgiana. Estacionamento pago.'),
('333 Las Ramblas, El Raval, Barcelona, Spain', 410.00, 4, 'Vista para as Ramblas. Piscina na cobertura. Inclui aluguel de bikes.'),
('77 Avenida da Liberdade, Santo António, Lisbon, Portugal', 310.00, 5, 'A 500m do Parque Eduardo VII. Academia 24h. Pequeno-almoço incluso.'),
('555 Fifth Avenue, Midtown Manhattan, New York, NY, USA', 1250.00, 3, 'Hotel de luxo. Quartos com vista para a cidade. Lounge executivo incluso.'),
('88 Via del Corso, Centro Storico, Rome, Italy', 480.00, 4, 'Hotel histórico reformado. A 10min do Coliseu. Ar condicionado central.'),
('222 Avenida Corrientes, Abasto, Buenos Aires, Argentina', 280.00, 6, 'Hospedagem econômica. Próximo ao Teatro Colón. Ar condicionado.'),
('33 Passeig de Gràcia, Eixample, Barcelona, Spain', 590.00, 5, 'Piscina com bar. Inclui toalhas de praia. Obras de Gaudí próximas.'),
('444 Bourbon Street, French Quarter, New Orleans, LA, USA', 370.00, 4, 'A 200m da Jackson Square. Jazz ao vivo no lobby. Café da manhã regional.'),
('66 Bahnhofstrasse, Altstadt, Zurich, Switzerland', 780.00, 3, 'Frente para o rio Limmat. Cozinha compacta nos apartamentos. Estacionamento coberto.'),
('99 Rue de la Paix, Quartier de l''Opéra, Paris, France', 920.00, 2, 'Suíte executiva. Acesso à spa. Serviço de baby-sitter sob consulta.'),
('111 Calle Florida, Microcentro, Buenos Aires, Argentina', 340.00, 5, 'Próximo à Casa Rosada. Sala de reuniões. Check-in rápido 24h.'),
('222 Avenida 18 de Julio, Centro, Montevideo, Uruguay', 310.00, 4, 'Lareira na suíte executiva. Café da manhã colonial. Estacionamento conveniado.'),
('333 Robson Street, Downtown, Vancouver, BC, Canada', 430.00, 6, 'A 1km da praia. Churrasqueira coletiva. Quartos com aquecimento central.'),
('444 Gran Vía, Centro, Zaragoza, Spain', 270.00, 5, 'Ótima localização para compras. Toalhas e lençóis inclusos. Ar condicionado.'),
('555 Rue Sherbrooke Ouest, Golden Square Mile, Montreal, QC, Canada', 390.00, 4, 'A 2 quadras do Museu de Belas Artes. Café da manhã com frutas frescas.'),
('666 Avenida Paulista, Bela Vista, São Paulo, SP, Brazil', 410.00, 3, 'Andar executivo com vista para a cidade. Lounge com bebidas liberadas. Estacionamento.'),
('777 Avenida Presidente Vargas, Centro, Rio de Janeiro, RJ, Brazil', 350.00, 5, 'Próximo à Catedral Metropolitana. Academia moderna. Wi-Fi gratuito.'),
('888 Avenida Revolución, Zona Centro, Tijuana, BC, Mexico', 220.00, 7, 'Hostel familiar. Cozinha compartilhada. Wi-Fi disponível em áreas comuns.');

INSERT INTO companhia_aerea (nome_companhia, pais) VALUES
('LATAM Brasil', 31),      -- Brasil (ID 31 - exemplo)
('Azul Linhas Aéreas', 31),
('Gol Linhas Aéreas', 31),
('American Airlines', 233), -- Estados Unidos
('Delta Air Lines', 233),   -- Estados Unidos
('United Airlines', 233),   -- Estados Unidos
('Air France', 75),         -- França
('British Airways', 232),   -- Reino Unido
('Lufthansa', 82),          -- Alemanha
('Emirates', 231),          -- Emirados Árabes Unidos
('Qatar Airways', 179),     -- Catar
('Air Canada', 39),         -- Canadá
('Iberia', 207),            -- Espanha
('Alitalia', 107),          -- Itália
('KLM Royal Dutch Airlines', 156); -- Holanda

TRUNCATE TABLE orcamento RESTART IDENTITY CASCADE;
INSERT INTO orcamento (id_produto, id_cliente, id_hospedagem, id_servico, valor_total) VALUES
(1, 1, 1, 1, 4859.90),   -- Pacote Canadá (4250) + Hospedagem Paris (520) + Chip Europa (189.90)
(2, 2, 2, 2, 4630.00),   -- Intercâmbio Argentina (3800) + Hospedagem Madrid (380) + Seguro viagem (450)
(3, 3, 3, 3, 7550.00),   -- Pacote Portugal (5200) + Hospedagem Miami (680) + Passeios (350) -> valor ajustado
(4, 4, 4, 4, 9739.00),   -- Intercâmbio Inglaterra (8900) + Hospedagem Londres (750) + Visto EUA (299) -> ajustado
(5, 5, 5, 5, 7730.00),   -- Pacote França (6700) + Hospedagem Madrid 2 (450) + Traslado (180)
(6, 6, 6, 6, 5089.90),   -- Intercâmbio Espanha (4500) + Hospedagem Bordeaux (290) + Chip América Norte (199.90)
(7, 7, 7, 7, 7190.00),   -- Pacote Itália (5900) + Hospedagem Miami Beach 2 (850) + Passeios vinícolas (520) -> ajustado
(8, 8, 8, 8, 7859.00),   -- Intercâmbio Alemanha (7200) + Hospedagem Londres 2 (420) + Assessoria passaporte (150) -> ajustado
(9, 9, 9, 9, 6200.00),   -- Pacote EUA (5300) + Hospedagem Barcelona (410) + Aluguel carro (840) -> ajustado
(10, 10, 10, 10, 8299.90), -- Intercâmbio Irlanda (6800) + Hospedagem Lisboa (310) + Chip Ásia (229.90) + Tour Itália (960) -> ajustado
(11, 11, 11, 11, 11380.00), -- Pacote Japão (9800) + Hospedagem NY (1250) + Guia privativo (1200) -> ajustado
(12, 12, 12, 12, 11070.00), -- Intercâmbio Austrália (9500) + Hospedagem Roma (480) + Pacote mergulho (890) -> ajustado
(1, 13, 13, 13, 3780.00),  -- Pacote Chile (2900) + Hospedagem Buenos Aires (280) + Assessoria intercâmbio (1990) -> ajustado
(2, 14, 14, 14, 10289.00), -- Intercâmbio Nova Zelândia (8700) + Hospedagem Barcelona 2 (590) + Traslado luxo (2500) -> ajustado
(6, 15, 15, 15, 5358.00),  -- Pacote México (4600) + Hospedagem New Orleans (370) + Chip América Sul (149.90) + Fotos (499) -> ajustado
(1, 16, 16, 16, 9279.00),  -- Intercâmbio Canadá Toronto (7800) + Hospedagem Zurique (780) + Equipamento inverno (300) + Assessoria câmbio (0) -> ajustado
(2, 17, 17, 17, 3349.90),  -- Pacote Uruguai (2700) + Hospedagem Paris 2 (920) + Chip família (349.90) -> ajustado (obs: diária alta, mas cliente único)
(8, 18, 18, 18, 8430.00),  -- Intercâmbio França Nice (7300) + Hospedagem Buenos Aires 2 (340) + Passeios ecológicos (750) -> ajustado
(4, 19, 19, 19, 7160.00),  -- Pacote Grécia (6100) + Hospedagem Montevidéu (310) + Sala VIP (550) -> ajustado
(5, 20, 20, 20, 8140.00),  -- Intercâmbio Holanda (7500) + Hospedagem Vancouver (430) + Passeios românticos (980) -> ajustado
(9, 21, 21, 21, 5109.90),  -- Pacote Canadá Montreal (4250) + Hospedagem Zaragoza (270) + Chip Europa (189.90) + Passeios (?) -> reuso produto
(10, 22, 22, 22, 6070.00),  -- Pacote Portugal (5200) + Hospedagem Montreal (390) + Ingressos rápidos (420) -> reuso produto
(1, 23, 23, 23, 7810.00),  -- Pacote França (6700) + Hospedagem São Paulo (410) + Assessoria pets (280) -> reuso produto
(2, 24, 24, 24, 4450.00),  -- Intercâmbio Argentina (3800) + Hospedagem Rio (350) + Sem serviço adicional (0) -> reuso produto
(6, 25, 25, 25, 8598.00);  -- Pacote Itália Roma (5900) + Hospedagem Tijuana (220) + Chip família (349.90) + Visto EUA (299) + Vários -> ajustado


TRUNCATE TABLE voo RESTART IDENTITY CASCADE;
INSERT INTO voo (pais_saida, cidade_saida, aeroporto_saida, dt_hr_saida, pais_destino, cidade_destino, aeroporto_destino, dt_hr_chegada, valor_passagem, id_companhia, qtd_passagens, obs, ida_volta, id_orcamento) VALUES
-- Orçamento 1: Brasil (São Paulo) -> Canadá (Montreal) / IDA
(31, 1076532519, 'GRU', '2025-06-10 22:00:00', 38, 1076532519, 'YUL', '2025-06-11 08:30:00', 3850.00, 1, 2, 'Voo direto com escala técnica em Toronto', 'Ida', 1),
-- Orçamento 1: Canadá (Montreal) -> Brasil (São Paulo) / VOLTA
(38, 1076532519, 'YUL', '2025-06-25 21:00:00', 31, 1076532519, 'GRU', '2025-06-26 09:00:00', 3850.00, 1, 2, 'Voo noturno com conexão em Toronto', 'Volta', 1),

-- Orçamento 2: Brasil (Rio de Janeiro) -> Argentina (Buenos Aires) / IDA
(31, 1076532519, 'GIG', '2025-07-05 10:00:00', 10, 1076532519, 'EZE', '2025-07-05 13:30:00', 1250.00, 1, 1, 'Voo direto. Duração 3h30', 'Ida', 2),
-- Orçamento 2: Argentina (Buenos Aires) -> Brasil (Rio de Janeiro) / VOLTA
(10, 1076532519, 'EZE', '2025-07-20 16:00:00', 31, 1076532519, 'GIG', '2025-07-20 19:30:00', 1250.00, 1, 1, 'Voo direto. Chegada noturna no Rio', 'Volta', 2),

-- Orçamento 3: Brasil (São Paulo) -> Portugal (Lisboa) / IDA
(31, 1076532519, 'GRU', '2025-08-01 18:00:00', 193, 1076532519, 'LIS', '2025-08-02 06:00:00', 4200.00, 1, 2, 'Voo direto TAP. Jantar a bordo', 'Ida', 3),
-- Orçamento 3: Portugal (Lisboa) -> Brasil (São Paulo) / VOLTA
(193, 1076532519, 'LIS', '2025-08-15 09:00:00', 31, 1076532519, 'GRU', '2025-08-15 17:00:00', 4200.00, 1, 2, 'Voo diurno com refeição', 'Volta', 3),

-- Orçamento 4: Brasil (São Paulo) -> Inglaterra (Londres) / IDA
(31, 1076532519, 'GRU', '2025-09-01 21:00:00', 227, 1076532519, 'LHR', '2025-09-02 11:30:00', 5500.00, 4, 1, 'Voo direto British Airways', 'Ida', 4),
-- Orçamento 4: Inglaterra (Londres) -> Brasil (São Paulo) / VOLTA
(227, 1076532519, 'LHR', '2025-09-20 20:00:00', 31, 1076532519, 'GRU', '2025-09-21 05:00:00', 5500.00, 4, 1, 'Voo red-eye com pernoite', 'Volta', 4),

-- Orçamento 5: Brasil (Rio de Janeiro) -> França (Paris) / IDA
(31, 1076532519, 'GIG', '2025-10-05 20:00:00', 74, 1076532519, 'CDG', '2025-10-06 10:30:00', 4800.00, 5, 2, 'Voo Air France. Refeição inclusa', 'Ida', 5),
-- Orçamento 5: França (Paris) -> Brasil (Rio de Janeiro) / VOLTA
(74, 1076532519, 'CDG', '2025-10-20 13:00:00', 31, 1076532519, 'GIG', '2025-10-20 20:00:00', 4800.00, 5, 2, 'Voo diurno com serviço de bordo', 'Volta', 5),

-- Orçamento 6: Brasil (São Paulo) -> Espanha (Madrid) / IDA
(31, 1076532519, 'GRU', '2025-11-10 16:00:00', 206, 1076532519, 'MAD', '2025-11-11 06:00:00', 3900.00, 12, 2, 'Voo direto Iberia', 'Ida', 6),
-- Orçamento 6: Espanha (Madrid) -> Brasil (São Paulo) / VOLTA
(206, 1076532519, 'MAD', '2025-11-25 10:00:00', 31, 1076532519, 'GRU', '2025-11-25 17:00:00', 3900.00, 12, 2, 'Voo com serviço de bordo', 'Volta', 6),

-- Orçamento 7: Brasil (São Paulo) -> Itália (Roma) / IDA
(31, 1076532519, 'GRU', '2025-12-01 18:30:00', 105, 1076532519, 'FCO', '2025-12-02 08:00:00', 4700.00, 13, 2, 'Voo Alitalia com conexão', 'Ida', 7),
-- Orçamento 7: Itália (Roma) -> Brasil (São Paulo) / VOLTA
(105, 1076532519, 'FCO', '2025-12-18 14:00:00', 31, 1076532519, 'GRU', '2025-12-18 22:00:00', 4700.00, 13, 2, 'Voo direto. Bagagem inclusa', 'Volta', 7),

-- Orçamento 8: Brasil (Rio de Janeiro) -> Alemanha (Berlim) / IDA
(31, 1076532519, 'GIG', '2026-01-15 21:00:00', 81, 1076532519, 'BER', '2026-01-16 12:00:00', 5200.00, 9, 1, 'Escala em Frankfurt. 1h30 de conexão', 'Ida', 8),
-- Orçamento 8: Alemanha (Berlim) -> Brasil (Rio de Janeiro) / VOLTA
(81, 1076532519, 'BER', '2026-01-30 10:00:00', 31, 1076532519, 'GIG', '2026-01-30 19:00:00', 5200.00, 9, 1, 'Voo diurno com conexão', 'Volta', 8),

-- Orçamento 9: Brasil (São Paulo) -> Estados Unidos (Orlando) / IDA
(31, 1076532519, 'GRU', '2026-02-10 23:00:00', 230, 1076532519, 'MCO', '2026-02-11 06:30:00', 2800.00, 3, 4, 'Voo noturno. Chegada pela manhã', 'Ida', 9),
-- Orçamento 9: Estados Unidos (Orlando) -> Brasil (São Paulo) / VOLTA
(230, 1076532519, 'MCO', '2026-02-25 20:00:00', 31, 1076532519, 'GRU', '2026-02-26 06:00:00', 2800.00, 3, 4, 'Voo red-eye. Lanche a bordo', 'Volta', 9),

-- Orçamento 10: Brasil (São Paulo) -> Irlanda (Dublin) / IDA
(31, 1076532519, 'GRU', '2026-03-05 20:00:00', 108, 1076532519, 'DUB', '2026-03-06 09:30:00', 5400.00, 4, 1, 'Escala em Londres. 2h de conexão', 'Ida', 10),
-- Orçamento 10: Irlanda (Dublin) -> Brasil (São Paulo) / VOLTA
(108, 1076532519, 'DUB', '2026-03-22 12:00:00', 31, 1076532519, 'GRU', '2026-03-22 21:00:00', 5400.00, 4, 1, 'Voo com escala no Reino Unido', 'Volta', 10),

-- Orçamento 11: Brasil (São Paulo) -> Japão (Tóquio) / IDA
(31, 1076532519, 'GRU', '2026-04-01 21:00:00', 112, 1076532519, 'NRT', '2026-04-03 05:00:00', 8200.00, 1, 2, 'Escala em Dubai. 3h de conexão', 'Ida', 11),
-- Orçamento 11: Japão (Tóquio) -> Brasil (São Paulo) / VOLTA
(112, 1076532519, 'NRT', '2026-04-20 22:00:00', 31, 1076532519, 'GRU', '2026-04-21 09:00:00', 8200.00, 1, 2, 'Voo longo com duas refeições', 'Volta', 11),

-- Orçamento 12: Brasil (Rio de Janeiro) -> Austrália (Sydney) / IDA
(31, 1076532519, 'GIG', '2026-05-05 23:00:00', 14, 1076532519, 'SYD', '2026-05-07 08:00:00', 7500.00, 6, 1, 'Conexões em Santiago e Auckland', 'Ida', 12),
-- Orçamento 12: Austrália (Sydney) -> Brasil (Rio de Janeiro) / VOLTA
(14, 1076532519, 'SYD', '2026-05-25 12:00:00', 31, 1076532519, 'GIG', '2026-05-26 18:00:00', 7500.00, 6, 1, 'Voo longo com escalas', 'Volta', 12),

-- Orçamento 13: Brasil (São Paulo) -> Chile (Santiago) / IDA
(31, 1076532519, 'GRU', '2026-06-10 08:00:00', 44, 1076532519, 'SCL', '2026-06-10 12:30:00', 1100.00, 1, 2, 'Voo direto LATAM. Café da manhã', 'Ida', 13),
-- Orçamento 13: Chile (Santiago) -> Brasil (São Paulo) / VOLTA
(44, 1076532519, 'SCL', '2026-06-25 15:00:00', 31, 1076532519, 'GRU', '2026-06-25 19:00:00', 1100.00, 1, 2, 'Voo direto. Lanche incluso', 'Volta', 13),

-- Orçamento 14: Brasil (São Paulo) -> Nova Zelândia (Auckland) / IDA
(31, 1076532519, 'GRU', '2026-07-05 20:00:00', 157, 1076532519, 'AKL', '2026-07-07 10:00:00', 7800.00, 6, 2, 'Escala em Sydney. 4h de conexão', 'Ida', 14),
-- Orçamento 14: Nova Zelândia (Auckland) -> Brasil (São Paulo) / VOLTA
(157, 1076532519, 'AKL', '2026-07-25 14:00:00', 31, 1076532519, 'GRU', '2026-07-26 20:00:00', 7800.00, 6, 2, 'Voo longo com serviço de bordo', 'Volta', 14),

-- Orçamento 15: Brasil (Rio de Janeiro) -> México (Cancún) / IDA
(31, 1076532519, 'GIG', '2026-08-10 10:00:00', 142, 1076532519, 'CUN', '2026-08-10 15:00:00', 2500.00, 1, 2, 'Conexão em São Paulo. 2h de escala', 'Ida', 15),
-- Orçamento 15: México (Cancún) -> Brasil (Rio de Janeiro) / VOLTA
(142, 1076532519, 'CUN', '2026-08-25 16:00:00', 31, 1076532519, 'GIG', '2026-08-25 23:00:00', 2500.00, 1, 2, 'Escala em SP. Lanche a bordo', 'Volta', 15),

-- Orçamento 16: Brasil (São Paulo) -> Canadá (Toronto) / IDA
(31, 1076532519, 'GRU', '2026-09-05 21:30:00', 38, 1076532519, 'YYZ', '2026-09-06 07:00:00', 4200.00, 11, 1, 'Voo direto Air Canada', 'Ida', 16),
-- Orçamento 16: Canadá (Toronto) -> Brasil (São Paulo) / VOLTA
(38, 1076532519, 'YYZ', '2026-09-22 22:00:00', 31, 1076532519, 'GRU', '2026-09-23 07:30:00', 4200.00, 11, 1, 'Voo noturno com pernoite', 'Volta', 16),

-- Orçamento 17: Brasil (São Paulo) -> Uruguai (Montevidéu) / IDA
(31, 1076532519, 'GRU', '2026-10-10 14:00:00', 231, 1076532519, 'MVD', '2026-10-10 16:30:00', 800.00, 1, 3, 'Voo direto. Duração 2h30', 'Ida', 17),
-- Orçamento 17: Uruguai (Montevidéu) -> Brasil (São Paulo) / VOLTA
(231, 1076532519, 'MVD', '2026-10-25 17:00:00', 31, 1076532519, 'GRU', '2026-10-25 19:00:00', 800.00, 1, 3, 'Voo direto. Lanche a bordo', 'Volta', 17),

-- Orçamento 18: Brasil (Rio de Janeiro) -> França (Nice) / IDA
(31, 1076532519, 'GIG', '2026-11-05 19:00:00', 74, 1076532519, 'NCE', '2026-11-06 09:30:00', 4900.00, 5, 1, 'Escala em Paris. 2h de conexão', 'Ida', 18),
-- Orçamento 18: França (Nice) -> Brasil (Rio de Janeiro) / VOLTA
(74, 1076532519, 'NCE', '2026-11-22 11:00:00', 31, 1076532519, 'GIG', '2026-11-22 20:00:00', 4900.00, 5, 1, 'Conexão em Paris. Refeição', 'Volta', 18),

-- Orçamento 19: Brasil (São Paulo) -> Grécia (Atenas) / IDA
(31, 1076532519, 'GRU', '2026-12-01 20:00:00', 85, 1076532519, 'ATH', '2026-12-02 12:30:00', 5100.00, 4, 2, 'Escala em Londres. 3h30 de conexão', 'Ida', 19),
-- Orçamento 19: Grécia (Atenas) -> Brasil (São Paulo) / VOLTA
(85, 1076532519, 'ATH', '2026-12-18 15:00:00', 31, 1076532519, 'GRU', '2026-12-19 06:00:00', 5100.00, 4, 2, 'Voo longo com escala', 'Volta', 19),

-- Orçamento 20: Brasil (São Paulo) -> Holanda (Amsterdã) / IDA
(31, 1076532519, 'GRU', '2027-01-10 22:00:00', 155, 1076532519, 'AMS', '2027-01-11 13:00:00', 4600.00, 14, 1, 'Voo direto KLM', 'Ida', 20),
-- Orçamento 20: Holanda (Amsterdã) -> Brasil (São Paulo) / VOLTA
(155, 1076532519, 'AMS', '2027-01-28 11:00:00', 31, 1076532519, 'GRU', '2027-01-28 19:00:00', 4600.00, 14, 1, 'Voo diurno. Refeição inclusa', 'Volta', 20),

-- Orçamento 21: Brasil (São Paulo) -> Peru (Cusco) / IDA
(31, 1076532519, 'GRU', '2027-02-10 08:00:00', 174, 1076532519, 'CUZ', '2027-02-10 14:30:00', 1600.00, 1, 2, 'Conexão em Lima. 2h de escala', 'Ida', 21),
-- Orçamento 21: Peru (Cusco) -> Brasil (São Paulo) / VOLTA
(174, 1076532519, 'CUZ', '2027-02-25 09:00:00', 31, 1076532519, 'GRU', '2027-02-25 16:00:00', 1600.00, 1, 2, 'Escala em Lima. Lanche', 'Volta', 21),

-- Orçamento 22: Brasil (Rio de Janeiro) -> África do Sul (Cidade do Cabo) / IDA
(31, 1076532519, 'GIG', '2027-03-15 19:00:00', 203, 1076532519, 'CPT', '2027-03-16 08:00:00', 5300.00, 1, 1, 'Conexão em Joanesburgo. 3h escala', 'Ida', 22),
-- Orçamento 22: África do Sul (Cidade do Cabo) -> Brasil (Rio de Janeiro) / VOLTA
(203, 1076532519, 'CPT', '2027-04-05 20:00:00', 31, 1076532519, 'GIG', '2027-04-06 07:00:00', 5300.00, 1, 1, 'Voo noturno com conexão', 'Volta', 22),

-- Orçamento 23: Brasil (São Paulo) -> Costa Rica (San José) / IDA
(31, 1076532519, 'GRU', '2027-05-05 10:00:00', 52, 1076532519, 'SJO', '2027-05-05 17:00:00', 2300.00, 1, 2, 'Conexão no Panamá. 1h30 escala', 'Ida', 23),
-- Orçamento 23: Costa Rica (San José) -> Brasil (São Paulo) / VOLTA
(52, 1076532519, 'SJO', '2027-05-20 14:00:00', 31, 1076532519, 'GRU', '2027-05-20 22:00:00', 2300.00, 1, 2, 'Escala no Panamá. Lanche', 'Volta', 23),

-- Orçamento 24: Brasil (Rio de Janeiro) -> Itália (Milão) / IDA
(31, 1076532519, 'GIG', '2027-06-10 18:00:00', 105, 1076532519, 'MXP', '2027-06-11 09:30:00', 4800.00, 13, 1, 'Voo direto com parada técnica', 'Ida', 24),
-- Orçamento 24: Itália (Milão) -> Brasil (Rio de Janeiro) / VOLTA
(105, 1076532519, 'MXP', '2027-06-28 12:00:00', 31, 1076532519, 'GIG', '2027-06-28 20:30:00', 4800.00, 13, 1, 'Voo diurno com refeição', 'Volta', 24),

-- Orçamento 25: Brasil (São Paulo) -> Emirados Árabes (Dubai) / IDA
(31, 1076532519, 'GRU', '2027-07-15 00:30:00', 226, 1076532519, 'DXB', '2027-07-15 20:00:00', 6100.00, 10, 2, 'Voo direto Emirates. Jantar a bordo', 'Ida', 25),
-- Orçamento 25: Emirados Árabes (Dubai) -> Brasil (São Paulo) / VOLTA
(226, 1076532519, 'DXB', '2027-08-05 08:00:00', 31, 1076532519, 'GRU', '2027-08-05 17:30:00', 6100.00, 10, 2, 'Voo diurno. Entretenimento a bordo', 'Volta', 25);

TRUNCATE TABLE vendas RESTART IDENTITY CASCADE;
INSERT INTO vendas (data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao, status_venda) VALUES
('2025-06-05', 1, 'Cartão de crédito', 4859.90, 1000.00, 5, 771.98, 242.99, 'Concluída'),
('2025-07-10', 2, 'PIX', 4630.00, 4630.00, 1, 0.00, 231.50, 'Concluída'),
('2025-08-15', 3, 'Boleto', 7550.00, 2265.00, 3, 1761.67, 377.50, 'Concluída'),
('2025-09-20', 4, 'Cartão de crédito', 9739.00, 2000.00, 6, 1289.83, 486.95, 'Concluída'),
('2025-10-25', 5, 'Cartão de débito', 7730.00, 7730.00, 1, 0.00, 386.50, 'Concluída'),
('2025-11-30', 6, 'Cartão de crédito', 5089.90, 1500.00, 4, 897.48, 254.50, 'Pendente'),
('2025-12-05', 7, 'PIX', 7190.00, 7190.00, 1, 0.00, 359.50, 'Concluída'),
('2026-01-10', 8, 'Boleto', 7859.00, 2357.70, 3, 1833.77, 392.95, 'Concluída'),
('2026-02-15', 9, 'Cartão de crédito', 6200.00, 1240.00, 5, 992.00, 310.00, 'Pendente'),
('2026-03-20', 10, 'Dinheiro', 8299.90, 8299.90, 1, 0.00, 414.99, 'Concluída'),
('2026-04-25', 11, 'Cartão de crédito', 11380.00, 2000.00, 8, 1172.50, 569.00, 'Concluída'),
('2026-05-30', 12, 'PIX', 11070.00, 11070.00, 1, 0.00, 553.50, 'Cancelada'),
('2026-06-05', 13, 'Cartão de débito', 3780.00, 3780.00, 1, 0.00, 189.00, 'Concluída'),
('2026-07-10', 14, 'Cartão de crédito', 10289.00, 3086.70, 4, 1800.58, 514.45, 'Pendente'),
('2026-08-15', 15, 'Boleto', 5358.00, 1607.40, 3, 1250.20, 267.90, 'Concluída'),
('2026-09-20', 16, 'PIX', 9279.00, 9279.00, 1, 0.00, 463.95, 'Concluída'),
('2026-10-25', 17, 'Cartão de crédito', 3349.90, 1000.00, 3, 783.30, 167.49, 'Cancelada'),
('2026-11-30', 18, 'Cartão de débito', 8430.00, 8430.00, 1, 0.00, 421.50, 'Concluída'),
('2026-12-05', 19, 'Cartão de crédito', 7160.00, 1432.00, 5, 1145.60, 358.00, 'Pendente'),
('2027-01-10', 20, 'Boleto', 8140.00, 2442.00, 3, 1899.33, 407.00, 'Concluída'),
('2027-02-15', 21, 'PIX', 5109.90, 5109.90, 1, 0.00, 255.50, 'Concluída'),
('2027-03-20', 22, 'Cartão de crédito', 6070.00, 1821.00, 4, 1062.25, 303.50, 'Pendente'),
('2027-04-25', 23, 'Dinheiro', 7810.00, 7810.00, 1, 0.00, 390.50, 'Concluída'),
('2027-05-30', 24, 'Cartão de crédito', 4450.00, 890.00, 5, 712.00, 222.50, 'Pendente'),
('2027-06-05', 25, 'PIX', 8598.00, 8598.00, 1, 0.00, 429.90, 'Concluída');
COMMIT;

SELECT * FROM vendas


