"""
Componentes visuais reutilizáveis: cabeçalho, cartão de KPI com sparkline,
cartão de gráfico com menu "⋯" (Ver dados / Exportar CSV), tabelas HTML com
formatação condicional, estado vazio e rodapé.
"""

from __future__ import annotations

import html
from typing import Callable, Iterable

import pandas as pd
import streamlit as st

from core import nav
from core.data import HOJE
from core.theme import (
    BORDER, CRIT, INFO, MUTED, ORANGE, POS, PLOTLY_CONFIG, SURFACE2, TEXT, YELLOW,
    data_br, icon, pct, rgba,
)


# ----------------------------------------------------------------------------
# CABEÇALHO / RODAPÉ
# ----------------------------------------------------------------------------
def header(titulo: str, subtitulo: str):
    c1, c2 = st.columns([5, 1.25], vertical_alignment="center")
    with c1:
        st.markdown(
            f"""<div class="co-header">
                <div><p class="co-title">{titulo}</p><p class="co-sub">{subtitulo}</p></div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div style="display:flex;justify-content:flex-end"><span class="co-badge"><span class="co-dot"></span>'
            f'Atualizado <b>{data_br(HOJE)}</b></span></div>',
            unsafe_allow_html=True,
        )


def footer():
    st.markdown(
        '<div class="co-footer">Desenvolvido por <b>Datalyse</b> · Dados fictícios para demonstração</div>',
        unsafe_allow_html=True,
    )


def empty(msg: str = "Sem dados para os filtros selecionados"):
    st.markdown(f'<div class="empty">{icon("inbox", 30, MUTED, 1.5)}<span>{msg}</span></div>',
                unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# KPI
# ----------------------------------------------------------------------------
def sparkline(values: Iterable[float], color: str = ORANGE) -> str:
    vals = [float(v) for v in values if v is not None and not pd.isna(v)]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1.0
    w, h = 100, 30
    pts = [(i * w / (len(vals) - 1), h - 3 - (v - lo) / rng * (h - 6)) for i, v in enumerate(vals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"0,{h} " + line + f" {w},{h}"
    gid = f"g{abs(hash((tuple(vals), color))) % 10**8}"
    return (
        f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" width="100%" height="34">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{color}" stop-opacity=".35"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>'
        f'</linearGradient></defs><polygon points="{area}" fill="url(#{gid})"/>'
        f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="1.6" vector-effect="non-scaling-stroke"/></svg>'
    )


def delta_html(delta: float | None, comp: str | None, inverso: bool = False, pp: bool = False) -> str:
    if comp is None:
        return '<span title="O período de comparação começa antes de jan/2025, início da base">— comparação indisponível</span>'
    if delta is None or pd.isna(delta):
        return f'<span>— sem base de comparação</span>'
    bom = delta >= 0 if not inverso else delta <= 0
    seta = "▲" if delta >= 0 else "▼"
    if pp:
        txt = f"{delta * 100:+.1f} p.p.".replace(".", ",")
    else:
        txt = pct(abs(delta))
    return f'<span class="{"up" if bom else "down"}">{seta} {txt}</span> vs {comp}'


def kpi(key: str, label: str, valor: str, ico: str, *, delta: float | None = None, comp: str | None = "período anterior",
        inverso: bool = False, pp: bool = False, spark: Iterable[float] | None = None, info: str = "",
        tom: str = "", link: str | None = None, nota: str | None = None):
    with st.container(key=f"kpi_{key}"):
        d = nota if nota is not None else delta_html(delta, comp, inverso, pp)
        sp = sparkline(spark, CRIT if tom == "crit" else (YELLOW if tom in ("warn", "hl") else ORANGE)) if spark is not None else ""
        info_html = f'<span class="kpi-info" title="{html.escape(info)}">i</span>' if info else ""
        st.markdown(
            f"""<div class="kpi">
                <div class="kpi-top">{icon(ico, 20)}<span class="kpi-label">{label}</span>{info_html}</div>
                <div class="kpi-value {tom}">{valor}</div>
                <div class="kpi-delta">{d}</div>
                <div class="kpi-spark">{sp}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        if link and link in nav.PAGES:
            st.page_link(nav.PAGES[link], label=label)


def kpi_row(n: int = 6):
    return st.columns(n, gap="small")


# ----------------------------------------------------------------------------
# CARTÃO DE GRÁFICO
# ----------------------------------------------------------------------------
def _menu(key: str, data: pd.DataFrame | None, png: bool = True):
    with st.popover("⋯", use_container_width=False):
        st.markdown("**Ver dados**")
        if data is None or data.empty:
            st.caption("Sem dados para exibir.")
        else:
            st.dataframe(data, hide_index=True, use_container_width=True, height=min(360, 38 + 35 * len(data)))
            st.download_button(
                "Exportar CSV", data.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                file_name=f"casa_obra_{key}.csv", mime="text/csv", key=f"csv_{key}", use_container_width=True,
            )
        if png:
            st.caption("Exportar PNG: use o ícone de câmera que aparece ao passar o mouse sobre o gráfico.")


def card_header(key: str, titulo: str, sub: str = "", data: pd.DataFrame | None = None, png: bool = True):
    c1, c2 = st.columns([12, 1], vertical_alignment="top")
    with c1:
        st.markdown(f'<p class="card-title">{titulo}</p><p class="card-sub">{sub}</p>', unsafe_allow_html=True)
    with c2:
        _menu(key, data, png)


def chart(key: str, titulo: str, sub: str, fig, data: pd.DataFrame | None = None,
          on_select: Callable | None = None, sel_key: str | None = None):
    """Desenha um gráfico Plotly dentro de um cartão. Se `on_select` for dado,
    clicar num ponto chama o callback (filtro cruzado)."""
    with st.container(key=f"card_{key}"):
        card_header(key, titulo, sub, data)
        if fig is None:
            empty()
            return
        cfg = dict(PLOTLY_CONFIG)
        cfg["toImageButtonOptions"] = {**PLOTLY_CONFIG["toImageButtonOptions"], "filename": f"casa_obra_{key}"}
        if on_select is not None:
            st.plotly_chart(fig, key=sel_key or f"pl_{key}", config=cfg, on_select=on_select,
                            selection_mode="points", use_container_width=True)
        else:
            st.plotly_chart(fig, key=f"pl_{key}", config=cfg, use_container_width=True)


def html_card(key: str, titulo: str, sub: str, body: str, data: pd.DataFrame | None = None, png: bool = False):
    with st.container(key=f"card_{key}"):
        card_header(key, titulo, sub, data, png)
        st.markdown(body, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# TABELAS HTML
# ----------------------------------------------------------------------------
def pill(txt: str, tom: str) -> str:
    return f'<span class="pill {tom}">{html.escape(str(txt))}</span>'


def bar_cell(txt: str, frac: float, color: str = ORANGE) -> str:
    frac = max(0.0, min(1.0, float(frac) if frac == frac else 0.0))
    return (
        f'<div style="position:relative;min-width:110px">'
        f'<div style="position:absolute;left:0;top:2px;bottom:2px;width:{frac * 100:.1f}%;'
        f'background:{rgba(color, .28)};border-radius:4px"></div>'
        f'<span style="position:relative;padding-left:6px">{txt}</span></div>'
    )


def table(df: pd.DataFrame, align: dict[str, str] | None = None, max_height: int = 420) -> str:
    """Tabela HTML com cabeçalho fixo. As células já devem vir formatadas
    (podem conter HTML: pílulas, barras inline, sparklines)."""
    align = align or {}
    th = "".join(
        f'<th style="text-align:{align.get(c, "left")}">{html.escape(str(c))}</th>' for c in df.columns
    )
    rows = []
    for _, r in df.iterrows():
        tds = "".join(f'<td style="text-align:{align.get(c, "left")}">{r[c]}</td>' for c in df.columns)
        rows.append(f"<tr>{tds}</tr>")
    return f"""
    <div style="max-height:{max_height}px;overflow:auto;border-radius:10px;border:1px solid {BORDER}">
    <table style="width:100%;border-collapse:collapse;font-size:12.5px;font-variant-numeric:tabular-nums">
      <thead style="position:sticky;top:0;background:{SURFACE2};z-index:1">
        <tr style="color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:.06em">{th}</tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table></div>
    <style>
      table td, table th {{ padding:7px 10px; border-bottom:1px solid {BORDER}; color:{TEXT}; white-space:nowrap; }}
      table tbody tr:hover {{ background:{rgba(ORANGE, .06)}; }}
    </style>
    """


def hbar(labels, values, textos, cores=None, height: int = 340, hover: str | None = None, customdata=None,
         rank: bool = False):
    """Barras horizontais ordenadas do maior (topo) para o menor, com rótulo na ponta."""
    import plotly.graph_objects as go
    from core.theme import style

    labels, values, textos = list(labels), list(values), list(textos)
    if rank:
        labels = [f"{i + 1}º  {l}" for i, l in enumerate(labels)]
    cores = cores if cores is not None else ORANGE
    fig = go.Figure(go.Bar(
        y=labels[::-1], x=values[::-1], orientation="h",
        marker=dict(color=cores[::-1] if isinstance(cores, list) else cores, cornerradius=6),
        text=textos[::-1], textposition="outside", cliponaxis=False, textfont=dict(size=11, color=TEXT),
        customdata=customdata[::-1] if customdata is not None else None,
        hovertemplate=hover or "<b>%{y}</b><br>%{text}<extra></extra>",
    ))
    style(fig, height, legend=False)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)", showticklabels=False, rangemode="tozero")
    fig.update_yaxes(showgrid=False, ticksuffix="  ", automargin=True)
    if values:
        fig.update_xaxes(range=[0, max(values) * 1.28])
    return fig


def tone_meta(frac: float | None) -> str:
    if frac is None or pd.isna(frac):
        return "info"
    return "pos" if frac >= 1 else ("warn" if frac >= 0.85 else "crit")


TONS = {"pos": POS, "warn": YELLOW, "crit": CRIT, "info": INFO}
