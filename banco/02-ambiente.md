# Ambiente

O banco inteiro nasce do script de `banco/03-seed-e-conferencia.md` em segundos. Por isso qualquer PC com Neo4j serve para a apresentação. Preparar o ambiente em todo PC que puder ser usado (o de quem executa e o do Luis) e manter a AuraDB na nuvem como reserva.

## Requisitos

- Neo4j 5.x ou mais novo. A edição Community (gratuita) basta.
- Navegador.
- 8 GB de RAM sobram para este dataset.

## Opção A · Docker (se o PC já tem Docker)

```bash
docker run -d --name neo4j-demo -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/senhaDemo123 neo4j:5
```

- Abrir http://localhost:7474 e conectar com usuário `neo4j` e senha `senhaDemo123`.
- Parar: `docker stop neo4j-demo`. Subir de novo: `docker start neo4j-demo`.

## Opção B · Neo4j Desktop (sem Docker)

1. Baixar em https://neo4j.com/download e instalar.
2. Criar uma instância local (5.x ou mais nova), definir e anotar a senha.
3. Iniciar e abrir o Neo4j Browser (ou a ferramenta Query).

## Reserva · AuraDB Free (nuvem)

1. Criar conta em https://console.neo4j.io e uma instância AuraDB Free.
2. Baixar ou anotar a senha gerada (aparece uma vez só).
3. Rodar o seed também lá.
4. **Regra atual da AuraDB Free (confirmada na documentação oficial do Neo4j Aura):** a instância gratuita pausa automaticamente após **72 horas (3 dias)** contínuos sem operações de escrita/alteração (consultas apenas de leitura não contam como atividade). Os dados ficam preservados durante a pausa, mas se permanecer pausada por **30 dias** sem ser retomada, a instância é excluída permanentemente. **Recomendação:** retomar no console (`https://console.neo4j.io`) e rodar um comando de escrita (ou o seed) na véspera da apresentação.

## Ajustes no Browser

- Se der erro ao rodar vários comandos de uma vez, rodar o script bloco por bloco (cada bloco termina em `;`).
- Salvar as consultas da demo como favoritos (estrela), na ordem de `apresentacao/02-demo.md`.
- Na apresentação, zoom em uns 150% para a turma ler.

## Pronto quando

- [ ] Browser conecta no banco local de cada PC que pode ser usado
- [ ] Seed + conferência batendo (`banco/03`)
- [ ] AuraDB criada e com o seed rodado
