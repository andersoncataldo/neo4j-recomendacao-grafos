# Roteiro da demo ao vivo (6 min · vale 5,0)

As consultas e os resultados esperados estão em `../banco/04-consultas-e-crud.md`, pelo id. Aqui fica só a ordem, o que mostrar e o que falar.

**Regra de ouro:** rodar só pelos favoritos salvos no Browser. Nunca digitar ao vivo.

## Antes de começar (no PC da apresentação)

- [ ] Neo4j iniciado e Browser conectado
- [ ] Rodar o seed (reset) e a conferência (`../banco/03`)
- [ ] Favoritos salvos na ordem abaixo
- [ ] Zoom do Browser em uns 150%
- [ ] AuraDB aberta em outra aba, já conectada (reserva)
- [ ] Vídeo da demo à mão (último recurso)

## Passo a passo

| # | Id | Mostrar | Fala |
|---|---|---|---|
| 1 | R0 | Grafo inteiro (39 nós) | "Cada bolinha é um nó, cada seta é um relacionamento. Não tem tabela nem chave estrangeira." |
| 2 | R1 | Interestelar e O Lobo de Wall Street | "Bruno e Diego gostaram dos mesmos filmes que a Ana. O que eles gostaram e ela ainda não viu vira recomendação." |
| 3 | R2 | 3 caminhos até Interestelar | "O caminho é a justificativa da recomendação." |
| 4 | C1 | Duna criado e ligado | "Lançamento: filme novo, ligado a gênero, ator e duas avaliações." |
| 5 | R1 | Duna em primeiro | "O filme acabou de entrar e já é a primeira recomendação. Sem reprocessar nada." |
| 6 | U1 | Nota de Diego vira 2 | "Diego mudou de opinião sobre O Lobo de Wall Street." |
| 7 | R1 | O Lobo de Wall Street sumiu | "A opinião de um usuário parecido mudou e a recomendação da Ana mudou na hora." |
| 8 | U2 | Ana Premium com `atualizadoEm` | "`atualizadoEm` não existia em nenhum nó. No relacional seria um ALTER TABLE." |
| 9 | D1a | Erro | "O Neo4j não deixa relacionamento órfão." |
| 10 | D1b | Duna apagado com 4 relacionamentos | "Com DETACH DELETE, o nó sai junto com as ligações." |
| 11 | R1 | Só Interestelar | "Duna saiu do catálogo e da recomendação." |
| 12 | R3 | Recomendação por conteúdo com motivo (extra, se sobrar tempo) | "Outro jeito de recomendar: por gênero e ator em comum." |

Cobertura do CRUD: C (passo 4), R (passos 1, 2, 3, 5, 7, 11, 12), U (passos 6 e 8), D (passos 9 e 10).

## Plano B

| Problema | O que fazer |
|---|---|
| PC da apresentação falha ou não conecta no projetor | Abrir a AuraDB em outro computador; o seed recria tudo em segundos |
| Sem internet | Nada muda: o ambiente principal é local |
| Neo4j local não inicia | AuraDB. Se também falhar, vídeo gravado |
| Passo rodado 2 vezes ou fora de ordem | Rodar o seed (reset) e recomeçar do passo 2 |
| AuraDB pausada | Retomar no console (leva alguns minutos): por isso retomar na véspera |
| Estourou o tempo | Pular os passos 3 e 12 (extras). C, R, U e D ficam |

## Preparação

- [ ] Gravar um vídeo da demo completa (backup)
- [ ] Ensaiar a demo 2 vezes seguidas, do reset ao passo 11, sem erro
