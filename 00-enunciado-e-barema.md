# Enunciado e barema

Resumo completo do enunciado. PDF original em `fontes/26.2 - Projeto 3 - NoSQL.pdf`.

## Contexto

- Universidade de Fortaleza (Unifor), disciplina de Projeto de Banco de Dados, semestre 26.2.
- Trabalho em equipe, apresentado para a turma toda. Presença obrigatória em todas as apresentações, apresentando ou assistindo.
- Segundo o PDF, vale "a terceira da nota da disciplina" (provavelmente a AV3).

## Tema

O PDF define banco NoSQL como um SGBD cujo armazenamento e recuperação seguem um paradigma diferente do relacional. Esses bancos são cada vez mais usados em Big Data, machine learning, IoT e web moderna, e o sucesso deles depende da natureza do problema.

O professor sorteou um paradigma por equipe, entre 7:

1. Orientado a coluna: Apache Cassandra, HBase, ScyllaDB
2. Orientado a documento: MongoDB, CouchDB, RethinkDB, Amazon DocumentDB
3. Cache de chave-valor: Memcached, Redis
4. Armazenamento de chave-valor: Couchbase, Redis, Amazon DynamoDB
5. **Orientado a grafo: AllegroGraph, Apache Giraph, Neo4j, JanusGraph, Amazon Neptune** ← nosso sorteio (escolhemos o Neo4j)
6. Armazenamento de tuplas: Apache River, GigaSpaces
7. Banco de objetos: Perst, ZoDB

## O que apresentar (mínimo)

1. Descrição e características do paradigma e principais tipos de aplicação (redes sociais etc.)
2. Visão geral do SGBD escolhido
3. Aplicações reais que usam o SGBD no mercado
4. Principais vantagens (motivos para usar)
5. Principais desvantagens (motivos para evitar)
6. Escolher um destes sistemas que pode ser construído com o banco sorteado e explicar vantagens e desvantagens de usá-lo nesse contexto:
    - a. Redes sociais (Facebook, X)
    - **b. Sistemas de recomendação (Netflix, Spotify)** ← nossa escolha
    - c. Chat em tempo real (WhatsApp, Slack)

## Aplicação prática

Escolher um conjunto de dados do sistema escolhido (estrutura e dados) e, pela interface do banco ou por uma aplicação, fazer um CRUD: uma inserção, uma atualização, uma "alteração" e uma exclusão. Tudo ao vivo, durante a apresentação.

## Barema

| Critério | Pontos | Onde está |
|---|---|---|
| Descrição e características do banco: por que foi desenvolvido, onde, quem, como opera, que hardware precisa, paradigma em detalhe e como o banco o implementa | 2,0 | `pesquisa/01`, `pesquisa/02` |
| Vantagens | 1,0 | `pesquisa/03` |
| Desvantagens | 1,0 | `pesquisa/03` |
| Vantagens e desvantagens no contexto do sistema escolhido, explicando como o banco se adequa | 1,0 | `pesquisa/04` |
| Aplicação prática (CRUD) | **5,0** | `banco/` e `apresentacao/02` |
| **Total** | **10,0** | |

Aplicações reais (tópico 3) não têm peso próprio no barema, mas são obrigatórias na apresentação.

## Regras

- Apresentação de até 30 min. Planejado: 25 min + 5 de folga.
- O CRUD é feito ao vivo.
- "Inserção, atualização, alteração e exclusão" provavelmente tem um erro de digitação no lugar de "consulta". O plano cobre qualquer leitura: 1 inserção, 2 atualizações (uma em relacionamento, uma em nó), várias consultas e 1 exclusão.
