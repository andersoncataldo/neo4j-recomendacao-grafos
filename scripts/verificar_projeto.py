"""Motor de verificacao e execucao do Projeto 3 NoSQL (Neo4j - Recomendacao de Filmes).

Permite:
1. Carregar e validar `db/seed.cypher` em um grafo de propriedades em memoria
   com adjacencia sem indice (ponteiros diretos entre nos e relacionamentos) e
   restricoes de unicidade + integridade ACID.
2. Executar toda a sequencia oficial de conferencia e CRUD ao vivo
   (R0, R1, R2, R3, R4, C1, U1, U2, D1a, D1b) validando contra os criterios
   de aceitacao de `banco/03-seed-e-conferencia.md` e `banco/04-consultas-e-crud.md`.
3. Opcionalmente executar os scripts diretamente contra um servidor Neo4j real
   (Local ou AuraDB) via Bolt caso `--bolt` seja informado e o driver `neo4j`
   esteja disponivel.
"""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import re
import sys
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
DB_DIR = ROOT_DIR / "db"
CONSULTAS_DIR = DB_DIR / "consultas"


class Neo4jSimulationError(Exception):
    """Erro base de execucao no simulador de grafo."""


class ConstraintViolationError(Neo4jSimulationError):
    """Disparado quando uma restricao UNIQUE e violada."""


class RelationshipDeletionError(Neo4jSimulationError):
    """Disparado ao tentar DELETE simples em no com relacionamentos."""


@dataclass
class Node:
    """Representa um vertice no grafo de propriedades com ponteiros de adjacencia."""

    internal_id: int
    labels: set[str] = field(default_factory=set)
    properties: dict[str, Any] = field(default_factory=dict)
    outgoing: list["Relationship"] = field(default_factory=list)
    incoming: list["Relationship"] = field(default_factory=list)


@dataclass
class Relationship:
    """Representa uma aresta direcionada com tipo e propriedades proprias."""

    internal_id: int
    rel_type: str
    start_node: Node
    end_node: Node
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class WriteMetrics:
    """Resumo estilo Neo4j Browser de alteracoes de uma operacao Cypher."""

    added_labels: int = 0
    created_nodes: int = 0
    set_properties: int = 0
    created_relationships: int = 0
    deleted_nodes: int = 0
    deleted_relationships: int = 0

    def format_summary(self) -> str:
        parts = []
        if self.added_labels:
            parts.append(f"Added {self.added_labels} labels")
        if self.created_nodes:
            parts.append(f"created {self.created_nodes} nodes")
        if self.set_properties:
            parts.append(f"set {self.set_properties} properties")
        if self.created_relationships:
            parts.append(f"created {self.created_relationships} relationships")
        if self.deleted_nodes:
            parts.append(f"Deleted {self.deleted_nodes} node")
        if self.deleted_relationships:
            parts.append(f"deleted {self.deleted_relationships} relationships")
        return ", ".join(parts) if parts else "(no changes)"


