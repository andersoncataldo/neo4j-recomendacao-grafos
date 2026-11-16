// D1b · Forma certa de apagar Duna junto com seus relacionamentos (Delete)
// Esperado: "Deleted 1 node, deleted 4 relationships"
MATCH (f:Filme {filmeId:'f13'}) DETACH DELETE f;

// Limpeza opcional: Timothée Chalamet fica no banco sem filmes após o DETACH DELETE acima.
// Como não tem mais relacionamentos, DELETE simples funciona sem DETACH:
// MATCH (a:Ator {nome:'Timothée Chalamet'}) DELETE a;

