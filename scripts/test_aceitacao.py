"""Suite de testes de aceitacao do Projeto 3 NoSQL (Neo4j).

Valida:
1. Presenca de todos os entregaveis definidos em `README.md`.
2. Ausencia de marcacoes `(conferir)` pendentes nos arquivos de pesquisa e banco.
3. Conferencia exata de nos (39), relacionamentos (67) e restricoes (4) a partir de `db/seed.cypher`.
4. Resultados esperados de todas as consultas (`R0`, `R1`, `R2`, `R3`, `R4`, `C1`, `U1`, `U2`, `D1a`, `D1b`)
   em cada transicao de estado especificada em `banco/04-consultas-e-crud.md`.
5. Equivalencia da consulta SQL comparativa (`db/consultas/SQL-comparativo-R1.sql`) em `sqlite3`.
"""

from __future__ import annotations

import json
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys

from pptx import Presentation
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import verificar_projeto as vp  # noqa: E402


@pytest.fixture()
def seeded_graph() -> vp.PropertyGraphEngine:
    graph = vp.PropertyGraphEngine()
    vp.load_seed_from_file(graph, ROOT_DIR / "db" / "seed.cypher")
    return graph


def test_entregaveis_existem_e_nao_estao_vazios() -> None:
    expected_files = [
        "MAPEAMENTO_COMPLETO_PROJETO.md",
        "db/seed.cypher",
        "db/conferencia.cypher",
        "db/roteiro-demo-completa.cypher",
        "db/consultas/R0-visao-geral.cypher",
        "db/consultas/R1-recomendacao-colaborativa.cypher",
        "db/consultas/R2-explicacao-caminho.cypher",
        "db/consultas/R3-recomendacao-conteudo.cypher",
        "db/consultas/R4-populares-cold-start.cypher",
        "db/consultas/C1-lancamento-duna.cypher",
        "db/consultas/U1-diego-muda-nota.cypher",
        "db/consultas/U2-ana-muda-plano.cypher",
        "db/consultas/D1a-delete-ingenuo.cypher",
        "db/consultas/D1b-detach-delete.cypher",
        "db/consultas/DBA-indices-e-profile.cypher",
        "db/consultas/SQL-comparativo-R1.sql",
        "apresentacao/modelo-arrows.json",
        "apresentacao/slides-interativos.html",
        "apresentacao/Projeto3_NoSQL_Neo4j_Recomendacao.pptx",
    ]
    for rel_path in expected_files:
        full_path = ROOT_DIR / rel_path
        assert full_path.exists(), f"Arquivo ausente: {rel_path}"
        assert full_path.stat().st_size > 0, f"Arquivo vazio: {rel_path}"


def test_apresentacao_e_diagrama_validos() -> None:
    arrows = json.loads((ROOT_DIR / "apresentacao" / "modelo-arrows.json").read_text(encoding="utf-8"))
    assert len(arrows["nodes"]) == 4
    assert len(arrows["relationships"]) == 3

    html = (ROOT_DIR / "apresentacao" / "slides-interativos.html").read_text(encoding="utf-8")
    assert html.count('<section class="slide') == 15

    prs = Presentation(str(ROOT_DIR / "apresentacao" / "Projeto3_NoSQL_Neo4j_Recomendacao.pptx"))
    assert len(prs.slides) == 15


def test_nenhum_conferir_pendente_em_banco_e_pesquisa() -> None:
    for folder in ("banco", "pesquisa"):
        for md_file in (ROOT_DIR / folder).glob("*.md"):
            content = md_file.read_text(encoding="utf-8").lower()
            assert "(conferir" not in content, f"Pendencia '(conferir)' encontrada em {md_file}"


def test_conferencia_seed(seeded_graph: vp.PropertyGraphEngine) -> None:
    conf = vp.run_conferencia(seeded_graph)
    assert conf["nodes"] == {"Ator": 12, "Filme": 12, "Genero": 7, "Usuario": 8}
    assert conf["relationships"] == {"ASSISTIU": 26, "ATUOU_EM": 19, "DO_GENERO": 22}
    assert conf["constraints"] == ["ator_nome", "filme_id", "genero_nome", "usuario_id"]

    r0 = vp.query_r0_visao_geral(seeded_graph)
    assert r0 == {"nos": 39, "relacionamentos": 67}


