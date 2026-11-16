# Roteiro dos slides

25 min planejados, 5 de folga dentro do limite de 30.

| # | Slide | Conteúdo | Min | Base |
|---|---|---|---|---|
| 1 | Capa | Tema, equipe, disciplina, professora | 0,5 | · |
| 2 | O paradigma de grafo | Nós, arestas, propriedades, rótulos · grafo de propriedades × RDF · banco × processamento (Giraph) | 2 | `pesquisa/01` |
| 3 | Relacional × grafo | JOIN na consulta × relação gravada · tabela do benchmark | 1,5 | `pesquisa/01` |
| 4 | Onde se usa grafo | Aplicações típicas, 1 exemplo cada | 1 | `pesquisa/01` |
| 5 | Neo4j: quem, onde, por quê | Linha do tempo: 2000 protótipo · 2007 empresa · 2010 versão 1.0 · hoje | 1,5 | `pesquisa/02` |
| 6 | Neo4j: como opera | Armazenamento nativo, index-free adjacency (diagrama), Cypher, ACID, cluster com Raft, CAP = CP | 2 | `pesquisa/02` |
| 7 | Neo4j: hardware e edições | JVM, RAM (heap + page cache), SSD · Community × Enterprise × Aura | 1 | `pesquisa/02` |
| 8 | Quem usa | 4 a 6 casos reais, 1 linha cada | 1 | `pesquisa/03` |
| 9 | Vantagens | 6 itens | 1,5 | `pesquisa/03` |
| 10 | Desvantagens | 6 itens | 1,5 | `pesquisa/03` |
| 11 | Recomendação = percorrer relações | Colaborativa e por conteúdo desenhadas como caminhos · R1 em Cypher × SQL | 2 | `pesquisa/04`, `banco/04` |
| 12 | Neo4j na recomendação: prós e contras | Duas colunas + frase de fechamento | 2 | `pesquisa/04` |
| 13 | Nosso modelo | Diagrama (arrows.app) + números do dataset | 1 | `banco/01` |
| 14 | Demo ao vivo | Trocar para o Browser | 6 | `apresentacao/02` |
| 15 | Conclusão + referências | 1 frase de conclusão + fontes | 0,5 | `referencias.md` |

Conclusão sugerida: "Grafo não substitui o relacional. É a escolha certa quando o valor está nas relações, e recomendação é exatamente isso."

## Perguntas prováveis da professora

| Pergunta | Resposta curta |
|---|---|
| Por que não usar relacional com uma tabela "assistiu"? | Dá, mas cada salto vira JOIN. Recomendação em tempo real com 3 ou mais saltos fica cara. Mostrar slide 3 (benchmark) e o SQL do slide 11 |
| O Neo4j escala horizontalmente? | Leitura sim (réplicas). Escrita passa pelo líder e não há sharding automático de um grafo como no Cassandra. É a principal desvantagem |
| O que é index-free adjacency? | Cada nó aponta direto para seus relacionamentos. Cada salto custa o mesmo, não importa o tamanho do banco |
| Onde o Neo4j fica no CAP? | CP, como na aula: no cluster, sem maioria para eleger líder, a escrita para. Prioriza consistência |
| É ACID? | Sim, transações ACID completas |
| Como evitaram duplicidade? | Restrições de unicidade (`SHOW CONSTRAINTS`; rodar C1 duas vezes dá erro) |
| E usuário novo, sem histórico? | Partida a frio: recomendar por popularidade (consulta R4) |
| A Netflix usa Neo4j? | Não afirmamos isso. Netflix é o exemplo de tipo de sistema do PDF. Caso real de recomendação com Neo4j: Walmart |
