# Seed e conferência

O seed apaga tudo e recria o banco do zero. Serve para a carga inicial e como reset antes de cada ensaio e da apresentação. Pode rodar quantas vezes quiser.

Salvar como `db/seed.cypher`.

## Seed

```cypher
// 0 · Limpa o banco (use só no banco da demo)
MATCH (n) DETACH DELETE n;

// 1 · Restrições: id único (também cria índice para busca rápida)
CREATE CONSTRAINT usuario_id IF NOT EXISTS FOR (u:Usuario) REQUIRE u.usuarioId IS UNIQUE;
CREATE CONSTRAINT filme_id IF NOT EXISTS FOR (f:Filme) REQUIRE f.filmeId IS UNIQUE;
CREATE CONSTRAINT genero_nome IF NOT EXISTS FOR (g:Genero) REQUIRE g.nome IS UNIQUE;
CREATE CONSTRAINT ator_nome IF NOT EXISTS FOR (a:Ator) REQUIRE a.nome IS UNIQUE;

// 2 · Filmes, gêneros e atores
UNWIND [
  {id:'f01', titulo:'Matrix', ano:1999, duracao:136, generos:['Ficção Científica','Ação'], atores:['Keanu Reeves','Carrie-Anne Moss']},
  {id:'f02', titulo:'John Wick', ano:2014, duracao:101, generos:['Ação'], atores:['Keanu Reeves']},
  {id:'f03', titulo:'Interestelar', ano:2014, duracao:169, generos:['Ficção Científica','Drama'], atores:['Matthew McConaughey','Anne Hathaway']},
  {id:'f04', titulo:'A Origem', ano:2010, duracao:148, generos:['Ficção Científica','Ação'], atores:['Leonardo DiCaprio']},
  {id:'f05', titulo:'O Lobo de Wall Street', ano:2013, duracao:180, generos:['Comédia','Drama'], atores:['Leonardo DiCaprio','Margot Robbie']},
  {id:'f06', titulo:'Titanic', ano:1997, duracao:195, generos:['Romance','Drama'], atores:['Leonardo DiCaprio','Kate Winslet']},
  {id:'f07', titulo:'Diário de uma Paixão', ano:2004, duracao:123, generos:['Romance','Drama'], atores:['Ryan Gosling','Rachel McAdams']},
  {id:'f08', titulo:'La La Land', ano:2016, duracao:128, generos:['Romance','Musical'], atores:['Ryan Gosling','Emma Stone']},
  {id:'f09', titulo:'Barbie', ano:2023, duracao:114, generos:['Comédia'], atores:['Margot Robbie','Ryan Gosling']},
  {id:'f10', titulo:'Toy Story', ano:1995, duracao:81, generos:['Animação','Comédia'], atores:['Tom Hanks']},
  {id:'f11', titulo:'Forrest Gump', ano:1994, duracao:142, generos:['Drama','Romance'], atores:['Tom Hanks']},
  {id:'f12', titulo:'Divertida Mente', ano:2015, duracao:95, generos:['Animação','Comédia'], atores:['Amy Poehler']}
] AS row
MERGE (f:Filme {filmeId: row.id})
SET f.titulo = row.titulo, f.ano = row.ano, f.duracaoMin = row.duracao
FOREACH (nomeGenero IN row.generos |
  MERGE (g:Genero {nome: nomeGenero})
  MERGE (f)-[:DO_GENERO]->(g))
FOREACH (nomeAtor IN row.atores |
  MERGE (a:Ator {nome: nomeAtor})
  MERGE (a)-[:ATUOU_EM]->(f));

// 3 · Usuários
UNWIND [
  {id:'u01', nome:'Ana',    plano:'Padrão'},
  {id:'u02', nome:'Bruno',  plano:'Padrão'},
  {id:'u03', nome:'Carla',  plano:'Básico'},
  {id:'u04', nome:'Diego',  plano:'Premium'},
  {id:'u05', nome:'Elisa',  plano:'Padrão'},
  {id:'u06', nome:'Felipe', plano:'Básico'},
  {id:'u07', nome:'Gabi',   plano:'Premium'},
  {id:'u08', nome:'Hugo',   plano:'Padrão'}
] AS row
MERGE (u:Usuario {usuarioId: row.id})
SET u.nome = row.nome, u.plano = row.plano;

// 4 · Quem assistiu o quê (nota de 1 a 5)
UNWIND [
  ['u01','f01',5], ['u01','f02',4], ['u01','f04',5],
  ['u02','f01',5], ['u02','f04',4], ['u02','f03',5], ['u02','f02',3],
  ['u03','f06',5], ['u03','f07',5], ['u03','f08',4],
  ['u04','f01',4], ['u04','f03',4], ['u04','f05',4],
  ['u05','f07',4], ['u05','f08',5], ['u05','f09',4],
  ['u06','f10',5], ['u06','f12',5], ['u06','f09',3],
  ['u07','f06',4], ['u07','f11',5], ['u07','f07',5],
  ['u08','f10',4], ['u08','f11',4], ['u08','f12',4], ['u08','f01',3]
] AS row
MATCH (u:Usuario {usuarioId: row[0]}), (f:Filme {filmeId: row[1]})
MERGE (u)-[r:ASSISTIU]->(f)
SET r.nota = row[2];
```

## Conferência

Salvar como `db/conferencia.cypher`. Rodar logo depois do seed.

```cypher
MATCH (n) RETURN labels(n)[0] AS tipo, count(*) AS total ORDER BY tipo;
```

Esperado: Ator 12 · Filme 12 · Genero 7 · Usuario 8.

```cypher
MATCH ()-[r]->() RETURN type(r) AS relacionamento, count(*) AS total ORDER BY relacionamento;
```

Esperado: ASSISTIU 26 · ATUOU_EM 19 · DO_GENERO 22.

```cypher
SHOW CONSTRAINTS;
```

Esperado: 4 restrições (`usuario_id`, `filme_id`, `genero_nome`, `ator_nome`).

Se algum número não bater, rodar o seed de novo antes de qualquer outra coisa.
