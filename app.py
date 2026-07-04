"""
Casa&Obra — Painel de Vendas
Arquivo principal do app Streamlit.

Para executar:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st

from utils import load_data, apply_filters, MESES_PT
from styles import get_css
from views import view_analise, view_vendedor, view_produtos

st.set_page_config(
    page_title="Casa&Obra | Painel de Vendas",
    page_icon="assets/logo_mini.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_css(), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DADOS
# ----------------------------------------------------------------------------
df = load_data()

# ----------------------------------------------------------------------------
# SIDEBAR — identidade, navegação e filtros
# ----------------------------------------------------------------------------
with st.sidebar:
    st.image("assets/logo_badge.png", use_container_width=True)
    st.markdown(
        "<p style='text-align:center; letter-spacing:1px; font-size:11px; "
        "color:#B7BFCC; margin-top:-6px;'>PAINEL DE VENDAS</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    pagina = st.radio(
        "Navegação",
        options=["📊  Análise de Vendas", "🧑‍🔧  Vendas por Vendedor", "🧱  Vendas por Produtos"],
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:12px; font-weight:600; color:#B7BFCC; "
        "text-transform:uppercase; letter-spacing:0.6px;'>Filtros</p>",
        unsafe_allow_html=True,
    )

    data_min, data_max = df["Data_Venda"].min().date(), df["Data_Venda"].max().date()
    periodo = st.date_input(
        "Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
    )
    if isinstance(periodo, tuple) and len(periodo) == 2:
        data_ini, data_fim = periodo
    else:
        data_ini, data_fim = data_min, data_max

    categorias = st.multiselect("Categoria", sorted(df["Categoria"].unique()))
    vendedores = st.multiselect("Vendedor", sorted(df["Vendedor"].unique()))
    formas = st.multiselect("Forma de Pagamento", sorted(df["Forma_Pagamento"].unique()))

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:11px; color:#8590A3;'>Casa&Obra • Material de Construção<br>"
        "Dashboard gerado em Python + Streamlit</p>",
        unsafe_allow_html=True,
    )

df_filtrado = apply_filters(df, data_ini, data_fim, categorias, vendedores, formas)

# ----------------------------------------------------------------------------
# CABEÇALHO SUPERIOR COM LOGO
# ----------------------------------------------------------------------------
top_l, top_r = st.columns([4, 1])
with top_r:
    st.image("assets/logo_horizontal.png", use_container_width=True)

# ----------------------------------------------------------------------------
# ROTEAMENTO DE PÁGINAS
# ----------------------------------------------------------------------------
if "Análise de Vendas" in pagina:
    view_analise(df_filtrado)
elif "Vendedor" in pagina:
    view_vendedor(df_filtrado)
else:
    view_produtos(df_filtrado)
