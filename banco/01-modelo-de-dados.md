# Modelo de dados

Grafo de uma plataforma de streaming de filmes: usuários assistem e avaliam filmes; filmes têm gêneros e atores. É o mínimo que permite recomendar de dois jeitos: colaborativo (usuários parecidos) e por conteúdo (gênero e ator em comum).

## Diagrama

```
(:Usuario {usuarioId, nome, plano})
        |
        | [:ASSISTIU {nota: 1 a 5}]
        v
(:Filme {filmeId, titulo, ano, duracaoMin}) --[:DO_GENERO]--> (:Genero {nome})
        ^
        | [:ATUOU_EM]
        |
(:Ator {nome})
```

Para o slide, redesenhar em https://arrows.app (ferramenta gratuita do Neo4j para diagramas de grafo).

## Elementos

| Elemento | Tipo | Propriedades | Restrição |
|---|---|---|---|
| `:Usuario` | nó | `usuarioId` (string, ex.: `'u01'`) · `nome` (string) · `plano` (string: `Básico`, `Padrão`, `Premium`) | `usuarioId` único |
| `:Filme` | nó | `filmeId` (string, ex.: `'f01'`) · `titulo` (string) · `ano` (inteiro) · `duracaoMin` (inteiro) | `filmeId` único |
| `:Genero` | nó | `nome` (string) | `nome` único |
| `:Ator` | nó | `nome` (string) | `nome` único |
| `:ASSISTIU` | relacionamento `Usuario → Filme` | `nota` (inteiro de 1 a 5) | no máximo 1 por par usuário e filme (garantido pelo `MERGE` do seed) |
| `:DO_GENERO` | relacionamento `Filme → Genero` | nenhuma | |
| `:ATUOU_EM` | relacionamento `Ator → Filme` | nenhuma | |

## Decisões de modelagem

- **Assistir e avaliar numa relação só** (`ASSISTIU` com `nota`): menos elementos na tela, e a nota é exatamente o que a recomendação usa.
- **Nota no relacionamento, não no nó:** a nota pertence ao par usuário e filme. É o exemplo direto de uma vantagem do grafo de propriedades (relacionamento com propriedade).
- **Gênero e ator como nós, não como lista dentro do filme:** assim viram caminhos que a recomendação por conteúdo percorre.
- **Ids curtos em string** (`u01`, `f01`): fáceis de ler em voz alta na demo.
- **Dataset pequeno e montado à mão:** resultado de cada consulta previsível (vira teste de aceitação) e grafo legível na tela. Os gostos foram desenhados para a usuária da demo, Ana, ter recomendações claras.
- **Fora do escopo:** diretor, séries, data e hora de cada play, seguir amigos. Podem ser citados no slide como extensão que entra sem migração de esquema.

## Volume

8 usuários, 12 filmes, 7 gêneros e 12 atores (39 nós). 67 relacionamentos: 26 `ASSISTIU`, 22 `DO_GENERO`, 19 `ATUOU_EM`.

## Usuários

| Id | Nome | Plano | Assistiu (nota) | Perfil |
|---|---|---|---|---|
| u01 | Ana | Padrão | Matrix 5, John Wick 4, A Origem 5 | ficção e ação · **usuária da demo** |
| u02 | Bruno | Padrão | Matrix 5, A Origem 4, Interestelar 5, John Wick 3 | ficção e ação |
| u03 | Carla | Básico | Titanic 5, Diário de uma Paixão 5, La La Land 4 | romance |
| u04 | Diego | Premium | Matrix 4, Interestelar 4, O Lobo de Wall Street 4 | ficção e drama |
| u05 | Elisa | Padrão | Diário de uma Paixão 4, La La Land 5, Barbie 4 | romance e comédia |
| u06 | Felipe | Básico | Toy Story 5, Divertida Mente 5, Barbie 3 | animação |
| u07 | Gabi | Premium | Titanic 4, Forrest Gump 5, Diário de uma Paixão 5 | romance e drama |
| u08 | Hugo | Padrão | Toy Story 4, Forrest Gump 4, Divertida Mente 4, Matrix 3 | animação e drama |

## Filmes

| Id | Título | Ano | Min | Gêneros | Atores |
|---|---|---|---|---|---|
| f01 | Matrix | 1999 | 136 | Ficção Científica, Ação | Keanu Reeves, Carrie-Anne Moss |
| f02 | John Wick | 2014 | 101 | Ação | Keanu Reeves |
| f03 | Interestelar | 2014 | 169 | Ficção Científica, Drama | Matthew McConaughey, Anne Hathaway |
| f04 | A Origem | 2010 | 148 | Ficção Científica, Ação | Leonardo DiCaprio |
| f05 | O Lobo de Wall Street | 2013 | 180 | Comédia, Drama | Leonardo DiCaprio, Margot Robbie |
| f06 | Titanic | 1997 | 195 | Romance, Drama | Leonardo DiCaprio, Kate Winslet |
| f07 | Diário de uma Paixão | 2004 | 123 | Romance, Drama | Ryan Gosling, Rachel McAdams |
| f08 | La La Land | 2016 | 128 | Romance, Musical | Ryan Gosling, Emma Stone |
| f09 | Barbie | 2023 | 114 | Comédia | Margot Robbie, Ryan Gosling |
| f10 | Toy Story | 1995 | 81 | Animação, Comédia | Tom Hanks |
| f11 | Forrest Gump | 1994 | 142 | Drama, Romance | Tom Hanks |
| f12 | Divertida Mente | 2015 | 95 | Animação, Comédia | Amy Poehler |

**Entra só na demo** (consulta C1 de `banco/04`): f13 · Duna · 2021 · 155 min · Ficção Científica · Timothée Chalamet.
