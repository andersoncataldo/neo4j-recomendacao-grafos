// Conferência de nós: esperado Ator 12 · Filme 12 · Genero 7 · Usuario 8
MATCH (n) RETURN labels(n)[0] AS tipo, count(*) AS total ORDER BY tipo;

// Conferência de relacionamentos: esperado ASSISTIU 26 · ATUOU_EM 19 · DO_GENERO 22
MATCH ()-[r]->() RETURN type(r) AS relacionamento, count(*) AS total ORDER BY relacionamento;

// Conferência de restrições: esperado 4 restrições (usuario_id, filme_id, genero_nome, ator_nome)
SHOW CONSTRAINTS;
