// DBA · Inspeção de restrições, índices e plano de execução (PROFILE)
// Demonstra como o Neo4j combina busca inicial por índice UNIQUE (NodeUniqueIndexSeek)
// com travessia por ponteiros diretos (Expand(All) / index-free adjacency).

// 1. Restrições de unicidade ativas
SHOW CONSTRAINTS;

// 2. Índices criados automaticamente pelas restrições e lookup de rótulos
SHOW INDEXES;

// 3. Plano de execução real com métricas de db hits da consulta R1
PROFILE
MATCH (alvo:Usuario {usuarioId:'u01'})-[r1:ASSISTIU]->(f:Filme)<-[r2:ASSISTIU]-(outro:Usuario)
WHERE r1.nota >= 4 AND r2.nota >= 4
WITH alvo, outro, count(f) AS emComum
MATCH (outro)-[r3:ASSISTIU]->(rec:Filme)
WHERE r3.nota >= 4 AND NOT EXISTS { (alvo)-[:ASSISTIU]->(rec) }
RETURN rec.titulo AS recomendacao,
       count(DISTINCT outro) AS usuariosParecidos,
       sum(emComum) AS forca,
       round(avg(r3.nota), 1) AS notaMedia
ORDER BY forca DESC, notaMedia DESC, recomendacao
LIMIT 5;