def test_consultas_iniciais_pos_seed(seeded_graph: vp.PropertyGraphEngine) -> None:
    r1 = vp.query_r1_recomendacao_colaborativa(seeded_graph)
    assert r1 == [
        {"recomendacao": "Interestelar", "usuariosParecidos": 2, "forca": 3, "notaMedia": 4.5},
        {"recomendacao": "O Lobo de Wall Street", "usuariosParecidos": 1, "forca": 1, "notaMedia": 4.0},
    ]

    r2 = vp.query_r2_explicacao_caminho(seeded_graph)
    assert sorted(r2) == sorted(
        [
            ["Ana", "Matrix", "Bruno", "Interestelar"],
            ["Ana", "A Origem", "Bruno", "Interestelar"],
            ["Ana", "Matrix", "Diego", "Interestelar"],
        ]
    )

    r3 = vp.query_r3_recomendacao_conteudo(seeded_graph)
    assert r3 == [
        {"recomendacao": "Interestelar", "motivo": ["Ficção Científica"], "pontos": 2},
        {"recomendacao": "O Lobo de Wall Street", "motivo": ["Leonardo DiCaprio"], "pontos": 1},
        {"recomendacao": "Titanic", "motivo": ["Leonardo DiCaprio"], "pontos": 1},
    ]

    r4 = vp.query_r4_populares_cold_start(seeded_graph)
    assert r4 == [
        {"filme": "Matrix", "vezes": 4, "notaMedia": 4.3},
        {"filme": "Diário de uma Paixão", "vezes": 3, "notaMedia": 4.7},
        {"filme": "A Origem", "vezes": 2, "notaMedia": 4.5},
        {"filme": "Divertida Mente", "vezes": 2, "notaMedia": 4.5},
        {"filme": "Forrest Gump", "vezes": 2, "notaMedia": 4.5},
    ]


def test_ciclo_completo_crud_e_transicoes_estado(seeded_graph: vp.PropertyGraphEngine) -> None:
    # C1: Duna entra
    metrics_c1, _ = vp.exec_c1_lancamento_duna(seeded_graph)
    assert metrics_c1.added_labels == 2
    assert metrics_c1.created_nodes == 2
    assert metrics_c1.set_properties == 7
    assert metrics_c1.created_relationships == 4

    # C1 repetida deve falhar pela restricao filme_id e preservar atomicidade (rollback)
    nos_antes = len(seeded_graph.nodes)
    rels_antes = len(seeded_graph.relationships)
    with pytest.raises(vp.ConstraintViolationError):
        vp.exec_c1_lancamento_duna(seeded_graph)
    assert len(seeded_graph.nodes) == nos_antes
    assert len(seeded_graph.relationships) == rels_antes

    # R1 apos C1
    assert vp.query_r1_recomendacao_colaborativa(seeded_graph) == [
        {"recomendacao": "Duna", "usuariosParecidos": 2, "forca": 3, "notaMedia": 5.0},
        {"recomendacao": "Interestelar", "usuariosParecidos": 2, "forca": 3, "notaMedia": 4.5},
        {"recomendacao": "O Lobo de Wall Street", "usuariosParecidos": 1, "forca": 1, "notaMedia": 4.0},
    ]

    # R3 entre C1 e D1b
    assert vp.query_r3_recomendacao_conteudo(seeded_graph) == [
        {"recomendacao": "Duna", "motivo": ["Ficção Científica"], "pontos": 2},
        {"recomendacao": "Interestelar", "motivo": ["Ficção Científica"], "pontos": 2},
        {"recomendacao": "O Lobo de Wall Street", "motivo": ["Leonardo DiCaprio"], "pontos": 1},
        {"recomendacao": "Titanic", "motivo": ["Leonardo DiCaprio"], "pontos": 1},
    ]

    # U1: Diego muda nota de O Lobo de Wall Street para 2
    metrics_u1, res_u1 = vp.exec_u1_diego_muda_nota(seeded_graph)
    assert metrics_u1.set_properties == 1
    assert res_u1 == {"filme": "O Lobo de Wall Street", "novaNota": 2}
    assert vp.query_r1_recomendacao_colaborativa(seeded_graph) == [
        {"recomendacao": "Duna", "usuariosParecidos": 2, "forca": 3, "notaMedia": 5.0},
        {"recomendacao": "Interestelar", "usuariosParecidos": 2, "forca": 3, "notaMedia": 4.5},
    ]

    # U2: Ana muda plano para Premium e ganha campo novo atualizadoEm sem ALTER TABLE
    metrics_u2, res_u2 = vp.exec_u2_ana_muda_plano(seeded_graph)
    assert metrics_u2.set_properties == 2
    assert res_u2["plano"] == "Premium"
    assert "atualizadoEm" in res_u2 and res_u2["atualizadoEm"]
    diego = seeded_graph.find_node("Usuario", usuarioId="u04")
    assert diego is not None and "atualizadoEm" not in diego.properties

    # D1a: DELETE simples em no com relacionamentos deve falhar
    with pytest.raises(vp.RelationshipDeletionError):
        vp.exec_d1a_delete_ingenuo(seeded_graph)

    # D1b: DETACH DELETE remove Duna e suas 4 ligacoes; Timothee Chalamet permanece sem filmes
    metrics_d1b = vp.exec_d1b_detach_delete(seeded_graph)
    assert metrics_d1b.deleted_nodes == 1
    assert metrics_d1b.deleted_relationships == 4
    assert seeded_graph.find_node("Filme", filmeId="f13") is None
    assert seeded_graph.find_node("Ator", nome="Timothée Chalamet") is not None

    # R1 e R3 apos D1b
    assert vp.query_r1_recomendacao_colaborativa(seeded_graph) == [
        {"recomendacao": "Interestelar", "usuariosParecidos": 2, "forca": 3, "notaMedia": 4.5},
    ]
    assert vp.query_r3_recomendacao_conteudo(seeded_graph) == [
        {"recomendacao": "Interestelar", "motivo": ["Ficção Científica"], "pontos": 2},
        {"recomendacao": "O Lobo de Wall Street", "motivo": ["Leonardo DiCaprio"], "pontos": 1},
        {"recomendacao": "Titanic", "motivo": ["Leonardo DiCaprio"], "pontos": 1},
    ]


