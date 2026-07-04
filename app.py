"""
Casa&Obra — Painel de Vendas
Arquivo principal do app Streamlit.

Para executar:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st

from utils import (
    load_data, apply_filters, get_filter_state, periodo_anterior,
    saudacao_br, data_extenso_br,
)
from styles import get_css
from views import view_inicio, view_analise, view_vendedor, view_produtos

st.set_page_config(
    page_title="Casa&Obra | Painel de Vendas",
    page_icon="assets/logo_mini.png",
    layout="wide",
)

st.markdown(get_css(), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DADOS E ESTADO DE NAVEGAÇÃO/FILTROS
# ----------------------------------------------------------------------------
df = load_data()

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "Início"
pagina = st.session_state["pagina"]

data_ini, data_fim, categorias, vendedores, formas = get_filter_state(df)
df_filtrado = apply_filters(df, data_ini, data_fim, categorias, vendedores, formas)
df_anterior = periodo_anterior(df, data_ini, data_fim, categorias, vendedores, formas)

# ----------------------------------------------------------------------------
# CABEÇALHO SUPERIOR COM LOGO
# ----------------------------------------------------------------------------
top_l, top_r = st.columns([4, 1])
with top_r:
    st.image("assets/logo_horizontal.png", width="stretch")

# ----------------------------------------------------------------------------
# ROTEAMENTO DE PÁGINAS (navegação por botões, sem barra lateral)
# ----------------------------------------------------------------------------
if pagina == "Início":
    view_inicio(df_filtrado, df_anterior, saudacao_br(), data_extenso_br())
elif pagina == "Análise de Vendas":
    view_analise(df_filtrado, df_anterior, df)
elif pagina == "Vendas por Vendedor":
    view_vendedor(df_filtrado, df)
else:
    view_produtos(df_filtrado, df)

st.markdown('<div class="watermark">@datalyse</div>', unsafe_allow_html=True)

# O rerun de navegação é disparado aqui, só depois que a página inteira
# (inclusive seus widgets de filtro) já foi renderizada nesta execução —
# veja o comentário em views.nav_bar() para o motivo.
if st.session_state.pop("_trocar_pagina", False):
    st.rerun()
