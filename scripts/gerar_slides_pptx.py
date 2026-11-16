"""Gerador do deck PowerPoint (.pptx) do Projeto 3 NoSQL (Neo4j).

Cria `apresentacao/Projeto3_NoSQL_Neo4j_Recomendacao.pptx` com os 15 slides
previstos em `apresentacao/01-slides.md`, incluindo tabelas comparativas,
diagramas nativos (Index-Free Adjacency vs JOIN e Modelo de Dados), blocos de
codigo Cypher vs SQL e notas do apresentador em cada slide.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT_DIR = Path(__file__).resolve().parent.parent
OUT_PPTX = ROOT_DIR / "apresentacao" / "Projeto3_NoSQL_Neo4j_Recomendacao.pptx"

NAVY = RGBColor(0x00, 0x2B, 0x6B)
UNIFOR_BLUE = RGBColor(0x00, 0x44, 0xA8)
ROYAL = RGBColor(0x1A, 0x66, 0xCC)
SKY = RGBColor(0xE8, 0xF1, 0xFF)
TEAL = RGBColor(0x0F, 0x76, 0x6E)
AMBER = RGBColor(0xB4, 0x53, 0x09)
PURPLE = RGBColor(0x6D, 0x28, 0xD9)
RED = RGBColor(0xB9, 0x1C, 0x1C)
GREEN = RGBColor(0x15, 0x80, 0x3D)
DARK = RGBColor(0x0F, 0x17, 0x2A)
MUTED = RGBColor(0x47, 0x55, 0x69)
LIGHT_BG = RGBColor(0xF8, 0xFA, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xCB, 0xD5, 0xE1)


def _new_deck() -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def _add_notes(slide, text: str) -> None:
    slide.notes_slide.notes_text_frame.text = text


def _add_header_footer(
    slide, title: str, badge_text: str, page_num: int, footer_note: str = ""
) -> None:
    # Top accent bar
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = UNIFOR_BLUE
    bar.line.fill.background()

    # Title
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.28), Inches(9.5), Inches(0.65))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = NAVY

    # Badge
    badge = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.3), Inches(0.35), Inches(2.45), Inches(0.42)
    )
    badge.fill.solid()
    badge.fill.fore_color.rgb = SKY
    badge.line.color.rgb = ROYAL
    btf = badge.text_frame
    btf.word_wrap = True
    bp = btf.paragraphs[0]
    bp.text = badge_text
    bp.alignment = PP_ALIGN.CENTER
    bp.font.size = Pt(11.5)
    bp.font.bold = True
    bp.font.color.rgb = UNIFOR_BLUE

    # Divider line
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(0.98), Inches(12.133), Inches(0.02)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER
    line.line.fill.background()

    # Footer
    ft = slide.shapes.add_textbox(Inches(0.6), Inches(7.02), Inches(10.5), Inches(0.35))
    fp = ft.text_frame.paragraphs[0]
    fp.text = footer_note or "Unifor · Projeto de Banco de Dados (26.2) · Projeto 3 NoSQL"
    fp.font.size = Pt(10.5)
    fp.font.color.rgb = MUTED

    pg = slide.shapes.add_textbox(Inches(11.5), Inches(7.02), Inches(1.2), Inches(0.35))
    pp = pg.text_frame.paragraphs[0]
    pp.text = f"{page_num} / 15"
    pp.alignment = PP_ALIGN.RIGHT
    pp.font.size = Pt(10.5)
    pp.font.bold = True
    pp.font.color.rgb = MUTED


def _add_card(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    heading: str,
    bullets: list[str],
    accent_color: RGBColor = ROYAL,
    font_size: int = 13.5,
) -> None:
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT_BG
    box.line.color.rgb = BORDER

    stripe = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(0.09), Inches(height)
    )
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = accent_color
    stripe.line.fill.background()

    tb = slide.shapes.add_textbox(
        Inches(left + 0.2), Inches(top + 0.12), Inches(width - 0.32), Inches(height - 0.22)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = heading
    p0.font.size = Pt(15.5)
    p0.font.bold = True
    p0.font.color.rgb = accent_color
    p0.space_after = Pt(6)

    for item in bullets:
        p = tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(font_size)
        p.font.color.rgb = DARK
        p.space_after = Pt(4)


def _add_callout(
    slide, left: float, top: float, width: float, height: float, text: str, font_size: int = 13.5
) -> None:
    box = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    box.fill.solid()
    box.fill.fore_color.rgb = SKY
    box.line.color.rgb = ROYAL

    tb = slide.shapes.add_textbox(
        Inches(left + 0.18), Inches(top + 0.1), Inches(width - 0.32), Inches(height - 0.18)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = NAVY


def _add_table(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    headers: list[str],
    rows: list[list[str]],
    font_size: int = 12,
    highlight_row: int | None = None,
) -> None:
    shape = slide.shapes.add_table(
        len(rows) + 1, len(headers), Inches(left), Inches(top), Inches(width), Inches(height)
    )
    table = shape.table
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(font_size)
        p.font.bold = True
        p.font.color.rgb = WHITE

    for r_idx, row in enumerate(rows, start=1):
        is_hl = highlight_row is not None and (r_idx - 1) == highlight_row
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.fill.solid()
            if is_hl:
                cell.fill.fore_color.rgb = SKY
            else:
                cell.fill.fore_color.rgb = WHITE if r_idx % 2 == 1 else LIGHT_BG
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(font_size)
            p.font.bold = is_hl
            p.font.color.rgb = NAVY if is_hl else DARK


def _add_code_box(
    slide, left: float, top: float, width: float, height: float, title: str, code: str
) -> None:
    lbl = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(0.32))
    lp = lbl.text_frame.paragraphs[0]
    lp.text = title
    lp.font.size = Pt(13)
    lp.font.bold = True
    lp.font.color.rgb = NAVY

    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top + 0.32),
        Inches(width),
        Inches(height - 0.32),
    )
    box.fill.solid()
    box.fill.fore_color.rgb = DARK
    box.line.fill.background()

    tb = slide.shapes.add_textbox(
        Inches(left + 0.14), Inches(top + 0.42), Inches(width - 0.28), Inches(height - 0.5)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = code
    p.font.name = "Consolas"
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)


def _add_node(slide, cx: float, cy: float, r: float, title: str, subtitle: str, color: RGBColor) -> None:
    oval = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(cx - r), Inches(cy - r), Inches(2 * r), Inches(2 * r)
    )
    oval.fill.solid()
    oval.fill.fore_color.rgb = color
    oval.line.color.rgb = WHITE
    oval.line.width = Pt(2)
    tf = oval.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.alignment = PP_ALIGN.CENTER
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = WHITE


def build_presentation() -> Path:
    prs = _new_deck()
    blank = prs.slide_layouts[6]

    # SLIDE 1 · CAPA
    s1 = prs.slides.add_slide(blank)
    bg = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()

    tb = s1.shapes.add_textbox(Inches(0.9), Inches(1.15), Inches(11.4), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "UNIVERSIDADE DE FORTALEZA (UNIFOR) · PROJETO DE BANCO DE DADOS (26.2)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0x93, 0xC5, 0xFD)
    p.space_after = Pt(18)

    p2 = tf.add_paragraph()
    p2.text = "Bancos de Dados NoSQL:\nOrientado a Grafo com Neo4j"
    p2.font.size = Pt(42)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_after = Pt(18)

    p3 = tf.add_paragraph()
    p3.text = "Aplicação prática em Sistema de Recomendação de Filmes (estilo streaming)\ncom CRUD ao vivo em Cypher"
    p3.font.size = Pt(20)
    p3.font.color.rgb = RGBColor(0xE0, 0xF2, 0xFE)

    cards_info = [
        ("PARADIGMA SORTEADO", "5 · Orientado a Grafo"),
        ("SGBD & LINGUAGEM", "Neo4j · Cypher (ISO GQL)"),
        ("PROFESSORA", "Ana Maria Quevedo"),
    ]
    for idx, (k, v) in enumerate(cards_info):
        cx = 0.9 + idx * 3.9
        c = s1.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx), Inches(5.35), Inches(3.55), Inches(1.1)
        )
        c.fill.solid()
        c.fill.fore_color.rgb = UNIFOR_BLUE
        c.line.color.rgb = ROYAL
        ctf = c.text_frame
        ctf.word_wrap = True
        cp1 = ctf.paragraphs[0]
        cp1.text = k
        cp1.font.size = Pt(11)
        cp1.font.color.rgb = RGBColor(0xBF, 0xDB, 0xFE)
        cp2 = ctf.add_paragraph()
        cp2.text = v
        cp2.font.size = Pt(16)
        cp2.font.bold = True
        cp2.font.color.rgb = WHITE
    _add_notes(s1, "0,5 min. Apresentar o tema sorteado (Paradigma 5: Orientado a Grafo), SGBD Neo4j e sistema escolhido (recomendação de filmes).")

    # SLIDE 2 · O PARADIGMA DE GRAFO
    s2 = prs.slides.add_slide(blank)
    _add_header_footer(s2, "1. O Paradigma Orientado a Grafo", "Tópico 1 · 2,0 pts", 2, "Base: Aula 11 (Slides 29–30) & Graph Databases (O'Reilly)")
    _add_callout(
        s2, 0.6, 1.15, 12.133, 0.85,
        "Definição (Marko Rodriguez — Aula 11, Slide 29): \"Grafo é uma estrutura de dados que conecta um conjunto de vértices (nós) através de um conjunto de arestas (relacionamentos).\" Modelo whiteboard-friendly: o que desenhamos no quadro é o que gravamos no banco."
    )
    _add_card(s2, 0.6, 2.2, 5.9, 4.55, "Grafo de Propriedades Rotulado (LPG)", [
        "Nós (vértices): representam entidades (:Usuario, :Filme).",
        "Rótulos (Labels): classificam os tipos do nó (:Ator).",
        "Relacionamentos (arestas): conexões direcionadas e nomeadas ([:ASSISTIU]).",
        "Propriedades: pares chave-valor armazenados nos nós e nas arestas (nota: 5).",
    ], ROYAL)
    _add_card(s2, 6.83, 2.2, 5.9, 4.55, "Modelos e Tipos de Ferramenta do Enunciado", [
        "Property Graph (LPG): nós e arestas têm propriedades internas (Neo4j, JanusGraph, Neptune).",
        "RDF / Triplas: sujeito–predicado–objeto para Web Semântica/SPARQL (AllegroGraph, Neptune).",
        "Banco de Grafo (OLTP): consultas transacionais em tempo real (ex.: Neo4j).",
        "Motor de Processamento (OLAP): análise em lote distribuída (ex.: Apache Giraph, baseado no Pregel do Google).",
    ], TEAL)
    _add_notes(s2, "2 min. Usar os termos da Aula 11 (vértices, arestas, whiteboard-friendly) e diferenciar LPG vs RDF e Neo4j (OLTP) vs Apache Giraph (OLAP).")

    # SLIDE 3 · RELACIONAL x GRAFO
    s3 = prs.slides.add_slide(blank)
    _add_header_footer(s3, "Relacional × Grafo: JOIN na Consulta vs. Relação Gravada", "Tópico 1", 3, "Fonte: Vukotic et al. (Neo4j in Action, Cap. 1) & Graph Databases")
    _add_card(s3, 0.6, 1.15, 5.9, 2.45, "Modelo Relacional (SQL)", [
        "Relações N:N exigem tabelas associativas e chaves estrangeiras.",
        "Cada salto de profundidade gera um novo JOIN com busca em índice (B-tree).",
        "Explosão combinatória conforme a profundidade aumenta.",
    ], RED, 13)
    _add_card(s3, 6.83, 1.15, 5.9, 2.45, "Banco Orientado a Grafo (Neo4j)", [
        "As relações já ficam armazenadas fisicamente como ponteiros diretos.",
        "Aumentar saltos em Cypher é estender o padrão: (a)-[:AMIGO*1..3]->(b).",
        "O custo depende apenas da vizinhança visitada, não do total de linhas.",
    ], GREEN, 13)
    _add_table(
        s3, 0.6, 3.85, 12.133, 2.85,
        ["Profundidade (1 milhão de usuários)", "MySQL (Relacional)", "Neo4j (Grafo)", "Observação"],
        [
            ["Profundidade 2 (amigos de amigos)", "0,016 s", "0,010 s", "Ambos instantâneos"],
            ["Profundidade 3", "30,267 s", "0,168 s", "Neo4j ~180× mais rápido"],
            ["Profundidade 4", "1.543,505 s (~25,7 min)", "1,359 s", "SQL inviável para tempo real"],
            ["Profundidade 5", "Não terminou em 1 h (timeout)", "2,132 s", "Latência previsível no grafo"],
        ],
        font_size=12.5,
    )
    _add_notes(s3, "1,5 min. Comparar relação calculada na consulta (SQL JOIN) vs relação gravada como dado (Neo4j). Mostrar os números do benchmark do livro Neo4j in Action.")

    # SLIDE 4 · ONDE SE USA GRAFO
    s4 = prs.slides.add_slide(blank)
    _add_header_footer(s4, "Onde se Usa Grafo (e Comparativo da Aula 11)", "Tópico 1", 4, "*No Neo4j, leituras escalam horizontalmente; escritas passam pelo líder.")
    apps = [
        ("Redes Sociais", "Feeds, seguidores e grau de separação (ex.: Adobe Behance)."),
        ("Recomendação", "Filtragem colaborativa e por conteúdo em tempo real (ex.: Walmart)."),
        ("Detecção de Fraude", "Anéis de contas ligadas por IP, cartão ou dispositivo em milissegundos."),
        ("Grafos de Conhecimento", "Conexão semântica de dados corporativos (ex.: NASA, ICIJ)."),
        ("Redes, TI & Linhagem", "Impacto de falhas e catálogo de metadados (ex.: Lyft Amundsen)."),
        ("Logística & IAM", "Rotas otimizadas e controle hierárquico de permissões de acesso."),
    ]
    for i, (t, d) in enumerate(apps):
        col = i % 3
        row = i // 3
        _add_card(s4, 0.6 + col * 4.1, 1.15 + row * 1.45, 3.9, 1.3, t, [d], ROYAL, 12)
    _add_table(
        s4, 0.6, 4.2, 12.133, 2.55,
        ["Paradigma (Aula 11, Slide 32)", "Estrutura", "Melhor Uso", "Persistente", "Escalável", "CAP"],
        [
            ["Documentos (MongoDB)", "JSON / BSON", "Dados semiestruturados", "Sim", "Sim", "AP"],
            ["Família de Colunas (Cassandra)", "Famílias de colunas", "Grandes volumes e análises", "Sim", "Sim", "AP"],
            ["Grafos (Neo4j)", "Nós e arestas", "Relações complexas", "Sim", "Sim*", "CP"],
            ["Chave-Valor (Redis)", "Chave/valor em RAM", "Cache e acessos simples", "Opcional", "Sim", "AP ou CP"],
        ],
        font_size=12, highlight_row=2,
    )
    _add_notes(s4, "1 min. Apresentar aplicações típicas e conectar com a tabela comparativa dos 4 paradigmas da Aula 11 (Neo4j = CP).")

    # SLIDE 5 · NEO4J QUEM ONDE POR QUE
    s5 = prs.slides.add_slide(blank)
    _add_header_footer(s5, "2. Neo4j: Quem, Onde, Quando e Por Quê", "Tópico 2 · 2,0 pts", 5, "Fontes: Neo4j History & DB-Engines Graph DBMS Ranking")
    _add_card(s5, 0.6, 1.15, 5.9, 4.45, "Quem, Onde e Por Quê", [
        "Quem criou: Emil Eifrem, Johan Svensson e Peter Neubauer.",
        "Onde nasceu: Malmö, Suécia (empresa Neo4j, Inc. hoje em San Mateo/CA).",
        "Por quê: construíam um sistema de gestão de conteúdo (CMS) e o banco relacional travava com JOINs em dados muito conectados.",
        "Origem do nome: '4j' = for Java (motor escrito na JVM); esboçado em um guardanapo durante um voo para Mumbai em 2000.",
    ], ROYAL)
    _add_card(s5, 6.83, 1.15, 5.9, 4.45, "Linha do Tempo", [
        "2000: Protótipos iniciais desenvolvidos na Suécia.",
        "2007: Lançamento open-source e fundação da Neo Technology.",
        "2010 (fev): Versão 1.0 GA para produção.",
        "2011 / 2015: Criação do Cypher e abertura como openCypher.",
        "2024–Hoje: Cypher serviu de base (~95%) para a norma ISO/IEC 39075:2024 (GQL); líder no ranking DB-Engines.",
    ], TEAL)
    _add_callout(s5, 0.6, 5.8, 12.133, 0.9, "Resposta direta ao Barema: Criado em 2000 em Malmö (Suécia) por Emil Eifrem, Johan Svensson e Peter Neubauer para superar lentidão e rigidez de JOINs relacionais em redes de dados.")
    _add_notes(s5, "1,5 min. Responder explicitamente às perguntas do barema: por que foi desenvolvido, onde e quem desenvolveu.")

    # SLIDE 6 · NEO4J COMO OPERA
    s6 = prs.slides.add_slide(blank)
    _add_header_footer(s6, "Neo4j: Como Opera e Implementa o Paradigma", "Tópico 2 · Diagrama", 6, "Base: Neo4j Operations Manual, Graph Databases (Cap. 6) & Aula 11")
    _add_card(s6, 0.6, 1.15, 6.0, 5.65, "Mecanismos Internos", [
        "Armazenamento nativo: arquivos separados de tamanho fixo para nós, relacionamentos e propriedades.",
        "Index-free adjacency: cada nó aponta direto para seus relacionamentos; cada salto tem custo constante O(1), independente do tamanho do banco.",
        "Grafo de propriedades: nós com rótulos + relacionamentos direcionados com 1 tipo e propriedades.",
        "Cypher & ISO GQL: consulta declarativa em ASCII art; base da ISO/IEC 39075:2024.",
        "Transações ACID completas e esquema opcional com constraints.",
        "Cluster (Enterprise/Aura): escritas no líder via Raft; réplicas para leitura → CAP = CP.",
    ], ROYAL, 12.5)

    # Diagrama comparativo no lado direito do Slide 6
    diag_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.83), Inches(1.15), Inches(5.9), Inches(5.65))
    diag_box.fill.solid()
    diag_box.fill.fore_color.rgb = LIGHT_BG
    diag_box.line.color.rgb = BORDER

    dt = s6.shapes.add_textbox(Inches(7.0), Inches(1.25), Inches(5.55), Inches(0.4))
    dp = dt.text_frame.paragraphs[0]
    dp.text = "Index-Free Adjacency (Neo4j) vs. JOIN (Relacional)"
    dp.alignment = PP_ALIGN.CENTER
    dp.font.size = Pt(14.5)
    dp.font.bold = True
    dp.font.color.rgb = NAVY

    _add_node(s6, 7.8, 2.65, 0.55, "Ana", "u01", TEAL)
    _add_node(s6, 11.4, 2.65, 0.55, "Matrix", "f01", ROYAL)
    edge = s6.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(8.45), Inches(2.5), Inches(2.3), Inches(0.3))
    edge.fill.solid()
    edge.fill.fore_color.rgb = DARK
    edge.line.fill.background()
    el = s6.shapes.add_textbox(Inches(8.55), Inches(2.15), Inches(2.1), Inches(0.32))
    elp = el.text_frame.paragraphs[0]
    elp.text = "[:ASSISTIU {nota:5}]"
    elp.alignment = PP_ALIGN.CENTER
    elp.font.size = Pt(10.5)
    elp.font.bold = True
    elp.font.color.rgb = DARK

    gtxt = s6.shapes.add_textbox(Inches(7.1), Inches(3.35), Inches(5.35), Inches(0.55))
    gp = gtxt.text_frame.paragraphs[0]
    gp.text = "Neo4j: ponteiro físico direto em RAM/disco → salto O(1)"
    gp.alignment = PP_ALIGN.CENTER
    gp.font.size = Pt(12)
    gp.font.bold = True
    gp.font.color.rgb = GREEN

    _add_table(
        s6, 7.1, 4.15, 5.35, 2.35,
        ["Relacional (SQL)", "Operação no Disco / Índice"],
        [
            ["Tabela USUARIO", "Busca PK 'u01' em índice B-tree"],
            ["Tabela ASSISTIU (JOIN)", "Varre índice FK → acha 'f01'"],
            ["Tabela FILME (JOIN)", "Nova busca PK 'f01' em B-tree"],
        ],
        font_size=11.5,
    )
    _add_notes(s6, "2 min. Explicar index-free adjacency com o diagrama: seguir ponteiro direto vs busca em índices B-tree por JOIN. Reforçar ACID e CP.")

    # SLIDE 7 · HARDWARE E EDICOES
    s7 = prs.slides.add_slide(blank)
    _add_header_footer(s7, "Neo4j: Hardware, Edições e Ecossistema", "Tópico 2", 7, "Fonte: Neo4j Operations Manual (System Requirements) & AuraDB Docs")
    _add_card(s7, 0.6, 1.15, 6.2, 5.65, "Requisitos de Hardware (Operations Manual)", [
        "JVM: Java 17 (Neo4j 5.x) ou Java 21 (versões recentes 2025.x).",
        "RAM — Heap da JVM: execução de consultas e transações (server.memory.heap.max_size; manter initial = max e < ~32 GB).",
        "RAM — Page Cache (off-heap): mantém arquivos do grafo em RAM (server.memory.pagecache.size; ideal = tamanho do grafo ativo).",
        "Comando oficial: neo4j-admin server memory-recommendation.",
        "Disco SSD / NVMe: fundamental em produção pois seguir ponteiros fora do cache gera leitura aleatória.",
        "Porte: notebook com 8 GB de RAM roda a demo; produção usa dezenas de GB.",
    ], ROYAL, 12.5)
    _add_table(
        s7, 7.05, 1.15, 5.68, 2.75,
        ["Edição", "Licença / Modelo", "Destaque"],
        [
            ["Community", "Gratuita (GPLv3)", "1 servidor; suficiente para o projeto"],
            ["Enterprise", "Comercial", "Cluster Raft, backup a quente, RBAC"],
            ["AuraDB Free", "Nuvem (DBaaS)", "Gratuita; pausa após 72 h sem escrita"],
        ],
        font_size=12,
    )
    _add_card(s7, 7.05, 4.15, 5.68, 2.65, "Ferramentas do Ecossistema", [
        "Neo4j Browser: console Cypher + visualização interativa (nossa demo).",
        "Neo4j Bloom: exploração visual sem código para analistas.",
        "Graph Data Science (GDS): algoritmos (PageRank, similaridade, comunidades).",
        "APOC: biblioteca oficial de procedimentos e integrações.",
    ], TEAL, 12.5)
    _add_notes(s7, "1 min. Detalhar hardware (JVM, Heap + Page Cache + SSD) e as 3 edições (Community, Enterprise e AuraDB Free com pausa em 72h).")

    # SLIDE 8 · QUEM USA
    s8 = prs.slides.add_slide(blank)
    _add_header_footer(s8, "3. Aplicações Reais no Mercado (neo4j.com/customers)", "Tópico 3 · Obrigatório", 8, "Fonte: Neo4j Customer Case Studies")
    cases = [
        ("Walmart", "Recomendação de produtos em tempo real no e-commerce, substituindo lotes relacionais lentos."),
        ("eBay", "Grafo de conhecimento para assistente conversacional de compras (ShopBot) e roteamento."),
        ("NASA", "Base Lessons Learned conectando décadas de relatórios e competências para missões (Marte)."),
        ("ICIJ (Panama Papers)", "Jornalismo investigativo ligando empresas offshore, pessoas e endereços em horas."),
        ("Lyft (Amundsen)", "Catálogo de descoberta e linhagem de metadados usando Neo4j e PageRank."),
        ("Adobe (Behance)", "Feed de atividades e conexões para +18 milhões de criativos em tempo real."),
    ]
    for i, (emp, desc) in enumerate(cases):
        col = i % 3
        row = i // 3
        _add_card(s8, 0.6 + col * 4.1, 1.15 + row * 2.25, 3.9, 2.05, emp, [desc], ROYAL if row == 0 else TEAL, 13)
    _add_callout(s8, 0.6, 5.8, 12.133, 0.9, "Importante: Netflix e Spotify são apenas os exemplos de tipo de sistema do enunciado. Não afirmamos que usam Neo4j; o caso real confirmado de recomendação com Neo4j é o Walmart.")
    _add_notes(s8, "1 min. Apresentar os 6 casos confirmados e reforçar que não afirmamos que Netflix ou Spotify usam Neo4j.")

    # SLIDE 9 · VANTAGENS
    s9 = prs.slides.add_slide(blank)
    _add_header_footer(s9, "4. Principais Vantagens (Motivos para Usar)", "Tópico 4 · 1,0 pt", 9)
    vantagens = [
        ("1. Consultas Multissaltos Rápidas", "Index-free adjacency garante tempo estável mesmo com 3 a 5+ saltos (benchmark Slide 3)."),
        ("2. Modelagem Natural", "Modelo whiteboard-friendly: o desenho conceitual vai direto para o grafo, sem tabelas N:N."),
        ("3. Esquema Flexível (Schema-Optional)", "Novos campos, nós e relações entram on the fly sem ALTER TABLE (demonstrado em U2)."),
        ("4. Cypher Legível", "Padrões visuais substituem múltiplos JOINs SQL complexos."),
        ("5. Transações ACID e Integridade", "Impede arestas órfãs (D1a) e garante unicidade por constraints com rollback atômico (C1)."),
        ("6. Ecossistema Maduro", "Browser visual, Bloom, GDS, drivers oficiais (Python, Java, JS, Go, .NET) e AuraDB Free."),
    ]
    for i, (t, d) in enumerate(vantagens):
        col = i % 2
        row = i // 2
        _add_card(s9, 0.6 + col * 6.23, 1.15 + row * 1.9, 5.9, 1.7, t, [d], GREEN, 13)
    _add_notes(s9, "1,5 min. Conectar as vantagens diretamente com o que será demonstrado ao vivo (U2, C1, D1a).")

    # SLIDE 10 · DESVANTAGENS
    s10 = prs.slides.add_slide(blank)
    _add_header_footer(s10, "5. Principais Desvantagens (Motivos para Evitar)", "Tópico 5 · 1,0 pt", 10)
    desv = [
        ("1. Escrita e Sharding Difíceis", "Nuance Aula 11 (Slide 30): leitura escala em réplicas, mas escrita passa pelo líder Raft e sharding automático quebra travessias."),
        ("2. Fraco para Dados Tabulares / OLAP", "Agregações em massa sobre milhões de linhas são mais rápidas em SQL ou bancos colunares (Aula 11, Slide 31)."),
        ("3. Supernós (Supernodes)", "Nós com milhões de ligações (ex.: gênero 'Drama') geram gargalo de travessia."),
        ("4. Dependência de Memória RAM", "Exige page cache grande para manter o grafo ativo em memória e evitar I/O aleatório."),
        ("5. Recursos Avançados Pagos", "Cluster Raft, backup a quente e segurança RBAC fina ficam apenas na edição Enterprise."),
        ("6. Curva de Aprendizado & Blobs", "Exige domínio de Cypher/grafos e não serve para armazenar vídeos, imagens ou logs brutos."),
    ]
    for i, (t, d) in enumerate(desv):
        col = i % 2
        row = i // 2
        _add_card(s10, 0.6 + col * 6.23, 1.15 + row * 1.9, 5.9, 1.7, t, [d], RED, 13)
    _add_notes(s10, "1,5 min. Destacar a nuance do item 1 em relação ao slide 30 da aula (leitura escala horizontalmente; escrita vai ao líder).")

    # SLIDE 11 · RECOMENDACAO = PERCORRER RELACOES
    s11 = prs.slides.add_slide(blank)
    _add_header_footer(s11, "6. Sistema de Recomendação = Percorrer Relações", "Tópico 6 · 1,0 pt", 11, "Mensagem: cada salto extra no recomendador vira mais um JOIN no SQL.")
    _add_card(s11, 0.6, 1.12, 3.9, 1.5, "Colaborativa (R1)", ["3 saltos: Ana → Matrix ← Bruno → Interestelar (notas >= 4)."], ROYAL, 12)
    _add_card(s11, 4.71, 1.12, 3.9, 1.5, "Por Conteúdo (R3)", ["Atributos: Ana → A Origem ← DiCaprio → Titanic."], TEAL, 12)
    _add_card(s11, 8.83, 1.12, 3.9, 1.5, "Híbrida & Cold Start (R4)", ["Combina sinais + GDS; popularidade para usuário novo."], PURPLE, 12)

    cypher_r1 = (
        "MATCH (alvo:Usuario {usuarioId:'u01'})-[r1:ASSISTIU]->(f:Filme)<-[r2:ASSISTIU]-(outro:Usuario)\n"
        "WHERE r1.nota >= 4 AND r2.nota >= 4\n"
        "WITH alvo, outro, count(f) AS emComum\n"
        "MATCH (outro)-[r3:ASSISTIU]->(rec:Filme)\n"
        "WHERE r3.nota >= 4 AND NOT EXISTS { (alvo)-[:ASSISTIU]->(rec) }\n"
        "RETURN rec.titulo AS recomendacao, count(DISTINCT outro) AS usuariosParecidos,\n"
        "       sum(emComum) AS forca, round(avg(r3.nota), 1) AS notaMedia\n"
        "ORDER BY forca DESC, notaMedia DESC, recomendacao LIMIT 5;"
    )
    sql_r1 = (
        "SELECT f.titulo, COUNT(DISTINCT a2.usuario_id) AS usuarios_parecidos\n"
        "FROM assistiu a1\n"
        "JOIN assistiu a2 ON a2.filme_id = a1.filme_id AND a2.usuario_id <> a1.usuario_id\n"
        "JOIN assistiu a3 ON a3.usuario_id = a2.usuario_id\n"
        "JOIN filme f     ON f.filme_id = a3.filme_id\n"
        "WHERE a1.usuario_id = 'u01'\n"
        "  AND a1.nota >= 4 AND a2.nota >= 4 AND a3.nota >= 4\n"
        "  AND a3.filme_id NOT IN (SELECT filme_id FROM assistiu WHERE usuario_id = 'u01')\n"
        "GROUP BY f.titulo ORDER BY usuarios_parecidos DESC;"
    )
    _add_code_box(s11, 0.6, 2.8, 5.9, 3.95, "Consulta R1 em Cypher", cypher_r1)
    _add_code_box(s11, 6.83, 2.8, 5.9, 3.95, "Equivalente em SQL (3 JOINs na mesma tabela)", sql_r1)
    _add_notes(s11, "2 min. Abrir citando a Aula 11 (Slide 31 lista recomendação como uso ideal do Neo4j). Comparar Cypher com o SQL de 3 self-JOINs.")

    # SLIDE 12 · NEO4J NA RECOMENDACAO PROS E CONTRAS
    s12 = prs.slides.add_slide(blank)
    _add_header_footer(s12, "Neo4j na Recomendação: Adequação, Prós e Contras", "Tópico 6", 12)
    _add_card(s12, 0.6, 1.15, 5.9, 4.4, "Vantagens no Contexto", [
        "Tempo real: percorre apenas a vizinhança do usuário a cada clique.",
        "Explicável (R2): o caminho retorna a justificativa ('porque você viu Matrix').",
        "Novidade instantânea (C1 → R1): filme novo entra e já é recomendado.",
        "Novos sinais sem migração: seguir amigo ou lista entra como nova aresta.",
        "Caso real confirmado: Walmart usa Neo4j em recomendações.",
    ], GREEN, 13)
    _add_card(s12, 6.83, 1.15, 5.9, 4.4, "Desvantagens e Limites no Contexto", [
        "Volume de eventos: bilhões de plays brutos ficam em Kafka/Cassandra; no grafo entra só a relação resumida (assistiu, nota).",
        "Supernós: sucessos globais ou gêneros amplos exigem filtros e limites.",
        "Cold start: usuário sem histórico exige fallback por popularidade (R4).",
        "ML pesado (redes neurais/matrizes) roda fora do banco e complementa o grafo.",
    ], RED, 13)
    _add_callout(s12, 0.6, 5.75, 12.133, 0.98, "Como se adequa: Os dados de recomendação são naturalmente uma rede de usuários, filmes, gêneros e atores. O Neo4j armazena essa rede como ela é e responde 'o que recomendar e por quê' em poucos saltos, dentro de uma arquitetura poliglota.")
    _add_notes(s12, "2 min. Responder explicitamente ao critério 'Explicar em detalhes como o BD escolhido se adequa a esse sistema'.")

    # SLIDE 13 · NOSSO MODELO
    s13 = prs.slides.add_slide(blank)
    _add_header_footer(s13, "Aplicação Prática: Nosso Modelo de Grafo", "CRUD · 5,0 pts", 13, "Diagrama importável em Arrows.app: apresentacao/modelo-arrows.json")
    model_box = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.15), Inches(6.2), Inches(5.6))
    model_box.fill.solid()
    model_box.fill.fore_color.rgb = LIGHT_BG
    model_box.line.color.rgb = BORDER

    mt = s13.shapes.add_textbox(Inches(0.75), Inches(1.25), Inches(5.9), Inches(0.4))
    mp = mt.text_frame.paragraphs[0]
    mp.text = "Modelo de Dados (Streaming de Filmes)"
    mp.alignment = PP_ALIGN.CENTER
    mp.font.size = Pt(15)
    mp.font.bold = True
    mp.font.color.rgb = NAVY

    _add_node(s13, 1.55, 2.85, 0.62, ":Usuario", "id, nome, plano", TEAL)
    _add_node(s13, 3.7, 2.85, 0.65, ":Filme", "id, titulo, ano, min", ROYAL)
    _add_node(s13, 5.85, 2.85, 0.58, ":Genero", "nome", AMBER)
    _add_node(s13, 3.7, 5.15, 0.58, ":Ator", "nome", PURPLE)

    a1 = s13.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(2.25), Inches(2.74), Inches(0.75), Inches(0.22))
    a1.fill.solid(); a1.fill.fore_color.rgb = DARK; a1.line.fill.background()
    t1 = s13.shapes.add_textbox(Inches(2.1), Inches(2.38), Inches(1.1), Inches(0.3))
    t1.text_frame.paragraphs[0].text = "ASSISTIU {nota}"
    t1.text_frame.paragraphs[0].font.size = Pt(9.5)
    t1.text_frame.paragraphs[0].font.bold = True

    a2 = s13.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.42), Inches(2.74), Inches(0.8), Inches(0.22))
    a2.fill.solid(); a2.fill.fore_color.rgb = DARK; a2.line.fill.background()
    t2 = s13.shapes.add_textbox(Inches(4.32), Inches(2.38), Inches(1.0), Inches(0.3))
    t2.text_frame.paragraphs[0].text = "DO_GENERO"
    t2.text_frame.paragraphs[0].font.size = Pt(9.5)
    t2.text_frame.paragraphs[0].font.bold = True

    a3 = s13.shapes.add_shape(MSO_SHAPE.UP_ARROW, Inches(3.59), Inches(3.6), Inches(0.22), Inches(0.9))
    a3.fill.solid(); a3.fill.fore_color.rgb = DARK; a3.line.fill.background()
    t3 = s13.shapes.add_textbox(Inches(3.9), Inches(3.95), Inches(1.0), Inches(0.3))
    t3.text_frame.paragraphs[0].text = "ATUOU_EM"
    t3.text_frame.paragraphs[0].font.size = Pt(9.5)
    t3.text_frame.paragraphs[0].font.bold = True

    _add_card(s13, 7.05, 1.15, 5.68, 5.6, "Volume do Dataset & Decisões", [
        "39 Nós: 8 :Usuario · 12 :Filme · 7 :Genero · 12 :Ator.",
        "67 Relacionamentos: 26 :ASSISTIU · 22 :DO_GENERO · 19 :ATUOU_EM.",
        "4 Restrições UNIQUE: usuario_id, filme_id, genero_nome, ator_nome.",
        "Nota na aresta (:ASSISTIU): exemplo direto de propriedade em relacionamento.",
        "Gênero e Ator como nós: viram caminhos percorríveis na consulta R3.",
        "Fora do escopo (extensões sem migração): diretor, séries, amigos.",
    ], ROYAL, 13)
    _add_notes(s13, "1 min. Mostrar a estrutura simples e legível que permite demonstrar recomendação colaborativa, por conteúdo e todas as operações CRUD.")

    # SLIDE 14 · DEMO AO VIVO
    s14 = prs.slides.add_slide(blank)
    _add_header_footer(s14, "Demo ao Vivo no Neo4j Browser (6 min)", "CRUD · 5,0 pts", 14, "Regra de ouro: rodar só pelos favoritos salvos no Browser (ou usar slides-interativos.html como ensaio).")
    _add_table(
        s14, 0.6, 1.12, 12.133, 5.65,
        ["Passo", "ID", "Operação CRUD", "Resultado / Mensagem Didática na Apresentação"],
        [
            ["1", "R0", "Read (Grafo)", "Mostra 39 nós e 67 setas: não há tabelas nem chaves estrangeiras."],
            ["2", "R1", "Read (Colaborativa)", "Ana recebe Interestelar (força 3, 4.5) e O Lobo de Wall Street (força 1, 4.0)."],
            ["3", "R2", "Read (Caminhos)", "Exibe os 3 caminhos que justificam Interestelar (via Bruno e Diego)."],
            ["4", "C1", "Create", "Insere Duna (f13), Timothée Chalamet e 4 relações (+ teste UNIQUE se repetido)."],
            ["5", "R1", "Read", "Duna assume o 1º lugar na hora (média 5.0), sem reprocessar lote."],
            ["6", "U1", "Update (Aresta)", "Diego muda nota de O Lobo de Wall Street para 2."],
            ["7", "R1", "Read", "O Lobo de Wall Street desaparece da recomendação em tempo real."],
            ["8", "U2", "Update (Nó)", "Ana muda para Premium e ganha campo atualizadoEm sem ALTER TABLE."],
            ["9–10", "D1a / D1b", "Delete", "DELETE simples falha (sem aresta órfã); DETACH DELETE apaga Duna + 4 ligações."],
            ["11–12", "R1 / R3", "Read", "Volta a restar só Interestelar; R3 mostra recomendação por gênero/ator."],
        ],
        font_size=11.5,
    )
    _add_notes(s14, "6 min. Trocar para o Neo4j Browser (zoom 150%) com o seed rodado e favoritos na ordem. Em caso de queda de ambiente, usar AuraDB ou o simulador em slides-interativos.html.")

    # SLIDE 15 · CONCLUSAO E REFERENCIAS
    s15 = prs.slides.add_slide(blank)
    _add_header_footer(s15, "Conclusão e Referências", "Encerramento", 15, "Obrigado! Aberto para perguntas da professora e da turma.")
    _add_callout(
        s15, 0.6, 1.2, 12.133, 1.15,
        "\"Grafo não substitui o relacional. É a escolha certa quando o valor está nas relações — e recomendação é exatamente isso.\"",
        font_size=18,
    )
    _add_card(s15, 0.6, 2.6, 5.9, 4.15, "Resumo da Entrega", [
        "Paradigma de grafo e comparação com SQL (benchmark + JOINs).",
        "História, operação (index-free adjacency, ACID, CP) e hardware do Neo4j.",
        "6 casos reais de mercado + vantagens, desvantagens e adequação à recomendação.",
        "CRUD completo ao vivo (C1, R0–R4, U1, U2, D1a, D1b).",
    ], GREEN, 13)
    _add_card(s15, 6.83, 2.6, 5.9, 4.15, "Referências Verificadas", [
        "Aula 11 · NoSQL (Profa. Ana Maria Quevedo / Prof. Alan Carlos) & Enunciado Projeto 3 (26.2).",
        "ROBINSON, I.; WEBBER, J.; EIFREM, E. Graph Databases. 2. ed. O'Reilly, 2015.",
        "VUKOTIC, A. et al. Neo4j in Action. Manning, 2014 (Cap. 1).",
        "Neo4j Docs (Operations Manual, Cypher Manual, AuraDB Docs) & neo4j.com/customers.",
        "ISO/IEC 39075:2024 (GQL) & DB-Engines Graph DBMS Ranking.",
    ], ROYAL, 12)
    _add_notes(s15, "0,5 min. Encerrar com a frase síntese e abrir para perguntas da professora (respostas prontas em apresentacao/01-slides.md).")

    prs.save(str(OUT_PPTX))
    return OUT_PPTX


if __name__ == "__main__":
    out = build_presentation()
    print(f"PPTX gerado com sucesso: {out}")
