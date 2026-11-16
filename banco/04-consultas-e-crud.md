# Consultas e CRUD

Todas as operações do trabalho, cada uma com id, objetivo e resultado esperado. Salvar cada uma em `db/consultas/<id>-<nome>.cypher`.

**Estado do banco:** os resultados esperados valem para quem rodou o seed (`banco/03`) e depois executou as escritas nesta ordem: C1 → U1 → U2 → D1b. Quando o resultado muda conforme o estado, a tabela mostra cada estado.

| Id | Letra | O que faz |
|---|---|---|
| R0 | R | Mostra o grafo inteiro |
| R1 | R | Recomendação colaborativa para a Ana (consulta principal) |
| R2 | R | Mostra o caminho que explica uma recomendação |
| R3 | R | Recomendação por conteúdo, com o motivo |
| R4 | R | Mais populares, para usuário sem histórico (cold start) |
| C1 | C | Lançamento: Duna entra no catálogo e é avaliado |
| U1 | U | Diego muda a nota de um filme (atualiza relacionamento) |
| U2 | U | Ana muda de plano (atualiza nó e cria campo novo) |
| D1a | D | Tentativa de apagar nó com relacionamentos (falha de propósito) |
| D1b | D | Apaga Duna com seus relacionamentos |

## Leitura (R)

### R0 · Visão geral

```cypher
MATCH (n) RETURN n;
```

Esperado: grafo com 39 nós e as ligações entre eles.

### R1 · Recomendação colaborativa para a Ana

Usuários parecidos = deram nota 4 ou mais aos mesmos filmes que a Ana avaliou com 4 ou mais. Recomenda o que eles avaliaram com 4 ou mais e a Ana ainda não viu. `forca` soma quantos filmes em comum cada recomendador tem com ela.

```cypher
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
```

Esperado por estado:

| Estado | recomendacao · usuariosParecidos · forca · notaMedia |
|---|---|
| Após seed | Interestelar · 2 · 3 · 4.5<br>O Lobo de Wall Street · 1 · 1 · 4.0 |
| Após C1 | Duna · 2 · 3 · 5.0<br>Interestelar · 2 · 3 · 4.5<br>O Lobo de Wall Street · 1 · 1 · 4.0 |
| Após U1 | Duna · 2 · 3 · 5.0<br>Interestelar · 2 · 3 · 4.5 |
| Após D1b | Interestelar · 2 · 3 · 4.5 |

Por que: Bruno tem 2 filmes em comum com a Ana (Matrix e A Origem) e Diego tem 1 (Matrix). Hugo não conta porque deu 3 para Matrix.

### R2 · Explicação do caminho

```cypher
MATCH p = (:Usuario {usuarioId:'u01'})-[r1:ASSISTIU]->(:Filme)<-[r2:ASSISTIU]-(:Usuario)-[r3:ASSISTIU]->(:Filme {filmeId:'f03'})
WHERE r1.nota >= 4 AND r2.nota >= 4 AND r3.nota >= 4
RETURN p;
```

Esperado (qualquer estado): 3 caminhos terminando em Interestelar: Ana, Matrix, Bruno · Ana, A Origem, Bruno · Ana, Matrix, Diego.

### R3 · Recomendação por conteúdo, com o motivo

Filmes que compartilham gênero ou ator com os que a Ana avaliou com 4 ou mais.

```cypher
MATCH (alvo:Usuario {usuarioId:'u01'})-[r:ASSISTIU]->(:Filme)-[:DO_GENERO|ATUOU_EM]-(x)-[:DO_GENERO|ATUOU_EM]-(rec:Filme)
WHERE r.nota >= 4 AND NOT EXISTS { (alvo)-[:ASSISTIU]->(rec) }
RETURN rec.titulo AS recomendacao,
       collect(DISTINCT x.nome) AS motivo,
       count(*) AS pontos
ORDER BY pontos DESC, recomendacao
LIMIT 5;
```

Esperado após seed (e de novo após D1b):

| recomendacao | motivo | pontos |
|---|---|---|
| Interestelar | [Ficção Científica] | 2 |
| O Lobo de Wall Street | [Leonardo DiCaprio] | 1 |
| Titanic | [Leonardo DiCaprio] | 1 |

Entre C1 e D1b, Duna aparece em primeiro, empatado com Interestelar: `Duna · [Ficção Científica] · 2`.

### R4 · Mais populares (cold start)

Para usuário novo, sem histórico, que a R1 não consegue atender.

```cypher
MATCH (:Usuario)-[r:ASSISTIU]->(f:Filme)
RETURN f.titulo AS filme, count(r) AS vezes, round(avg(r.nota), 1) AS notaMedia
ORDER BY vezes DESC, notaMedia DESC, filme
LIMIT 5;
```

Esperado após seed (e de novo após D1b): Matrix · 4 · 4.3 · Diário de uma Paixão · 3 · 4.7 · A Origem · 2 · 4.5 · Divertida Mente · 2 · 4.5 · Forrest Gump · 2 · 4.5.

## Criação (C)

### C1 · Lançamento de Duna

Novo filme ligado a um gênero existente, a um ator novo e a duas avaliações.

```cypher
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
```

Esperado: "Added 2 labels, created 2 nodes, set 7 properties, created 4 relationships".
Se rodar 2 vezes: erro da restrição `filme_id` e nada é duplicado (a transação inteira é desfeita). Bom para mostrar integridade se perguntarem.

## Atualização (U)

### U1 · Diego muda a nota de O Lobo de Wall Street

```cypher
MATCH (:Usuario {usuarioId:'u04'})-[r:ASSISTIU]->(f:Filme {filmeId:'f05'})
SET r.nota = 2
RETURN f.titulo AS filme, r.nota AS novaNota;
```

Esperado: "Set 1 property" e a linha `O Lobo de Wall Street · 2`. Efeito: O Lobo de Wall Street sai da R1 da Ana.

### U2 · Ana muda de plano

```cypher
MATCH (u:Usuario {usuarioId:'u01'})
SET u.plano = 'Premium', u.atualizadoEm = datetime()
RETURN u;
```

Esperado: "Set 2 properties" e o nó da Ana com `plano: Premium` e `atualizadoEm`. Ponto didático: `atualizadoEm` não existia em nenhum nó e entrou sem `ALTER TABLE`.

## Exclusão (D)

### D1a · Tentativa ingênua (falha de propósito)

```cypher
MATCH (f:Filme {filmeId:'f13'}) DELETE f;
```

Esperado: erro do tipo "Cannot delete node..., because it still has relationships". Ponto didático: o Neo4j não deixa relacionamento órfão.

### D1b · Forma certa

```cypher
MATCH (f:Filme {filmeId:'f13'}) DETACH DELETE f;
```

Esperado: "Deleted 1 node, deleted 4 relationships".
O ator Timothée Chalamet fica no banco sem filmes. Se quiser limpar: `MATCH (a:Ator {nome:'Timothée Chalamet'}) DELETE a;` funciona sem `DETACH` porque ele não tem mais relacionamentos.

## Comparação com SQL (para o slide 11)

A R1 em SQL, supondo tabelas `filme` e `assistiu(usuario_id, filme_id, nota)`:

```sql
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
```

Mensagem: 3 JOINs da mesma tabela. Cada salto a mais no grafo é mais um JOIN no relacional.
