// U2 · Ana muda de plano e ganha propriedade nova sem ALTER TABLE (Update em nó)
// Esperado: "Set 2 properties" -> plano: Premium, atualizadoEm: <datetime>
MATCH (u:Usuario {usuarioId:'u01'})
SET u.plano = 'Premium', u.atualizadoEm = datetime()
RETURN u;
