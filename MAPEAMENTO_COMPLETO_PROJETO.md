# Mapeamento Completo do Projeto 3 · NoSQL (Orientado a Grafo — Neo4j)

Documento consolidado com todos os requisitos do enunciado, alinhamento conceitual com a Aula 11, arquitetura técnica do Neo4j, mapeamento de algoritmos/consultas Cypher e guia completo da execução prática.

---

## 1. Enquadramento Disciplinar e Barema (10,0 pontos)

- **Disciplina:** Projeto de Banco de Dados — Unifor (26.2)
- **Paradigma sorteado:** 5 · **Orientado a Grafo (*Graph Store*)**
- **SGBD escolhido:** **Neo4j** (Community Edition / AuraDB Free) + Linguagem **Cypher**
- **Sistema do Tópico 6:** **b · Sistemas de recomendação (estilo Netflix/Spotify)** — implementado como catálogo e recomendador de filmes

| Critério do Barema | Peso | Cobertura nos Entregáveis |
|---|---|---|
| Descrição e características do paradigma e do Neo4j (por quê, onde, quem, como opera, hardware, implementação do paradigma) | **2,0** | Slides 2–7 · `pesquisa/01-paradigma-grafo.md`, `pesquisa/02-neo4j.md` |
| Aplicações reais no mercado (obrigatório) | — | Slide 8 · `pesquisa/03-mercado-vantagens-desvantagens.md` |
| Principais vantagens (motivos para usar) | **1,0** | Slide 9 · `pesquisa/03-mercado-vantagens-desvantagens.md` |
| Principais desvantagens (motivos para evitar) | **1,0** | Slide 10 · `pesquisa/03-mercado-vantagens-desvantagens.md` |
| Vantagens, desvantagens e adequação detalhada no sistema de recomendação | **1,0** | Slides 11–12 · `pesquisa/04-recomendacao-com-grafo.md` |
| Aplicação prática ao vivo (CRUD completo: Create, Read, Update, Delete) | **5,0** | Slides 13–14 · `db/` · `apresentacao/02-demo.md` |

---

## 2. Conexão Direta com os Conceitos da Aula 11

| Conceito da Aula 11 | Aplicação no Nosso Projeto |
|---|---|
| **Definição de Marko Rodriguez (Slide 29)** | Grafo como estrutura de vértices (`:Usuario`, `:Filme`, `:Genero`, `:Ator`) conectados por arestas multirrelacionais (`:ASSISTIU`, `:DO_GENERO`, `:ATUOU_EM`). |
| **Modelo *Whiteboard-Friendly* (Slide 29)** | O diagrama desenhado no quadro (e em `apresentacao/modelo-arrows.json`) é exatamente o esquema físico gravado no Neo4j, sem tabelas intermediárias N:N. |
| **Esquema flexível / *On the fly* (Slides 18, 19, 30)** | Demonstrado ao vivo na operação **U2**: o atributo `atualizadoEm` é adicionado somente no nó da usuária Ana sem `ALTER TABLE` nem migração. |
| **Transações ACID (Slide 17 e 19)** | Diferente de bancos BASE, o Neo4j garante Atomicidade, Consistência, Isolamento e Durabilidade. Demonstrado ao vivo em **C1** duplicado (rollback pela constraint `filme_id`) e **D1a** (bloqueio de aresta órfã). |
| **Teorema CAP (Slides 10–16, 31, 32)** | O Neo4j é classificado como **CP** (Consistência + Tolerância a Partição): em cluster (Enterprise/Aura), escritas passam pelo líder via consenso Raft; sem maioria em partição, escritas param para proteger a consistência. |
| **Escalabilidade Horizontal × Vertical & Sharding (Slides 4–9, 30)** | Nuance fundamental: o slide 30 generaliza que grafos escalam horizontalmente. No Neo4j, **leituras** escalam horizontalmente com réplicas assíncronas, mas **escritas** passam pelo líder Raft e não há *sharding* automático do grafo como no Cassandra (principal desvantagem). |

---

## 3. Arquitetura e Fundamentos Técnicos do Neo4j

- **Origem (Quem, Onde, Por quê):** Idealizado em **2000** por **Emil Eifrem, Johan Svensson e Peter Neubauer** (em **Malmö, Suécia**) durante o desenvolvimento de um CMS que sofria gargalos com múltiplos `JOIN`s em banco relacional. Empresa **Neo Technology** fundada em **2007** (hoje Neo4j, Inc., San Mateo/CA); versão **1.0 GA em fevereiro de 2010**. `"4j"` = *for Java*.
- **Armazenamento Nativo e *Index-Free Adjacency*:** Nós, relacionamentos e propriedades ficam em arquivos separados de tamanho fixo. Cada nó mantém ponteiros diretos para sua lista duplamente encadeada de relacionamentos, e cada relacionamento aponta para origem e destino. Cada salto custa **O(1)** (depende só do grau do nó, não do tamanho total do banco).
- **Benchmark (*Neo4j in Action*, cap. 1 — 1 milhão de pessoas):**
  - Profundidade 2: MySQL `0,016 s` vs Neo4j `0,010 s`
  - Profundidade 3: MySQL `30,267 s` vs Neo4j `0,168 s`
  - Profundidade 4: MySQL `1.543,505 s` vs Neo4j `1,359 s`
  - Profundidade 5: MySQL `timeout (> 1 h)` vs Neo4j `2,132 s`
