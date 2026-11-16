// R2 · Explicação do caminho até Interestelar (f03)
MATCH p = (:Usuario {usuarioId:'u01'})-[r1:ASSISTIU]->(:Filme)<-[r2:ASSISTIU]-(:Usuario)-[r3:ASSISTIU]->(:Filme {filmeId:'f03'})
WHERE r1.nota >= 4 AND r2.nota >= 4 AND r3.nota >= 4
RETURN p;
