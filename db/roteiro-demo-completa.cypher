// ============================================================================
// ROTEIRO MESTRE DA DEMO AO VIVO (Neo4j Browser - Executar bloco a bloco)
// Ordem oficial de apresentacao/02-demo.md
// ============================================================================

// [Passo 1 · R0] Grafo inteiro (39 nós e 67 relacionamentos)
MATCH (n) RETURN n;

// [Passo 2 · R1] Recomendação colaborativa para a Ana (após seed: Interestelar, O Lobo de Wall Street)
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

// [Passo 3 · R2] Explicação do caminho (3 caminhos até Interestelar)
MATCH p = (:Usuario {usuarioId:'u01'})-[r1:ASSISTIU]->(:Filme)<-[r2:ASSISTIU]-(:Usuario)-[r3:ASSISTIU]->(:Filme {filmeId:'f03'})
WHERE r1.nota >= 4 AND r2.nota >= 4 AND r3.nota >= 4
RETURN p;

// [Passo 4 · C1] Lançamento de Duna (Create)
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

// [Passo 5 · R1] Duna em primeiro lugar (sem reprocessar nada)
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

// [Passo 6 · U1] Diego muda nota de O Lobo de Wall Street para 2 (Update em relacionamento)
MATCH (:Usuario {usuarioId:'u04'})-[r:ASSISTIU]->(f:Filme {filmeId:'f05'})
SET r.nota = 2
RETURN f.titulo AS filme, r.nota AS novaNota;

// [Passo 7 · R1] O Lobo de Wall Street sumiu das recomendações da Ana
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

// [Passo 8 · U2] Ana muda de plano para Premium e cria campo atualizadoEm (Update em nó / schema-optional)
MATCH (u:Usuario {usuarioId:'u01'})
SET u.plano = 'Premium', u.atualizadoEm = datetime()
RETURN u;

// [Passo 9 · D1a] Tentativa ingênua de apagar Duna (falha proposital: não deixa relacionamento órfão)
MATCH (f:Filme {filmeId:'f13'}) DELETE f;

// [Passo 10 · D1b] DETACH DELETE remove Duna e suas 4 ligações (Delete)
MATCH (f:Filme {filmeId:'f13'}) DETACH DELETE f;

// [Passo 11 · R1] Só Interestelar resta nas recomendações
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

// [Passo 12 · R3] Extra: Recomendação por conteúdo (gênero e ator em comum)
MATCH (alvo:Usuario {usuarioId:'u01'})-[r:ASSISTIU]->(:Filme)-[:DO_GENERO|ATUOU_EM]-(x)-[:DO_GENERO|ATUOU_EM]-(rec:Filme)
WHERE r.nota >= 4 AND NOT EXISTS { (alvo)-[:ASSISTIU]->(rec) }
RETURN rec.titulo AS recomendacao,
       collect(DISTINCT x.nome) AS motivo,
       count(*) AS pontos
ORDER BY pontos DESC, recomendacao
LIMIT 5;

// [Extra · R4] Mais populares (Cold Start para usuário sem histórico)
MATCH (:Usuario)-[r:ASSISTIU]->(f:Filme)
RETURN f.titulo AS filme, count(r) AS vezes, round(avg(r.nota), 1) AS notaMedia
ORDER BY vezes DESC, notaMedia DESC, filme
LIMIT 5;
