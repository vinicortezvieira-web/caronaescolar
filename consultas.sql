-- Consultas de exemplo do CaronaEscolar

-- 1) Viagens com vagas livres (JOIN de 3 tabelas + contagem)
SELECT v.id, v.tipo, u.nome AS motorista, e.nome AS escola, v.horario,
       v.vagas - COUNT(r.id) AS livres
FROM viagens v
JOIN usuarios u ON u.id = v.motorista_id
JOIN escolas e ON e.id = v.escola_id
LEFT JOIN reservas r ON r.viagem_id = v.id
GROUP BY v.id
ORDER BY v.horario;

-- 2) Reservas de um passageiro (troque o 1 pelo id do passageiro)
SELECT r.id, v.tipo, v.origem, v.horario, e.nome AS escola
FROM reservas r
JOIN viagens v ON v.id = r.viagem_id
JOIN escolas e ON e.id = v.escola_id
WHERE r.passageiro_id = 1;

-- 3) Passageiros de cada viagem de um motorista
SELECT v.id, v.origem, GROUP_CONCAT(p.nome, ', ') AS passageiros
FROM viagens v
LEFT JOIN reservas r ON r.viagem_id = v.id
LEFT JOIN usuarios p ON p.id = r.passageiro_id
WHERE v.motorista_id = 1
GROUP BY v.id;

-- 4) Escola com mais viagens
SELECT e.nome, COUNT(v.id) AS total
FROM escolas e LEFT JOIN viagens v ON v.escola_id = e.id
GROUP BY e.id ORDER BY total DESC;

-- 5) Cancelar uma reserva
DELETE FROM reservas WHERE id = 1 AND passageiro_id = 1;

-- 6) Atualizar o número de vagas de uma viagem
UPDATE viagens SET vagas = 5 WHERE id = 1;
