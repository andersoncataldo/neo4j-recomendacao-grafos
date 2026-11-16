# Neo4j: história e funcionamento (tópico 2)

Maior peso teórico do barema (2,0, junto com `01-paradigma-grafo.md`). Cada pergunta abaixo tem resposta explícita e verificada nas fontes oficiais em `../referencias.md`.

## Perguntas do barema

- [x] Por que foi desenvolvido?
- [x] Onde?
- [x] Quem?
- [x] Como opera?
- [x] Que hardware precisa?
- [x] Como implementa o paradigma de grafo?

## Quem, onde, por quê (verificado)

- **Quem:** **Emil Eifrem**, **Johan Svensson** e **Peter Neubauer**.
- **Onde e quando:** idealizado em **2000** (Eifrem esboçou o primeiro conceito em um guardanapo durante um voo para Mumbai) e desenvolvido em **Malmö, Suécia**. O código foi aberto e a empresa **Neo Technology** foi fundada em **2007** (atual **Neo4j, Inc.**, hoje sediada em San Mateo, Califórnia). A versão **1.0 GA** foi lançada em **fevereiro de 2010**. O sufixo **"4j"** vem de *"for Java"*, linguagem em que o motor foi construído.
- **Por quê:** construíam um sistema de gestão de conteúdo (CMS) corporativo e enfrentavam gargalos severos de desempenho e complexidade com `JOIN`s em bancos relacionais para dados altamente conectados; criaram então um motor nativo de grafo para tratar conexões como cidadãs de primeira classe.

## Como opera

- **Armazenamento nativo de grafo:** nós, relacionamentos e propriedades são gravados em arquivos de armazenamento separados (`neostore.nodestore.db`, `neostore.relationshipstore.db`, `neostore.propertystore.db`), usando registros de tamanho fixo para localização por offset direto em memória/disco.
- ***Index-free adjacency*** (adjacência sem índice): cada nó armazena ponteiros diretos para o primeiro relacionamento da sua lista duplamente encadeada, e cada relacionamento aponta diretamente para seu nó de origem e seu nó de destino. Ir de um nó ao vizinho é seguir um ponteiro físico em memória (**complexidade O(1) por salto**), cujo custo depende apenas do grau do nó visitado, não do tamanho total do banco. No relacional, cada `JOIN` exige busca em índice B-tree (O(log N) ou mais), degradando com o crescimento das tabelas.
- **Grafo de propriedades (LPG):** um nó possui 0 ou mais rótulos (`:Usuario`, `:Filme`) e propriedades chave-valor. Um relacionamento possui obrigatoriamente 1 tipo (`:ASSISTIU`), 1 direção, 1 nó de origem e 1 nó de destino, podendo carregar propriedades próprias (`nota: 5`). O modelo de `../banco/01-modelo-de-dados.md` ilustra isso diretamente.
- **Cypher e padrão ISO GQL:** linguagem declarativa criada pelo Neo4j em 2011 (aberta como *openCypher* em 2015) que expressa padrões graficamente em ASCII, como `(u:Usuario)-[:ASSISTIU]->(f:Filme)`. **Confirmado:** o Cypher serviu como principal base e inspiração (~95% de aderência de modelo e sintaxe de padrões) para a norma internacional **ISO/IEC 39075:2024 — GQL (Graph Query Language)**, publicada em abril de 2024 (a primeira nova linguagem de consulta de banco padronizada pela ISO desde o SQL).
- **Transações ACID:** garante Atomicidade, Consistência, Isolamento e Durabilidade completas, diferindo de muitos bancos NoSQL baseados apenas em consistência eventual (BASE).
- **Esquema flexível com restrições opcionais:** é *schema-optional* (aceita novos rótulos e propriedades em tempo de execução, como mostrado na consulta `U2`), mas permite impor restrições de unicidade, existência e índices. O `seed.cypher` define 4 restrições de unicidade (`usuario_id`, `filme_id`, `genero_nome`, `ator_nome`).
- **Distribuição em cluster** (edições Enterprise e AuraDB): arquitetura de servidores primários usando algoritmo de consenso **Raft** para escritas com consistência forte, combinados com réplicas secundárias assíncronas para escalar leituras. Leituras escalam horizontalmente; escritas passam pelo líder do Raft.
- **Teorema CAP:** conforme a Aula 11, o Neo4j é classificado como **CP** (Consistência + Tolerância a Partição) — em caso de partição sem quórum para o líder Raft, novas escritas são bloqueadas para preservar a consistência do grafo.

## Hardware (verificado em *Neo4j Operations Manual — System Requirements*)

- **Runtime:** executa sobre a **JVM** — requer **Java 17** no Neo4j 5.x (e **Java 21** nas versões recentes 5.14+ / 2025.x; distribuições OpenJDK, Oracle JDK, Eclipse Temurin ou Zulu).
- **Memória RAM (fator mais crítico):** dividida explicitamente em três faixas:
  1. **JVM Heap** (`server.memory.heap.initial_size` e `server.memory.heap.max_size`): armazena objetos em tempo de execução, planos de consulta e estado transacional. Boa prática oficial: definir `initial_size = max_size` para evitar pausas de redimensionamento do *Garbage Collector* e manter abaixo de **~31–32 GB** para preservar *Compressed Oops* na JVM.
  2. **Page Cache** off-heap (`server.memory.pagecache.size`): mantém em RAM os arquivos nativos de nós, relacionamentos e índices nativos para evitar I/O de disco. Idealmente deve cobrir o tamanho total do grafo ativo em disco.
  3. **Sistema Operacional:** reservar no mínimo **1 GB a 2 GB** de folga e desativar *swap* em servidores dedicados.
  - Ferramenta oficial de dimensionamento: `neo4j-admin server memory-recommendation`.
- **Armazenamento:** disco **SSD / NVMe** altamente recomendado, pois seguir ponteiros de adjacência fora do cache gera padrão de leitura aleatória (*random I/O*), onde HDDs mecânicos degradam drasticamente.
- **Porte:** ambiente de estudo/demo roda com folga em notebook comum com **8 GB de RAM**; ambientes de produção utilizam servidores com dezenas de GB de RAM e múltiplos núcleos para consultas concorrentes.

## Edições e ferramentas

- **Community Edition:** gratuita (licença GPLv3), servidor único (sem clustering nativo). Suficiente para o projeto e demo.
- **Enterprise Edition:** comercial, inclui clustering causal (Raft), backup a quente, controle de acesso baseado em papéis (RBAC) e múltiplos bancos.
- **AuraDB:** serviço gerenciado em nuvem (DBaaS), com plano **AuraDB Free** (pausa após 72 h sem escrita).
- **Ecossistema de ferramentas:** **Neo4j Browser** (console Cypher + visualização interativa), **Neo4j Bloom** (exploração visual para analistas), **Graph Data Science (GDS)** (algoritmos como PageRank, similaridade e detecção de comunidades) e **APOC** (biblioteca padrão de procedimentos utilitários).

## Diagrama obrigatório (slide 6)

Dois nós ligados por um relacionamento, mostrando os ponteiros físicos diretos (nó -> primeiro relacionamento -> nó vizinho, ou seja, *index-free adjacency*), lado a lado com duas tabelas relacionais conectadas por chave estrangeira e busca em índice (`JOIN`).

## Fontes

Neo4j Documentation (Operations Manual — System Requirements & Memory Configuration; Cypher Manual; AuraDB Docs) · *Graph Databases* (O'Reilly, 2015, cap. 6) · ISO/IEC 39075:2024 (GQL) · Aula 11. Detalhes completos em `../referencias.md`.