def test_equivalencia_sql_comparativo_r1(seeded_graph: vp.PropertyGraphEngine) -> None:
    sql_query = (ROOT_DIR / "db" / "consultas" / "SQL-comparativo-R1.sql").read_text(
        encoding="utf-8"
    )
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE filme (filme_id TEXT PRIMARY KEY, titulo TEXT)")
    conn.execute(
        "CREATE TABLE assistiu (usuario_id TEXT, filme_id TEXT, nota INTEGER, PRIMARY KEY (usuario_id, filme_id))"
    )
    for node in seeded_graph.nodes:
        if "Filme" in node.labels:
            conn.execute(
                "INSERT INTO filme VALUES (?, ?)",
                (node.properties["filmeId"], node.properties["titulo"]),
            )
    for rel in seeded_graph.relationships:
        if rel.rel_type == "ASSISTIU":
            conn.execute(
                "INSERT INTO assistiu VALUES (?, ?, ?)",
                (
                    rel.start_node.properties["usuarioId"],
                    rel.end_node.properties["filmeId"],
                    rel.properties["nota"],
                ),
            )

    sql_rows = conn.execute(sql_query).fetchall()
    cypher_rows = [
        (r["recomendacao"], r["usuariosParecidos"])
        for r in vp.query_r1_recomendacao_colaborativa(seeded_graph)
    ]
    assert sql_rows == cypher_rows == [("Interestelar", 2), ("O Lobo de Wall Street", 1)]


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def test_integracao_neo4j_bolt_real() -> None:
    """Executa toda a bateria de consultas Cypher diretamente no Neo4j 5 local via Bolt.

    Se o servidor local nao estiver rodando, sobe temporariamente via `iniciar_neo4j.ps1`
    e encerra ao final com `parar_neo4j.ps1` para nao deixar processos ativos.
    """
    started_here = False
    if not _port_open("127.0.0.1", 7687):
        subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT_DIR / "scripts" / "iniciar_neo4j.ps1"),
            ],
            check=True,
        )
        started_here = True

    try:
        rc = vp.run_against_neo4j_bolt(
            "bolt://localhost:7687", "neo4j", "senhaDemo123", assert_expected=True
        )
        assert rc == 0
        rc_reset = vp.run_against_neo4j_bolt(
            "bolt://localhost:7687",
            "neo4j",
            "senhaDemo123",
            assert_expected=True,
            reset_only=True,
        )
        assert rc_reset == 0
    finally:
        if started_here:
            subprocess.run(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT_DIR / "scripts" / "parar_neo4j.ps1"),
                ],
                check=True,
            )
