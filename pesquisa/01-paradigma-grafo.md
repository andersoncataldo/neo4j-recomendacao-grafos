# Paradigma orientado a grafo (tópico 1)

Vale junto com `02-neo4j.md` o bloco de 2,0 pontos. Usar os termos da aula 11 (nós, arestas, CAP) para falar a língua da professora. Todos os itens abaixo foram verificados nas fontes citadas em `../referencias.md`.

## O slide precisa responder

- [x] O que é: nós (vértices), relacionamentos (arestas), propriedades (chave-valor nos dois), rótulos (tipo do nó).
- [x] Os dois modelos: **grafo de propriedades rotulado (Labeled Property Graph — LPG)** (Neo4j, JanusGraph, Amazon Neptune) — onde nós e arestas armazenam pares chave-valor e rótulos/tipos — e **RDF / triplas** (`sujeito – predicado – objeto`, padrão W3C/SPARQL, usado por AllegroGraph e também suportado pelo Amazon Neptune), focado em web semântica e ontologias.
- [x] Banco de grafo (transacional/OLTP, consulta em tempo real, ex.: Neo4j) × motor de processamento de grafo (análise em lote/OLAP distribuída, ex.: Apache Giraph, baseado no Pregel do Google). O enunciado lista o Giraph junto com o Neo4j; diferenciar os dois mostra domínio do ecossistema.
- [x] Por que grafo e não relacional: no relacional a relação é calculada em tempo de execução por `JOIN`s entre chaves estrangeiras; no grafo ela já está persistida fisicamente como dado (ponteiro direto).
- [x] Aplicações típicas: redes sociais, sistemas de recomendação, detecção de fraude em tempo real, grafos de conhecimento (*knowledge graphs*), gestão de redes e TI, logística e rotas, controle de acesso (IAM).

## Ponto de partida

- Definição da aula 11 (Marko Rodriguez): "estrutura de dados que conecta um conjunto de vértices através de um conjunto de arestas". Modelo *whiteboard friendly*: o que se desenha no quadro é exatamente o que se grava no banco.
- Exemplo "amigos de amigos": em SQL cada nível de profundidade exige um novo *self-JOIN*; no grafo basta estender o padrão do caminho em Cypher: `(a)-[:AMIGO*1..3]->(b)`.
- **Benchmark confirmado** (VUKOTIC et al., *Neo4j in Action*, cap. 1, 2014; citado também em *Graph Databases*, O'Reilly): rede social simulada com **1 milhão de pessoas** (média de ~50 amigos por pessoa), buscando amigos até a profundidade *N*:

| Profundidade | MySQL (s) | Neo4j (s) | Observação |
|---|---|---|---|
| 2 | 0,016 | 0,010 | Ambos instantâneos |
| 3 | 30,267 | 0,168 | ~180× mais rápido no Neo4j |
| 4 | 1.543,505 (~25,7 min) | 1,359 | Explosão combinatória dos `JOIN`s no SQL |
| 5 | Não terminou em 1 h (timeout) | 2,132 | Custo cresce conforme a vizinhança explorada, não o total de linhas |

## Fontes

Aula 11 (slides 29 a 32) · *Graph Databases* (Robinson, Webber & Eifrem, O'Reilly, 2015, cap. 1 e 2) · *Neo4j in Action* (Vukotic et al., Manning, 2014, cap. 1). Detalhes completos em `../referencias.md`.
