# Projeto 3 NoSQL · Banco de Grafo (Neo4j) + Sistema de Recomendação

Pacote de planejamento para executar o trabalho. Cada arquivo trata de um assunto, para que quem executa (pessoa ou agente de IA) leia só o que precisa em cada etapa. Comece por aqui.

## Contexto

Trabalho em equipe da disciplina de Projeto de Banco de Dados da Unifor (26.2): Projeto 3 · NoSQL. Cada equipe recebeu por sorteio um paradigma NoSQL; o nosso é o 5, orientado a grafo. A apresentação é para a turma toda, dura até 30 min e inclui um CRUD ao vivo.

O enunciado completo está resumido em `00-enunciado-e-barema.md` e o conteúdo da aula de NoSQL em `01-aula-11.md`. Os PDFs originais estão em `fontes/`. Esta pasta é autossuficiente: não depende de nenhum outro arquivo.

## Objetivo

Apresentar em até 30 min o paradigma orientado a grafo, usando o **Neo4j** como SGBD e um **sistema de recomendação de filmes (estilo Netflix)** como exemplo, com CRUD ao vivo no Neo4j. O CRUD vale 5 dos 10 pontos, por isso o banco é o núcleo do trabalho.

## Decisões fechadas (não rediscutir)

| Item | Decisão | Por quê |
|---|---|---|
| Paradigma (sorteado) | 5 · Orientado a grafo | Sorteio |
| SGBD | Neo4j | Está na lista do PDF, é o exemplo da aula 11, é o banco de grafo mais usado, tem versão gratuita e interface visual boa para demo |
| Sistema do ponto 6 | b · Recomendação de filmes | Recomendar é percorrer relações, que é o forte do grafo. A própria aula cita recomendação como uso ideal do Neo4j |
| Linguagem | Cypher | Nativa do Neo4j |
| Como fazer o CRUD | Direto no Neo4j Browser, sem app próprio | O PDF aceita "interface do banco". App não soma ponto e aumenta o risco |
| Ambiente | Neo4j local no PC da apresentação + AuraDB Free na nuvem como reserva | O banco nasce de um script em segundos, então qualquer PC serve |

## Mapa dos arquivos

| Arquivo | Assunto |
|---|---|
| `00-enunciado-e-barema.md` | O que o PDF pede e quanto vale cada parte |
| `01-aula-11.md` | O que a professora ensinou sobre NoSQL e grafos (termos a usar e pontos de atenção) |
| `fontes/` | PDFs originais do enunciado e da aula 11 |
| **`banco/01-modelo-de-dados.md`** | Modelo de grafo, tipos, restrições e dataset |
| **`banco/02-ambiente.md`** | Subir o Neo4j local (Docker ou Desktop) e a reserva na nuvem |
| **`banco/03-seed-e-conferencia.md`** | Script que cria (e reseta) o banco + conferência |
| **`banco/04-consultas-e-crud.md`** | Todas as consultas e operações CRUD com resultado esperado |
| `pesquisa/01-paradigma-grafo.md` | Tópico 1 do PDF: o paradigma |
| `pesquisa/02-neo4j.md` | Tópico 2: história, funcionamento e hardware do Neo4j |
| `pesquisa/03-mercado-vantagens-desvantagens.md` | Tópicos 3, 4 e 5: quem usa, prós e contras |
| `pesquisa/04-recomendacao-com-grafo.md` | Tópico 6: Neo4j no contexto de recomendação |
| `apresentacao/01-slides.md` | Roteiro dos slides e perguntas prováveis |
| `apresentacao/02-demo.md` | Roteiro da demo ao vivo e plano B |
| `referencias.md` | Fontes |

## Ordem de execução

1. Ler `00-enunciado-e-barema.md` e `01-aula-11.md`.
2. **Banco:** `banco/01` → `banco/02` → `banco/03` → `banco/04`, conferindo cada resultado esperado.
3. **Pesquisa:** `pesquisa/01` a `04`, resolvendo todos os itens marcados **(conferir)**.
4. **Apresentação:** `apresentacao/01` (slides) e `apresentacao/02` (demo), depois ensaiar.

O banco vem antes da pesquisa porque vale metade da nota e porque os slides usam os exemplos dele.

## Entregáveis

```
db/
  seed.cypher                     # banco/03, cria e reseta o banco
  conferencia.cypher              # banco/03, contagens esperadas
  consultas/
    R0-visao-geral.cypher         # um arquivo por consulta de banco/04,
    R1-recomendacao-colaborativa.cypher   # nome = id da consulta
    R2-explicacao-caminho.cypher
    R3-recomendacao-conteudo.cypher
    R4-populares-cold-start.cypher
    C1-lancamento-duna.cypher
    U1-diego-muda-nota.cypher
    U2-ana-muda-plano.cypher
    D1a-delete-ingenuo.cypher
    D1b-detach-delete.cypher
slides (PowerPoint ou Google Slides, roteiro em apresentacao/01)
video-demo (gravação da demo, backup)
```

## Regras para quem executa

- **Os resultados esperados de `banco/04` são o teste de aceitação.** Se algum divergir, investigar o dado ou a consulta. Nunca ajustar o esperado só para bater.
- Usar os nomes de rótulos, relacionamentos, propriedades e ids exatamente como em `banco/01`.
- Não inventar fatos. Tudo que vai para slide precisa de fonte em `referencias.md`. Item marcado **(conferir)** só entra depois de confirmado.
- Não afirmar que Netflix ou Spotify usam Neo4j. Eles são só o exemplo de tipo de sistema do PDF.
- Não construir aplicação, API ou front-end. Está fora do escopo.
- Não ampliar o modelo (diretor, séries, amigos). Isso só aparece em slide, como extensão possível.

## Critério de pronto

- [ ] Seed + conferência batendo em todos os PCs que podem ser usados e na AuraDB *(Neo4j 5.26.0 local instalado, ativo e 100% validado via Bolt; falta apenas replicar na AuraDB reserva / outro PC da equipe)*
- [x] Todas as consultas de `banco/04` com resultado igual ao esperado *(validado via `scripts/test_aceitacao.py`)*
- [ ] Demo rodada 2 vezes seguidas, do reset ao fim, sem erro *(simulador interativo e scripts prontos para ensaio)*
- [x] Cada pergunta do barema respondida explicitamente em algum slide *(`apresentacao/Projeto3_NoSQL_Neo4j_Recomendacao.pptx` e `apresentacao/slides-interativos.html`)*
- [x] Nenhum **(conferir)** sem fonte *(todos os itens resolvidos com fontes em `referencias.md`)*
- [ ] Ensaio completo em até 25 min *(cronômetro integrado em `slides-interativos.html`)*
