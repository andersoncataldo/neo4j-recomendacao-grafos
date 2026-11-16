# Mercado, vantagens e desvantagens (tópicos 3, 4 e 5)

Vantagens valem 1,0 e desvantagens 1,0. Aplicações reais não têm peso próprio, mas são obrigatórias.

## Aplicações reais (tópico 3 — casos confirmados em neo4j.com/customers)

| Empresa | Uso do Neo4j (confirmado) |
|---|---|
| **Walmart** | Recomendação de produtos em tempo real no e-commerce ("quem comprou também comprou"), substituindo lotes relacionais lentos por travessia instantânea entre clientes e produtos |
| **eBay** | Grafo de conhecimento para comércio conversacional (ShopBot / Google Assistant) e roteamento inteligente de entregas e contexto de compra |
| **NASA** | Base de conhecimento *Lessons Learned* conectando décadas de relatórios técnicos e competências de engenheiros (usado no planejamento da Missão a Marte) |
| **ICIJ** | Investigações jornalísticas globais (*Panama Papers*, *Paradise Papers* e *Pandora Papers*), mapeando redes de empresas offshore, políticos e intermediários |
| **Lyft** | Motor do catálogo de descoberta e linhagem de dados **Amundsen**, conectando datasets, tabelas e usuários com algoritmos de relevância (PageRank) |
| **Adobe** | Rede criativa **Behance** (+18 milhões de usuários): feed de atividades e grafo de conexões em tempo real, substituindo fan-out custoso e reduzindo infraestrutura |

**Regra importante:** não afirmar que Netflix ou Spotify usam Neo4j. Eles são apenas exemplos de tipo de sistema do enunciado do trabalho.

## Vantagens (tópico 4)

- [x] Consultas de relacionamento rápidas e estáveis mesmo com muitos saltos (*index-free adjacency* + benchmark de `01-paradigma-grafo.md`).
- [x] Modelo natural (*whiteboard-friendly*): o que se desenha no quadro é o que se grava.
- [x] Esquema flexível (*schema-optional*): novo tipo de nó, relacionamento ou propriedade entra sem `ALTER TABLE` nem migração bloqueante (a demo mostra isso na `U2`).
- [x] Linguagem Cypher legível e expressiva por padrões visuais (comparar com o SQL equivalente com 3 `JOIN`s no fim de `../banco/04-consultas-e-crud.md`).
- [x] Transações ACID completas e restrições de integridade (a demo mostra na `D1a` que relacionamentos órfãos são impedidos e na `C1` que restrições garantem unicidade).
- [x] Ecossistema maduro: Neo4j Browser visual, Bloom, Graph Data Science (GDS), drivers oficiais (Java, Python, JavaScript, .NET, Go), edição Community gratuita e nuvem AuraDB.

## Desvantagens (tópico 5)

- [x] Escrita não escala horizontalmente com facilidade: escritas passam pelo líder do cluster (consenso Raft) e particionar (*sharding*) um único grafo conectado entre servidores sem quebrar travessias não é automático como no Cassandra. **Nuance para a aula (slide 30):** leitura escala horizontalmente por réplicas, mas escrita centraliza no líder.
- [x] Pouco eficaz para dados tabulares simples e agregações analíticas em massa (somas e médias sobre bilhões de linhas): bancos relacionais ou colunares (como Cassandra/ClickHouse) são superiores (reforça o slide 31 da aula).
- [x] Supernós (*supernodes*): nós com milhões de relacionamentos (ex.: um gênero "Drama" num catálogo gigante) viram gargalos de travessia e exigem modelagem específica.
- [x] Alto consumo de RAM para máxima performance: idealmente o *page cache* deve comportar o grafo ativo em memória.
- [x] Recursos avançados de produção (clustering causal, backup a quente, RBAC avançado) são exclusivos da edição Enterprise paga (ou AuraDB gerenciada).
- [x] Curva de aprendizado (pensar em grafos + Cypher) e menor oferta de profissionais no mercado em comparação com SQL tradicional.
- [x] Não é indicado para armazenar objetos binários grandes (vídeos, imagens) nem logs brutos de eventos em alta vazão.
