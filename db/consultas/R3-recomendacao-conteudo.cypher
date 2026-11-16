// R3 · Recomendação por conteúdo, com o motivo
MATCH (alvo:Usuario {usuarioId:'u01'})-[r:ASSISTIU]->(:Filme)-[:DO_GENERO|ATUOU_EM]-(x)-[:DO_GENERO|ATUOU_EM]-(rec:Filme)
WHERE r.nota >= 4 AND NOT EXISTS { (alvo)-[:ASSISTIU]->(rec) }
RETURN rec.titulo AS recomendacao,
       collect(DISTINCT x.nome) AS motivo,
       count(*) AS pontos
ORDER BY pontos DESC, recomendacao
LIMIT 5;
