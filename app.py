"""
Casa&Obra — Painel de Gestão (Streamlit)
Dashboard demonstrativo Datalyse para uma rede de 3 lojas de materiais de
construção. Especificação: ESCOPO_DASHBOARD_CASA_E_OBRA.md.

Para executar:
    pip install -r requirements.txt
    streamlit run app.py
"""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from core import nav
from core.data import load
from core.filters import init_state
from core.theme import CSS
from views import clientes, estoque, financeiro, inicio, inteligencia, rentabilidade, vendas, visao_geral

ASSETS = Path(__file__).resolve().parent / "assets"

st.set_page_config(
    page_title="CASA & OBRA | Painel de Gestão",
    page_icon=str(ASSETS / "logo-icone.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(CSS, unsafe_allow_html=True)

load()
init_state()

RENDER = {
    "visao": visao_geral.render, "vendas": vendas.render, "estoque": estoque.render,
    "rentab": rentabilidade.render, "finan": financeiro.render, "clientes": clientes.render,
    "intel": inteligencia.render,
}

home = st.Page(inicio.render, title="Início", icon=":material/home:", url_path="inicio", default=True)
nav.PAGES["inicio"] = home
paginas = [home]
for chave, titulo, rota, icone, _, _ in nav.MENU:
    p = st.Page(RENDER[chave], title=titulo, icon=icone, url_path=rota)
    nav.PAGES[chave] = p
    paginas.append(p)

# sem menu lateral: a navegação é a barra de botões no topo de cada página (core.ui.topbar)
atual = st.navigation(paginas, position="hidden")

atual.run()

# Atalhos de teclado (1–7, F, Esc) injetados na página principal
components.html(
    """
<script>
const doc = window.parent.document;
if (!doc.__coKeys) {
  doc.__coKeys = true;
  doc.addEventListener('keydown', (e) => {
    const t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (/^[1-7]$/.test(e.key)) {
      const links = doc.querySelectorAll('.st-key-topnav a');
      const a = links[parseInt(e.key, 10)];
      if (a) { a.click(); e.preventDefault(); }
    } else if (e.key === 'f' || e.key === 'F') {
      const i = doc.querySelector('.st-key-filtros input');
      if (i) { i.focus(); e.preventDefault(); }
    } else if (e.key === 'Escape') {
      const b = doc.querySelector('.st-key-esc_cross button');
      if (b) b.click();
    }
  });
}
</script>
""",
    height=0,
)
