// R1 · Recomendação colaborativa para a Ana (u01)
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
