// C1 · Lançamento de Duna (Create)
// Esperado: "Added 2 labels, created 2 nodes, set 7 properties, created 4 relationships"
// Se rodar 2 vezes: erro da restrição filme_id e nada é duplicado (ACID).
MATCH (g:Genero {nome:'Ficção Científica'}),
      (bruno:Usuario {usuarioId:'u02'}),
      (diego:Usuario {usuarioId:'u04'})
CREATE (f:Filme {filmeId:'f13', titulo:'Duna', ano:2021, duracaoMin:155})
CREATE (f)-[:DO_GENERO]->(g)
MERGE (a:Ator {nome:'Timothée Chalamet'})
CREATE (a)-[:ATUOU_EM]->(f)
CREATE (bruno)-[:ASSISTIU {nota:5}]->(f),
       (diego)-[:ASSISTIU {nota:5}]->(f)
RETURN f, g, a, bruno, diego;
