// R4 · Mais populares (cold start para usuário sem histórico)
MATCH (:Usuario)-[r:ASSISTIU]->(f:Filme)
RETURN f.titulo AS filme, count(r) AS vezes, round(avg(r.nota), 1) AS notaMedia
ORDER BY vezes DESC, notaMedia DESC, filme
LIMIT 5;