- **Linguagem Cypher & ISO GQL:** Padrões visuais em ASCII `(u:Usuario)-[:ASSISTIU]->(f:Filme)`. Criada em 2011 e aberta como openCypher em 2015, foi a base direta para o padrão internacional **ISO/IEC 39075:2024 (GQL)**, o primeiro padrão ISO de linguagem de banco desde o SQL.
- **Hardware (*Operations Manual*):** Executa sobre JVM (**Java 17** no Neo4j 5; **Java 21** em versões 2025.x). Dimensões críticas: **JVM Heap** (`initial_size = max_size`, abaixo de ~31–32 GB para *Compressed Oops*), **Page Cache** off-heap (`server.memory.pagecache.size` cobrindo o grafo ativo em RAM), **SSD/NVMe** (por leitura aleatória de ponteiros) e dimensionamento via `neo4j-admin server memory-recommendation`.

---

## 4. Casos Reais no Mercado e Adequação à Recomendação

- **Casos confirmados (`neo4j.com/customers`):**
  1. **Walmart:** recomendação de produtos em tempo real no e-commerce ("quem comprou também comprou").
  2. **eBay:** assistente conversacional de compras e roteamento inteligente com grafo de conhecimento.
  3. **NASA:** grafo de conhecimento *Lessons Learned* conectando décadas de missões (usado no planejamento para Marte).
  4. **ICIJ:** investigações *Panama Papers*, *Paradise Papers* e *Pandora Papers*.
  5. **Lyft (Amundsen):** catálogo de descoberta e linhagem de dados com PageRank.
  6. **Adobe (Behance):** feed de atividades para +18 milhões de usuários criativos.
- **Aviso explícito:** Netflix e Spotify são apenas os exemplos do enunciado para o *tipo de sistema*; não afirmamos que utilizam Neo4j.
- **Por que Neo4j funciona bem em recomendação:**
  - **Filtragem Colaborativa (`R1`):** travessia de 3 saltos em tempo real (`Ana -> Filme <- Outro -> FilmeRec`).
  - **Filtragem Baseada em Conteúdo (`R3`):** travessia por gênero e ator (`[:DO_GENERO|ATUOU_EM]`).
  - **Explicabilidade nativa (`R2`):** o próprio caminho `p` retornado é a justificativa da recomendação.
  - **Partida a frio (*Cold Start* — `R4`):** fallback para popularidade quando usuário ainda não tem arestas `:ASSISTIU`.
  - **Limites no contexto:** logs massivos de *play/pause* devem ficar em banco colunar/streaming (Kafka/Cassandra), levando ao grafo apenas interações consolidadas; supernós (gêneros muito amplos) exigem cuidado; ML pesado (redes neurais/fatoração de matrizes) roda fora do banco.

---

## 5. Mapa dos Arquivos Executáveis e Ferramentas Criadas

- **Scripts Cypher & SQL (`db/`):**
  - [db/seed.cypher](db/seed.cypher) — Limpa, cria 4 constraints UNIQUE, popula 39 nós (`8 Usuario`, `12 Filme`, `7 Genero`, `12 Ator`) e 67 relacionamentos (`26 ASSISTIU`, `22 DO_GENERO`, `19 ATUOU_EM`).
  - [db/conferencia.cypher](db/conferencia.cypher) — Valida contagens e restrições.
  - [db/consultas/](db/consultas/) — Consultas individuais `R0`, `R1`, `R2`, `R3`, `R4`, `C1`, `U1`, `U2`, `D1a`, `D1b`, [DBA-indices-e-profile.cypher](db/consultas/DBA-indices-e-profile.cypher) (`SHOW CONSTRAINTS`, `SHOW INDEXES`, `PROFILE` da `R1`) e [SQL-comparativo-R1.sql](db/consultas/SQL-comparativo-R1.sql).
  - [db/roteiro-demo-completa.cypher](db/roteiro-demo-completa.cypher) — Script mestre comentado na ordem exata dos 12 passos da apresentação.
- **Automação, Verificação e Testes (`scripts/`):**
  - [scripts/verificar_projeto.py](scripts/verificar_projeto.py) — Motor de Grafo de Propriedades em memória que lê `db/seed.cypher` e valida todo o ciclo CRUD, com suporte a Neo4j real via `--bolt` e reset de emergência via `--bolt ... --reset-only`.
  - [scripts/test_aceitacao.py](scripts/test_aceitacao.py) — Suíte `pytest` com os testes de aceitação do banco, restrições, transições de estado, equivalência SQL e integração real via Bolt.
  - [scripts/iniciar_neo4j.ps1](scripts/iniciar_neo4j.ps1) / [scripts/parar_neo4j.ps1](scripts/parar_neo4j.ps1) / [scripts/setup_neo4j_local.ps1](scripts/setup_neo4j_local.ps1) — Scripts PowerShell para subir, diagnosticar e encerrar o Neo4j 5 local ou em container Docker.
  - [scripts/gerar_slides_pptx.py](scripts/gerar_slides_pptx.py) — Gerador automatizado do deck `.pptx`.
- **Apresentação e Diagramas (`apresentacao/`):**
  - [apresentacao/modelo-arrows.json](apresentacao/modelo-arrows.json) — Arquivo importável diretamente no `arrows.app`.
  - [apresentacao/slides-interativos.html](apresentacao/slides-interativos.html) — Slides completos em HTML com diagramas SVG, notas do apresentador e **Simulador Interativo do Neo4j Browser** integrado no Slide 14.
  - [apresentacao/Projeto3_NoSQL_Neo4j_Recomendacao.pptx](apresentacao/Projeto3_NoSQL_Neo4j_Recomendacao.pptx) — Apresentação PowerPoint pronta para exibição.
