// D1a · Tentativa ingênua de apagar nó com relacionamentos (falha proposital)
// Esperado: erro "Cannot delete node..., because it still has relationships"
MATCH (f:Filme {filmeId:'f13'}) DELETE f;
