"""
Casa&Obra — Painel de Vendas
Funções utilitárias: carga de dados, tokens de estilo e helpers de formatação.
"""

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# TOKENS DE DESIGN — "Planta Baixa" (identidade visual Casa&Obra)
# ----------------------------------------------------------------------------
COLORS = {
    "orange": "#E8752E",   # Casa
    "lime": "#E4F222",     # &Obra
    "navy": "#22314A",     # fundo escuro / textos de destaque
    "slate": "#3C536B",    # azul secundário
    "concrete": "#F2EFE7", # fundo geral (cor de concreto/cimento)
    "card": "#FFFFFF",
    "text": "#20293A",
    "muted": "#6B7480",
    "border": "#D8D2C4",
    "success": "#3F9142",
    "danger": "#C1443A",
}

# Paleta categórica para gráficos (ordem fixa, sempre as mesmas cores por categoria)
CATEGORY_PALETTE = [
    COLORS["orange"], COLORS["navy"], COLORS["lime"],
    COLORS["slate"], "#8A6E4B", "#B24C2F",
]

FONT_DISPLAY = "'Archivo Black', 'Arial Black', sans-serif"
FONT_BODY = "'Work Sans', 'Segoe UI', sans-serif"
FONT_MONO = "'IBM Plex Mono', 'Courier New', monospace"

DATA_PATH = "data/vendas.xlsx"


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


def plotly_layout_defaults(fig, height=380, legend=True):
    """Aplica o estilo visual padrão (tema 'planta baixa') a uma figura Plotly."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_BODY, color=COLORS["text"], size=13),
        title_font=dict(family=FONT_DISPLAY, size=15, color=COLORS["navy"]),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=11),
        ) if legend else dict(),
        showlegend=legend,
        hoverlabel=dict(
            bgcolor=COLORS["navy"], font_color="white", font_family=FONT_BODY
        ),
    )
    fig.update_xaxes(showgrid=False, linecolor=COLORS["border"], zeroline=False)
    fig.update_yaxes(
        showgrid=True, gridcolor="#E7E2D6", gridwidth=1, zeroline=False
    )
    return fig