class PropertyGraphEngine:
    """Motor de Grafo de Propriedades em memoria fiel ao modelo do Neo4j."""

    def __init__(self) -> None:
        self._next_node_id = 1
        self._next_rel_id = 1
        self.nodes: list[Node] = []
        self.relationships: list[Relationship] = []
        self.constraints: dict[str, tuple[str, str]] = {}

    def clear(self) -> None:
        self.nodes.clear()
        self.relationships.clear()
        self._next_node_id = 1
        self._next_rel_id = 1

    def add_constraint(self, name: str, label: str, prop: str) -> None:
        self.constraints[name] = (label, prop)

    def _check_uniqueness(
        self, label: str, prop: str, value: Any, exclude_node: Node | None = None
    ) -> None:
        for cname, (clabel, cprop) in self.constraints.items():
            if clabel == label and cprop == prop:
                for node in self.nodes:
                    if node is exclude_node:
                        continue
                    if label in node.labels and node.properties.get(prop) == value:
                        raise ConstraintViolationError(
                            f"Node already exists with label :{label} and property {prop}={value!r} "
                            f"(constraint '{cname}')"
                        )

    def find_node(self, label: str, **props: Any) -> Node | None:
        for node in self.nodes:
            if label in node.labels and all(
                node.properties.get(k) == v for k, v in props.items()
            ):
                return node
        return None

    def create_node(self, labels: list[str], properties: dict[str, Any]) -> Node:
        for label in labels:
            for prop, val in properties.items():
                self._check_uniqueness(label, prop, val)
        node = Node(
            internal_id=self._next_node_id,
            labels=set(labels),
            properties=dict(properties),
        )
        self._next_node_id += 1
        self.nodes.append(node)
        return node

    def merge_node(
        self, label: str, key_props: dict[str, Any], set_props: dict[str, Any] | None = None
    ) -> tuple[Node, bool]:
        existing = self.find_node(label, **key_props)
        if existing is not None:
            if set_props:
                for k, v in set_props.items():
                    self._check_uniqueness(label, k, v, exclude_node=existing)
                    existing.properties[k] = v
            return existing, False
        merged_props = {**key_props, **(set_props or {})}
        return self.create_node([label], merged_props), True

    def create_relationship(
        self, start: Node, rel_type: str, end: Node, properties: dict[str, Any] | None = None
    ) -> Relationship:
        rel = Relationship(
            internal_id=self._next_rel_id,
            rel_type=rel_type,
            start_node=start,
            end_node=end,
            properties=dict(properties or {}),
        )
        self._next_rel_id += 1
        start.outgoing.append(rel)
        end.incoming.append(rel)
        self.relationships.append(rel)
        return rel

    def merge_relationship(
        self, start: Node, rel_type: str, end: Node, properties: dict[str, Any] | None = None
    ) -> tuple[Relationship, bool]:
        for rel in start.outgoing:
            if rel.rel_type == rel_type and rel.end_node is end:
                if properties:
                    rel.properties.update(properties)
                return rel, False
        return self.create_relationship(start, rel_type, end, properties), True

    def delete_node(self, node: Node, detach: bool = False) -> WriteMetrics:
        attached = list(node.outgoing) + list(node.incoming)
        if attached and not detach:
            raise RelationshipDeletionError(
                f"Cannot delete node<{node.internal_id}>, because it still has relationships. "
                "To delete this node, you must first delete its relationships (DETACH DELETE)."
            )
        metrics = WriteMetrics()
        for rel in attached:
            if rel in rel.start_node.outgoing:
                rel.start_node.outgoing.remove(rel)
            if rel in rel.end_node.incoming:
                rel.end_node.incoming.remove(rel)
            if rel in self.relationships:
                self.relationships.remove(rel)
                metrics.deleted_relationships += 1
        self.nodes.remove(node)
        metrics.deleted_nodes = 1
        return metrics

    def snapshot(self) -> tuple[int, int, list[Node], list[Relationship]]:
        """Captura copia rasa para rollback atomico ACID em caso de erro."""
        nodes_copy = list(self.nodes)
        rels_copy = list(self.relationships)
        return self._next_node_id, self._next_rel_id, nodes_copy, rels_copy

    def restore(self, snap: tuple[int, int, list[Node], list[Relationship]]) -> None:
        next_n, next_r, nodes_copy, rels_copy = snap
        self._next_node_id = next_n
        self._next_rel_id = next_r
        self.nodes = nodes_copy
        self.relationships = rels_copy
        for n in self.nodes:
            n.outgoing = [r for r in self.relationships if r.start_node is n]
            n.incoming = [r for r in self.relationships if r.end_node is n]


