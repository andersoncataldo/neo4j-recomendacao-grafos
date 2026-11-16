-- Equivalente SQL da consulta R1 (Recomendação colaborativa para a Ana 'u01')
-- Supondo tabelas: filme(filme_id, titulo) e assistiu(usuario_id, filme_id, nota)
-- Mensagem didática: 3 JOINs da mesma tabela. Cada salto a mais no grafo vira mais um JOIN no relacional.

SELECT f.titulo,
       COUNT(DISTINCT a2.usuario_id) AS usuarios_parecidos
FROM assistiu a1
JOIN assistiu a2 ON a2.filme_id = a1.filme_id
                AND a2.usuario_id <> a1.usuario_id
JOIN assistiu a3 ON a3.usuario_id = a2.usuario_id
JOIN filme f     ON f.filme_id = a3.filme_id
WHERE a1.usuario_id = 'u01'
  AND a1.nota >= 4 AND a2.nota >= 4 AND a3.nota >= 4
  AND a3.filme_id NOT IN (SELECT filme_id FROM assistiu WHERE usuario_id = 'u01')
GROUP BY f.titulo
ORDER BY usuarios_parecidos DESC;
