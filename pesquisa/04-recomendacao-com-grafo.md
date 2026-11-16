# Neo4j num sistema de recomendação (tópico 6)

Vale 1,0. O barema pede vantagens e desvantagens nesse contexto e uma explicação detalhada de como o banco se adequa. Usar o nosso banco (`../banco/`) como exemplo concreto em tudo.

Mensagem central: **recomendar é percorrer relações, e o banco de grafo guarda as relações prontas para percorrer.**

## Como funciona (slide 11)

- **Filtragem colaborativa** = travessia de 3 saltos: `Ana -ASSISTIU-> Matrix <-ASSISTIU- Bruno -ASSISTIU-> Interestelar`. "Quem gostou do que você gostou também gostou de..." É a consulta R1.
- **Baseada em conteúdo** = travessia por características: `Ana -ASSISTIU-> A Origem <-ATUOU_EM- DiCaprio -ATUOU_EM-> Titanic`. É a consulta R3.
- **Híbrida** = soma dos dois sinais. Algoritmos da Graph Data Science (similaridade entre nós, PageRank para popularidade) refinam o ranking.
- Comparar R1 em Cypher com o SQL equivalente (fim de `../banco/04-consultas-e-crud.md`).

## Vantagens no contexto (slide 12)

- **Tempo real:** a consulta só toca a vizinhança do usuário, então dá para recalcular a cada clique, sem processamento noturno.
- **Explicável:** o caminho é a justificativa ("porque você assistiu Matrix"). É a consulta R2.
- **Novidade entra na hora:** filme lançado e assistido já aparece nas recomendações. A demo prova isso com C1 seguida de R1.
- **Sinal novo sem migração:** seguir amigo, adicionar à lista, ator favorito entram como novos relacionamentos.
- **Caso real confirmado:** o **Walmart** (inclusive sua operação de e-commerce) adotou o Neo4j para recomendações de produtos em tempo real ("quem comprou também comprou"), substituindo processos batch em bancos relacionais que não conseguiam acompanhar o comportamento em tempo real dos compradores.

## Desvantagens no contexto (slide 12)

- **Volume de eventos:** uma plataforma do porte da Netflix gera bilhões de "plays". Gravar cada evento no grafo pesa. O normal é guardar o log bruto em outro banco (Cassandra, Kafka) e levar ao grafo só a relação resumida (assistiu, nota).
- **Supernós:** filmes muito populares e gêneros amplos ligam em quase todo mundo. É preciso filtrar ou limitar.
- **Partida a frio (cold start):** usuário novo, sem relações, não recebe recomendação colaborativa. Saída: recomendar por popularidade (consulta R4).
- **Machine learning pesado fica fora:** fatoração de matrizes e redes neurais rodam fora do banco. O Neo4j complementa, não substitui.
- **Arquitetura poliglota:** grafo para relações, relacional ou documento para catálogo e cobrança.

## Como o Neo4j se adequa (frase de fechamento do slide)

Os dados de recomendação são uma rede de usuários, filmes, gêneros e atores. O Neo4j guarda essa rede do jeito que ela é e responde "o que recomendar para este usuário" percorrendo poucos saltos, em milissegundos, com a explicação junto.