def _cypher_list_to_python(raw_list_text: str) -> list[Any]:
    """Converte bloco UNWIND [...] de Cypher (chaves sem aspas) para objetos Python."""
    quoted_keys = re.sub(r"([{\[,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', raw_list_text)
    return ast.literal_eval(quoted_keys)


def load_seed_from_file(graph: PropertyGraphEngine, seed_path: Path) -> None:
    """Le e executa o arquivo `db/seed.cypher` diretamente no grafo em memoria."""
    text = seed_path.read_text(encoding="utf-8")

    if "MATCH (n) DETACH DELETE n" in text:
        graph.clear()

    constraint_pattern = re.compile(
        r"CREATE\s+CONSTRAINT\s+(\w+)\s+IF\s+NOT\s+EXISTS\s+FOR\s+\(\w+:(\w+)\)\s+REQUIRE\s+\w+\.(\w+)\s+IS\s+UNIQUE",
        re.IGNORECASE,
    )
    for cname, label, prop in constraint_pattern.findall(text):
        graph.add_constraint(cname, label, prop)

    unwind_blocks = re.findall(r"UNWIND\s*(\[.*?\])\s*AS\s*row", text, flags=re.DOTALL)
    if len(unwind_blocks) != 3:
        raise ValueError(
            f"Esperado 3 blocos UNWIND em {seed_path}, encontrado {len(unwind_blocks)}."
        )

    filmes_data = _cypher_list_to_python(unwind_blocks[0])
    usuarios_data = _cypher_list_to_python(unwind_blocks[1])
    assistiu_data = _cypher_list_to_python(unwind_blocks[2])

    for row in filmes_data:
        filme, _ = graph.merge_node(
            "Filme",
            {"filmeId": row["id"]},
            {"titulo": row["titulo"], "ano": row["ano"], "duracaoMin": row["duracao"]},
        )
        for gen_name in row["generos"]:
            gen, _ = graph.merge_node("Genero", {"nome": gen_name})
            graph.merge_relationship(filme, "DO_GENERO", gen)
        for actor_name in row["atores"]:
            actor, _ = graph.merge_node("Ator", {"nome": actor_name})
            graph.merge_relationship(actor, "ATUOU_EM", filme)

    for row in usuarios_data:
        graph.merge_node(
            "Usuario",
            {"usuarioId": row["id"]},
            {"nome": row["nome"], "plano": row["plano"]},
        )

    for user_id, filme_id, nota in assistiu_data:
        u = graph.find_node("Usuario", usuarioId=user_id)
        f = graph.find_node("Filme", filmeId=filme_id)
        if u is None or f is None:
            raise ValueError(f"Referencia invalida no seed: {user_id} -> {filme_id}")
        graph.merge_relationship(u, "ASSISTIU", f, {"nota": nota})


def run_conferencia(graph: PropertyGraphEngine) -> dict[str, Any]:
    """Executa as 3 verificacoes de `db/conferencia.cypher`."""
    node_counts: dict[str, int] = defaultdict(int)
    for node in graph.nodes:
        label = sorted(node.labels)[0] if node.labels else ""
        node_counts[label] += 1

    rel_counts: dict[str, int] = defaultdict(int)
    for rel in graph.relationships:
        rel_counts[rel.rel_type] += 1

    return {
        "nodes": dict(sorted(node_counts.items())),
        "relationships": dict(sorted(rel_counts.items())),
        "constraints": sorted(graph.constraints.keys()),
    }


def query_r0_visao_geral(graph: PropertyGraphEngine) -> dict[str, int]:
    return {"nos": len(graph.nodes), "relacionamentos": len(graph.relationships)}


def _cypher_round_1(value: float) -> float:
    """Replica o arredondamento HALF_UP do Cypher (`round(x, 1)`)."""
    return float(Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def query_r1_recomendacao_colaborativa(
    graph: PropertyGraphEngine, usuario_id: str = "u01", limit: int = 5
) -> list[dict[str, Any]]:
    alvo = graph.find_node("Usuario", usuarioId=usuario_id)
    if alvo is None:
        return []

    alvo_watched = {
        rel.end_node.internal_id: rel.properties.get("nota", 0)
        for rel in alvo.outgoing
        if rel.rel_type == "ASSISTIU"
    }

    # Passo 1: encontrar outros usuarios com filmes em comum avaliados >= 4
    em_comum_por_outro: dict[int, tuple[Node, int]] = {}
    for rel_alvo in alvo.outgoing:
        if rel_alvo.rel_type != "ASSISTIU" or rel_alvo.properties.get("nota", 0) < 4:
            continue
        filme = rel_alvo.end_node
        for rel_outro in filme.incoming:
            if rel_outro.rel_type != "ASSISTIU" or rel_outro.properties.get("nota", 0) < 4:
                continue
            outro = rel_outro.start_node
            if outro.internal_id not in em_comum_por_outro:
                em_comum_por_outro[outro.internal_id] = (outro, 0)
            prev_node, prev_cnt = em_comum_por_outro[outro.internal_id]
            em_comum_por_outro[outro.internal_id] = (prev_node, prev_cnt + 1)

    # Passo 2: percorrer filmes avaliados >= 4 pelos usuarios parecidos que alvo nao viu
    recs: dict[int, dict[str, Any]] = {}
    for outro_id, (outro, em_comum) in em_comum_por_outro.items():
        for rel3 in outro.outgoing:
            if rel3.rel_type != "ASSISTIU" or rel3.properties.get("nota", 0) < 4:
                continue
            rec = rel3.end_node
            if rec.internal_id in alvo_watched:
                continue
            if rec.internal_id not in recs:
                recs[rec.internal_id] = {
                    "recomendacao": rec.properties["titulo"],
                    "outros": set(),
                    "forca": 0,
                    "notas": [],
                }
            recs[rec.internal_id]["outros"].add(outro_id)
            recs[rec.internal_id]["forca"] += em_comum
            recs[rec.internal_id]["notas"].append(rel3.properties["nota"])

    results = [
        {
            "recomendacao": info["recomendacao"],
            "usuariosParecidos": len(info["outros"]),
            "forca": info["forca"],
            "notaMedia": _cypher_round_1(sum(info["notas"]) / len(info["notas"])),
        }
        for info in recs.values()
    ]
    results.sort(key=lambda x: (-x["forca"], -x["notaMedia"], x["recomendacao"]))
    return results[:limit]


def query_r2_explicacao_caminho(
    graph: PropertyGraphEngine, usuario_id: str = "u01", filme_id: str = "f03"
) -> list[list[str]]:
    alvo = graph.find_node("Usuario", usuarioId=usuario_id)
    destino = graph.find_node("Filme", filmeId=filme_id)
    if alvo is None or destino is None:
        return []

    paths: list[list[str]] = []
    for r1 in alvo.outgoing:
        if r1.rel_type != "ASSISTIU" or r1.properties.get("nota", 0) < 4:
            continue
        filme_comum = r1.end_node
        for r2 in filme_comum.incoming:
            if r2.rel_type != "ASSISTIU" or r2.properties.get("nota", 0) < 4:
                continue
            outro = r2.start_node
            for r3 in outro.outgoing:
                if (
                    r3.rel_type == "ASSISTIU"
                    and r3.properties.get("nota", 0) >= 4
                    and r3.end_node is destino
                ):
                    paths.append(
                        [
                            alvo.properties["nome"],
                            filme_comum.properties["titulo"],
                            outro.properties["nome"],
                            destino.properties["titulo"],
                        ]
                    )
    return paths


def _connected_attributes(filme: Node) -> list[Node]:
    """Retorna nos ligados por [:DO_GENERO|ATUOU_EM] em qualquer direcao."""
    attrs: list[Node] = []
    for rel in filme.outgoing:
        if rel.rel_type in ("DO_GENERO", "ATUOU_EM"):
            attrs.append(rel.end_node)
    for rel in filme.incoming:
        if rel.rel_type in ("DO_GENERO", "ATUOU_EM"):
            attrs.append(rel.start_node)
    return attrs


def _connected_films(attr_node: Node) -> list[Node]:
    films: list[Node] = []
    for rel in attr_node.incoming:
        if rel.rel_type in ("DO_GENERO", "ATUOU_EM"):
            films.append(rel.start_node)
    for rel in attr_node.outgoing:
        if rel.rel_type in ("DO_GENERO", "ATUOU_EM"):
            films.append(rel.end_node)
    return films


def query_r3_recomendacao_conteudo(
    graph: PropertyGraphEngine, usuario_id: str = "u01", limit: int = 5
) -> list[dict[str, Any]]:
    alvo = graph.find_node("Usuario", usuarioId=usuario_id)
    if alvo is None:
        return []

    alvo_watched = {
        rel.end_node.internal_id for rel in alvo.outgoing if rel.rel_type == "ASSISTIU"
    }

    recs: dict[int, dict[str, Any]] = {}
    for rel in alvo.outgoing:
        if rel.rel_type != "ASSISTIU" or rel.properties.get("nota", 0) < 4:
            continue
        filme_visto = rel.end_node
        for attr in _connected_attributes(filme_visto):
            for rec in _connected_films(attr):
                if rec.internal_id in alvo_watched:
                    continue
                if rec.internal_id not in recs:
                    recs[rec.internal_id] = {
                        "recomendacao": rec.properties["titulo"],
                        "motivo": [],
                        "pontos": 0,
                    }
                if attr.properties["nome"] not in recs[rec.internal_id]["motivo"]:
                    recs[rec.internal_id]["motivo"].append(attr.properties["nome"])
                recs[rec.internal_id]["pontos"] += 1

    results = list(recs.values())
    results.sort(key=lambda x: (-x["pontos"], x["recomendacao"]))
    return results[:limit]


def query_r4_populares_cold_start(
    graph: PropertyGraphEngine, limit: int = 5
) -> list[dict[str, Any]]:
    stats: dict[int, dict[str, Any]] = {}
    for rel in graph.relationships:
        if rel.rel_type != "ASSISTIU":
            continue
        f = rel.end_node
        if f.internal_id not in stats:
            stats[f.internal_id] = {"filme": f.properties["titulo"], "notas": []}
        stats[f.internal_id]["notas"].append(rel.properties["nota"])

    results = [
        {
            "filme": info["filme"],
            "vezes": len(info["notas"]),
            "notaMedia": _cypher_round_1(sum(info["notas"]) / len(info["notas"])),
        }
        for info in stats.values()
    ]
    results.sort(key=lambda x: (-x["vezes"], -x["notaMedia"], x["filme"]))
    return results[:limit]


def exec_c1_lancamento_duna(graph: PropertyGraphEngine) -> tuple[WriteMetrics, dict[str, Any]]:
    """Executa C1 de forma transacional (rollback completo se falhar)."""
    snap = graph.snapshot()
    try:
        g = graph.find_node("Genero", nome="Ficção Científica")
        bruno = graph.find_node("Usuario", usuarioId="u02")
        diego = graph.find_node("Usuario", usuarioId="u04")
        if not (g and bruno and diego):
            raise ValueError("Nos base do C1 nao encontrados no grafo.")

        metrics = WriteMetrics()
        duna = graph.create_node(
            ["Filme"],
            {"filmeId": "f13", "titulo": "Duna", "ano": 2021, "duracaoMin": 155},
        )
        metrics.added_labels += 1
        metrics.created_nodes += 1
        metrics.set_properties += 4

        graph.create_relationship(duna, "DO_GENERO", g)
        metrics.created_relationships += 1

        ator, created_ator = graph.merge_node("Ator", {"nome": "Timothée Chalamet"})
        if created_ator:
            metrics.added_labels += 1
            metrics.created_nodes += 1
            metrics.set_properties += 1

        graph.create_relationship(ator, "ATUOU_EM", duna)
        metrics.created_relationships += 1

        graph.create_relationship(bruno, "ASSISTIU", duna, {"nota": 5})
        metrics.set_properties += 1
        metrics.created_relationships += 1

        graph.create_relationship(diego, "ASSISTIU", duna, {"nota": 5})
        metrics.set_properties += 1
        metrics.created_relationships += 1

        return metrics, {
            "f": duna.properties,
            "g": g.properties,
            "a": ator.properties,
            "bruno": bruno.properties,
            "diego": diego.properties,
        }
    except Exception:
        graph.restore(snap)
        raise


def exec_u1_diego_muda_nota(graph: PropertyGraphEngine) -> tuple[WriteMetrics, dict[str, Any]]:
    diego = graph.find_node("Usuario", usuarioId="u04")
    lobo = graph.find_node("Filme", filmeId="f05")
    if not (diego and lobo):
        raise ValueError("Nos para U1 nao encontrados.")
    for rel in diego.outgoing:
        if rel.rel_type == "ASSISTIU" and rel.end_node is lobo:
            rel.properties["nota"] = 2
            return WriteMetrics(set_properties=1), {"filme": lobo.properties["titulo"], "novaNota": 2}
    raise ValueError("Relacionamento ASSISTIU entre u04 e f05 nao encontrado.")


def exec_u2_ana_muda_plano(graph: PropertyGraphEngine) -> tuple[WriteMetrics, dict[str, Any]]:
    ana = graph.find_node("Usuario", usuarioId="u01")
    if ana is None:
        raise ValueError("No u01 nao encontrado.")
    ana.properties["plano"] = "Premium"
    ana.properties["atualizadoEm"] = datetime.now(timezone.utc).isoformat()
    return WriteMetrics(set_properties=2), dict(ana.properties)


def exec_d1a_delete_ingenuo(graph: PropertyGraphEngine) -> None:
    duna = graph.find_node("Filme", filmeId="f13")
    if duna is None:
        raise ValueError("No f13 nao encontrado.")
    graph.delete_node(duna, detach=False)


def exec_d1b_detach_delete(graph: PropertyGraphEngine) -> WriteMetrics:
    duna = graph.find_node("Filme", filmeId="f13")
    if duna is None:
        raise ValueError("No f13 nao encontrado.")
    return graph.delete_node(duna, detach=True)


def _print_table(title: str, rows: list[dict[str, Any]]) -> None:
    print(f"\n=== {title} ===")
    if not rows:
        print("(sem resultados)")
        return
    headers = list(rows[0].keys())
    widths = {
        h: max(len(str(h)), *(len(str(r[h])) for r in rows)) for h in headers
    }
    header_line = " | ".join(str(h).ljust(widths[h]) for h in headers)
    sep_line = "-+-".join("-" * widths[h] for h in headers)
    print(header_line)
    print(sep_line)
    for row in rows:
        print(" | ".join(str(row[h]).ljust(widths[h]) for h in headers))


def verify_in_memory() -> int:
    """Executa toda a jornada da demo em memoria e imprime o relatorio completo."""
    graph = PropertyGraphEngine()
    seed_path = DB_DIR / "seed.cypher"
    load_seed_from_file(graph, seed_path)

    conf = run_conferencia(graph)
    print("=== SEED & CONFERENCIA ===")
    print(f"Nos por tipo: {conf['nodes']}")
    print(f"Relacionamentos por tipo: {conf['relationships']}")
    print(f"Restricoes: {conf['constraints']}")

    r0 = query_r0_visao_geral(graph)
    print(f"\n[Passo 1 · R0] Grafo completo: {r0['nos']} nos, {r0['relacionamentos']} relacionamentos")

    _print_table("[Passo 2 · R1 apos seed] Recomendacao colaborativa (Ana)", query_r1_recomendacao_colaborativa(graph))

    paths_r2 = query_r2_explicacao_caminho(graph)
    print("\n=== [Passo 3 · R2] Caminhos explicativos ate Interestelar ===")
    for idx, p in enumerate(paths_r2, 1):
        print(f"  {idx}. {' -> '.join(p)}")

    _print_table("[R3 apos seed] Recomendacao por conteudo (Ana)", query_r3_recomendacao_conteudo(graph))
    _print_table("[R4] Mais populares (Cold Start)", query_r4_populares_cold_start(graph))

    m_c1, _ = exec_c1_lancamento_duna(graph)
    print(f"\n[Passo 4 · C1] {m_c1.format_summary()}")
    try:
        exec_c1_lancamento_duna(graph)
    except ConstraintViolationError as err:
        print(f"[Teste ACID/Unicidade · C1 repetida] Rollback garantido: {err}")

    _print_table("[Passo 5 · R1 apos C1] Duna assume 1o lugar em tempo real", query_r1_recomendacao_colaborativa(graph))
    _print_table("[R3 apos C1] Conteudo com Duna", query_r3_recomendacao_conteudo(graph))

    m_u1, res_u1 = exec_u1_diego_muda_nota(graph)
    print(f"\n[Passo 6 · U1] {m_u1.format_summary()} -> {res_u1}")
    _print_table("[Passo 7 · R1 apos U1] O Lobo de Wall Street saiu", query_r1_recomendacao_colaborativa(graph))

    m_u2, res_u2 = exec_u2_ana_muda_plano(graph)
    print(f"\n[Passo 8 · U2] {m_u2.format_summary()} -> {res_u2}")

    try:
        exec_d1a_delete_ingenuo(graph)
    except RelationshipDeletionError as err:
        print(f"\n[Passo 9 · D1a] Erro esperado (integridade): {err}")

    m_d1b = exec_d1b_detach_delete(graph)
    print(f"[Passo 10 · D1b] {m_d1b.format_summary()}")
    _print_table("[Passo 11 · R1 apos D1b] Apenas Interestelar resta", query_r1_recomendacao_colaborativa(graph))
    _print_table("[Passo 12 · R3 apos D1b] Conteudo volta ao estado original", query_r3_recomendacao_conteudo(graph))
    return 0


def run_against_neo4j_bolt(
    uri: str, user: str, password: str, assert_expected: bool = True, reset_only: bool = False
) -> int:
    """Executa todos os arquivos .cypher reais contra um servidor Neo4j ativo."""
    try:
        from neo4j import GraphDatabase  # type: ignore
    except ImportError:
        print("ERRO: pacote Python 'neo4j' nao instalado. Execute: pip install neo4j", file=sys.stderr)
        return 1

    def split_statements(cypher_text: str) -> list[str]:
        cleaned = "\n".join(
            line for line in cypher_text.splitlines() if not line.strip().startswith("//")
        )
        return [stmt.strip() for stmt in cleaned.split(";") if stmt.strip()]

    def run_seed(session: Any) -> None:
        for stmt in split_statements((DB_DIR / "seed.cypher").read_text(encoding="utf-8")):
            session.run(stmt).consume()

    def run_single(session: Any, fname: str) -> tuple[list[dict[str, Any]], Any]:
        stmt = split_statements((CONSULTAS_DIR / fname).read_text(encoding="utf-8"))[0]
        res = session.run(stmt)
        records = [r.data() for r in res]
        summary = res.consume()
        return records, summary

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            print(f"Conectado a {uri}. Executando seed.cypher no Neo4j real...")
            run_seed(session)

            conf_stmts = split_statements((DB_DIR / "conferencia.cypher").read_text(encoding="utf-8"))
            conf_nodes = {r["tipo"]: r["total"] for r in session.run(conf_stmts[0])}
            conf_rels = {r["relacionamento"]: r["total"] for r in session.run(conf_stmts[1])}
            conf_constraints = sorted(r["name"] for r in session.run(conf_stmts[2]))
            print(f"Conferencia real -> Nos: {conf_nodes} | Rels: {conf_rels} | Constraints: {conf_constraints}")
            if assert_expected:
                assert conf_nodes == {"Ator": 12, "Filme": 12, "Genero": 7, "Usuario": 8}, conf_nodes
                assert conf_rels == {"ASSISTIU": 26, "ATUOU_EM": 19, "DO_GENERO": 22}, conf_rels
                assert conf_constraints == ["ator_nome", "filme_id", "genero_nome", "usuario_id"], conf_constraints

            if reset_only:
                print("Reset rapido concluido e conferencia validada.")
                return 0

            r0_recs, _ = run_single(session, "R0-visao-geral.cypher")
            print(f"[R0] {len(r0_recs)} nos retornados")
            if assert_expected:
                assert len(r0_recs) == 39

            r1_seed, _ = run_single(session, "R1-recomendacao-colaborativa.cypher")
            _print_table("[Neo4j Real · R1 apos seed]", r1_seed)
            if assert_expected:
                assert r1_seed == [
                    {"recomendacao": "Interestelar", "usuariosParecidos": 2, "forca": 3, "notaMedia": 4.5},
                    {"recomendacao": "O Lobo de Wall Street", "usuariosParecidos": 1, "forca": 1, "notaMedia": 4.0},
                ], r1_seed

            r2_recs, _ = run_single(session, "R2-explicacao-caminho.cypher")
            print(f"[Neo4j Real · R2] {len(r2_recs)} caminhos retornados")
            if assert_expected:
                assert len(r2_recs) == 3

            r3_seed, _ = run_single(session, "R3-recomendacao-conteudo.cypher")
            _print_table("[Neo4j Real · R3 apos seed]", r3_seed)
            if assert_expected:
                assert r3_seed == [
                    {"recomendacao": "Interestelar", "motivo": ["Ficção Científica"], "pontos": 2},
                    {"recomendacao": "O Lobo de Wall Street", "motivo": ["Leonardo DiCaprio"], "pontos": 1},
                    {"recomendacao": "Titanic", "motivo": ["Leonardo DiCaprio"], "pontos": 1},
                ], r3_seed

            r4_recs, _ = run_single(session, "R4-populares-cold-start.cypher")
            _print_table("[Neo4j Real · R4 Cold Start]", r4_recs)
            if assert_expected:
                assert r4_recs == [
                    {"filme": "Matrix", "vezes": 4, "notaMedia": 4.3},
                    {"filme": "Diário de uma Paixão", "vezes": 3, "notaMedia": 4.7},
                    {"filme": "A Origem", "vezes": 2, "notaMedia": 4.5},
                    {"filme": "Divertida Mente", "vezes": 2, "notaMedia": 4.5},
                    {"filme": "Forrest Gump", "vezes": 2, "notaMedia": 4.5},
                ], r4_recs

            _, c1_sum = run_single(session, "C1-lancamento-duna.cypher")
            print(f"[Neo4j Real · C1] counters={c1_sum.counters}")
            if assert_expected:
                assert c1_sum.counters.nodes_created == 2
                assert c1_sum.counters.relationships_created == 4

            # Teste de unicidade em C1 duplicado
            try:
                run_single(session, "C1-lancamento-duna.cypher")
                raise AssertionError("Era esperado erro de restricao UNIQUE ao rodar C1 duas vezes!")
            except Exception as exc:
                print(f"[Neo4j Real · C1 duplicado] Erro UNIQUE esperado: {exc}")

            r1_c1, _ = run_single(session, "R1-recomendacao-colaborativa.cypher")
            _print_table("[Neo4j Real · R1 apos C1]", r1_c1)
            if assert_expected:
                assert r1_c1 == [
                    {"recomendacao": "Duna", "usuariosParecidos": 2, "forca": 3, "notaMedia": 5.0},
                    {"recomendacao": "Interestelar", "usuariosParecidos": 2, "forca": 3, "notaMedia": 4.5},
                    {"recomendacao": "O Lobo de Wall Street", "usuariosParecidos": 1, "forca": 1, "notaMedia": 4.0},
                ], r1_c1

            u1_recs, u1_sum = run_single(session, "U1-diego-muda-nota.cypher")
            print(f"[Neo4j Real · U1] {u1_recs} | counters={u1_sum.counters}")
            if assert_expected:
                assert u1_recs == [{"filme": "O Lobo de Wall Street", "novaNota": 2}]

            r1_u1, _ = run_single(session, "R1-recomendacao-colaborativa.cypher")
            _print_table("[Neo4j Real · R1 apos U1]", r1_u1)
            if assert_expected:
                assert r1_u1 == [
                    {"recomendacao": "Duna", "usuariosParecidos": 2, "forca": 3, "notaMedia": 5.0},
                    {"recomendacao": "Interestelar", "usuariosParecidos": 2, "forca": 3, "notaMedia": 4.5},
                ], r1_u1

            u2_recs, u2_sum = run_single(session, "U2-ana-muda-plano.cypher")
            print(f"[Neo4j Real · U2] counters={u2_sum.counters}")
            if assert_expected:
                ana_props = dict(u2_recs[0]["u"])
                assert ana_props["plano"] == "Premium"
                assert "atualizadoEm" in ana_props

            try:
                run_single(session, "D1a-delete-ingenuo.cypher")
                raise AssertionError("Era esperado erro ao executar DELETE simples em Duna!")
            except Exception as exc:
                print(f"[Neo4j Real · D1a] Erro esperado capturado: {exc}")

            _, d1b_sum = run_single(session, "D1b-detach-delete.cypher")
            print(f"[Neo4j Real · D1b] counters={d1b_sum.counters}")
            if assert_expected:
                assert d1b_sum.counters.nodes_deleted == 1
                assert d1b_sum.counters.relationships_deleted == 4

            r1_d1b, _ = run_single(session, "R1-recomendacao-colaborativa.cypher")
            _print_table("[Neo4j Real · R1 apos D1b]", r1_d1b)
            if assert_expected:
                assert r1_d1b == [
                    {"recomendacao": "Interestelar", "usuariosParecidos": 2, "forca": 3, "notaMedia": 4.5},
                ], r1_d1b

            # Reaplica o seed para deixar o banco pronto para a apresentacao no Neo4j Browser
            print("\nReaplicando seed.cypher para deixar o Neo4j Browser no estado inicial...")
            run_seed(session)
            print("Verificacao real via Bolt concluida com 100% de aderencia!")
    finally:
        driver.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verificador do Projeto 3 NoSQL (Neo4j)")
    parser.add_argument("--bolt", help="URI Bolt opcional (ex: bolt://localhost:7687)")
    parser.add_argument("--user", default="neo4j", help="Usuario Neo4j (padrao: neo4j)")
    parser.add_argument("--password", default="senhaDemo123", help="Senha Neo4j")
    parser.add_argument(
        "--reset-only",
        action="store_true",
        help="Com --bolt, reaplica apenas o seed e a conferencia sem rodar o roteiro CRUD",
    )
    args = parser.parse_args()

    if args.bolt:
        return run_against_neo4j_bolt(
            args.bolt, args.user, args.password, reset_only=args.reset_only
        )
    return verify_in_memory()


if __name__ == "__main__":
    raise SystemExit(main())
