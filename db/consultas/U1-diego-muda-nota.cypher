// U1 · Diego muda a nota de O Lobo de Wall Street (Update em relacionamento)
// Esperado: "Set 1 property" -> O Lobo de Wall Street | 2
MATCH (:Usuario {usuarioId:'u04'})-[r:ASSISTIU]->(f:Filme {filmeId:'f05'})
SET r.nota = 2
RETURN f.titulo AS filme, r.nota AS novaNota;
