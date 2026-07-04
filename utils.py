"""
Casa&Obra — Painel de Vendas
Funções utilitárias: carga de dados, tokens de estilo e helpers de formatação.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# TOKENS DE DESIGN — tema escuro, identidade Casa&Obra
# ----------------------------------------------------------------------------
COLORS = {
    "orange": "#E8752E",        # Casa
    "orange_light": "#FF9E5E",
    "orange_dark": "#B85422",
    "lime": "#E4F222",          # &Obra
    "lime_dark": "#A7B81A",
    "navy": "#0B1220",           # fundo geral (bem escuro)
    "surface": "#141B2D",        # cartões
    "surface_alt": "#1B2438",    # hover / linhas alternadas
    "slate": "#3C536B",
    "slate_light": "#6E8CAE",
    "card": "#141B2D",
    "text": "#F2F4F8",
    "muted": "#8A93A6",
    "border": "rgba(255,255,255,0.08)",
    "success": "#3ED598",
    "danger": "#FF5C7A",
}

# Paleta categórica derivada das cores da marca (ordem fixa e sempre consistente)
CATEGORY_PALETTE = [
    COLORS["orange"], COLORS["lime"], COLORS["slate_light"],
    COLORS["orange_light"], COLORS["lime_dark"], COLORS["slate"],
    COLORS["orange_dark"],
]

FONT_DISPLAY = "'Archivo Black', 'Arial Black', sans-serif"
FONT_BODY = "'Work Sans', 'Segoe UI', sans-serif"
FONT_MONO = "'IBM Plex Mono', 'Courier New', monospace"

DATA_PATH = "data/vendas.xlsx"

# Páginas do painel: (rótulo com ícone, chave interna usada em st.session_state)
PAGINAS = [
    ("🏠 Início", "Início"),
    ("📊 Análise de Vendas", "Análise de Vendas"),
    ("🧑‍🔧 Vendas por Vendedor", "Vendas por Vendedor"),
    ("🧱 Vendas por Produtos", "Vendas por Produtos"),
]


@st.cache_data(show_spinner=False)
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_excel(path)
    df["Data_Venda"] = pd.to_datetime(df["Data_Venda"])
    df["Ano"] = df["Data_Venda"].dt.year
    df["MesNum"] = df["Data_Venda"].dt.month
    df["AnoMes"] = df["Data_Venda"].dt.to_period("M").dt.to_timestamp()
    df["Margem"] = df["Valor_Total"] - (df["Custo_Unitário"] * df["Quantidade"])
    return df


def fmt_moeda(v: float) -> str:
    if v is None or pd.isna(v):
        return "R$ 0,00"
    s = f"R$ {v:,.2f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".")


def fmt_num(v: float, casas: int = 0) -> str:
    if v is None or pd.isna(v):
        return "0"
    s = f"{v:,.{casas}f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".")


def fmt_pct(v: float) -> str:
    if v is None or pd.isna(v):
        return "0%"
    return f"{v:.1f}%".replace(".", ",")


MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

MESES_PT_EXT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
    7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}

DIAS_PT_EXT = {
    0: "segunda-feira", 1: "terça-feira", 2: "quarta-feira", 3: "quinta-feira",
    4: "sexta-feira", 5: "sábado", 6: "domingo",
}


def hora_brasil() -> datetime:
    """Retorna o horário atual no fuso de Brasília (America/Sao_Paulo)."""
    return datetime.now(ZoneInfo("America/Sao_Paulo"))


def saudacao_br(agora: datetime | None = None) -> str:
    """Bom dia / Boa tarde / Boa noite, de acordo com o horário de Brasília."""
    agora = agora or hora_brasil()
    h = agora.hour
    if 5 <= h < 12:
        return "Bom dia"
    if 12 <= h < 18:
        return "Boa tarde"
    return "Boa noite"


def data_extenso_br(agora: datetime | None = None) -> str:
    agora = agora or hora_brasil()
    dia_semana = DIAS_PT_EXT[agora.weekday()]
    texto = f"{dia_semana}, {agora.day} de {MESES_PT_EXT[agora.month]} de {agora.year}"
    return texto[0].upper() + texto[1:]


def get_filter_state(df: pd.DataFrame):
    """Lê o estado atual dos filtros a partir do session_state (com valores
    padrão para a primeira execução). Os widgets em si são desenhados mais
    tarde, dentro de cada página — isso permite calcular os KPIs já filtrados
    antes de renderizar os controles de filtro na tela."""
    data_min, data_max = df["Data_Venda"].min().date(), df["Data_Venda"].max().date()
    periodo = st.session_state.get("flt_periodo", (data_min, data_max))
    if isinstance(periodo, tuple) and len(periodo) == 2:
        data_ini, data_fim = periodo
    else:
        data_ini, data_fim = data_min, data_max
    categorias = st.session_state.get("flt_categorias", [])
    vendedores = st.session_state.get("flt_vendedores", [])
    formas = st.session_state.get("flt_formas", [])
    return data_ini, data_fim, categorias, vendedores, formas


def apply_filters(df: pd.DataFrame, data_ini, data_fim, categorias, vendedores, formas) -> pd.DataFrame:
    mask = (
        (df["Data_Venda"] >= pd.Timestamp(data_ini))
        & (df["Data_Venda"] <= pd.Timestamp(data_fim))
    )
    if categorias:
        mask &= df["Categoria"].isin(categorias)
    if vendedores:
        mask &= df["Vendedor"].isin(vendedores)
    if formas:
        mask &= df["Forma_Pagamento"].isin(formas)
    return df.loc[mask]


def periodo_anterior(df: pd.DataFrame, data_ini, data_fim, categorias, vendedores, formas) -> pd.DataFrame:
    """Mesmo recorte de filtros, aplicado ao período imediatamente anterior
    (com a mesma duração), para calcular variações período a período."""
    ini = pd.Timestamp(data_ini)
    fim = pd.Timestamp(data_fim)
    duracao = fim - ini
    prev_fim = ini - pd.Timedelta(days=1)
    prev_ini = prev_fim - duracao
    return apply_filters(df, prev_ini, prev_fim, categorias, vendedores, formas)


def variacao_pct(atual: float, anterior: float) -> float | None:
    """% de variação de `anterior` para `atual`. None se não houver base de comparação."""
    if anterior is None or pd.isna(anterior) or anterior == 0:
        return None
    return 100 * (atual - anterior) / anterior


def plotly_layout_defaults(fig, height=380, legend=True):
    """Aplica o estilo visual padrão (tema escuro Casa&Obra) a uma figura Plotly."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=36, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_BODY, color=COLORS["text"], size=13),
        title=dict(text=""),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=11, color=COLORS["muted"]),
            title_text="",
        ) if legend else dict(title_text=""),
        showlegend=legend,
        hoverlabel=dict(
            bgcolor=COLORS["surface_alt"], font_color=COLORS["text"],
            font_family=FONT_BODY, bordercolor=COLORS["orange"],
        ),
    )
    fig.update_xaxes(showgrid=False, linecolor=COLORS["border"], zeroline=False, color=COLORS["muted"])
    fig.update_yaxes(
        showgrid=True, gridcolor="rgba(255,255,255,0.06)", gridwidth=1, zeroline=False,
        color=COLORS["muted"],
    )
    for trace in fig.data:
        if hasattr(trace, "showlegend") and getattr(trace, "name", None) is None:
            trace.name = ""
    return fig
