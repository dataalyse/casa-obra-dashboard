"""PÁGINA 0 — Início: apresentação do painel e escolha da análise."""

from __future__ import annotations

import streamlit as st

from core import nav
from core.data import HOJE
from core.theme import BG, MUTED, ORANGE, SURFACE, TEXT, YELLOW, icon, rgba
from core.ui import _logo_b64, topbar

CSS = f"""
<style>
.hero {{ text-align:center; padding:34px 10px 8px; }}
.hero img {{ width:150px; filter: drop-shadow(0 10px 36px {rgba(ORANGE, .30)}); }}
.hero h1 {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:38px; letter-spacing:.5px;
  margin:18px 0 6px 0; line-height:1.15; color:{TEXT}; }}
.hero h1 .c {{ color:{ORANGE}; }} .hero h1 .o {{ color:{YELLOW}; }}
.hero p {{ color:{MUTED}; font-size:16px; margin:0; }}
.homec {{ display:flex; flex-direction:column; gap:8px; min-height:178px; }}
.homec .ic {{ width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center;
  background:{rgba(ORANGE, .12)}; margin-bottom:4px; }}
.homec .n {{ font-family:'Space Grotesk',sans-serif; font-size:19px; font-weight:700; color:{TEXT}; }}
.homec .q {{ color:{ORANGE}; font-size:13px; font-weight:600; }}
.homec .d {{ color:{MUTED}; font-size:13.5px; line-height:1.45; }}
div[class*="st-key-home_"] {{
  background:{rgba(SURFACE, .85)}; border:1px solid rgba(255,255,255,.08); border-radius:18px; padding:20px 20px 16px;
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease; animation: coFade .55s both;
}}
div[class*="st-key-home_"]:hover {{ transform: translateY(-4px); border-color:{ORANGE};
  box-shadow: 0 0 0 1px {ORANGE}55, 0 8px 32px {ORANGE}22; }}
div[class*="st-key-home_"] [data-testid="stPageLink"] a {{
  width:100%; max-width:none; justify-content:center; border-radius:10px; padding:8px 12px;
  background:{rgba(ORANGE, .12)}; border:1px solid {ORANGE}66; transition: background .15s ease;
}}
div[class*="st-key-home_"] [data-testid="stPageLink"] a span {{ color:{ORANGE} !important; font-weight:700; }}
div[class*="st-key-home_"] [data-testid="stPageLink"] [data-testid="stIconMaterial"] {{ display:none; }}
div[class*="st-key-home_"]:hover [data-testid="stPageLink"] a {{ background:{ORANGE}; }}
div[class*="st-key-home_"]:hover [data-testid="stPageLink"] a span {{ color:{BG} !important; }}
</style>
"""


def _card(chave: str, titulo: str, pergunta: str, ico: str):
    with st.container(key=f"home_{chave}"):
        st.markdown(
            f"""<div class="homec">
                <div class="ic">{icon(ico, 26)}</div>
                <div class="n">{titulo}</div>
                <div class="q">{pergunta}</div>
                <div class="d">{nav.DESC[chave]}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.page_link(nav.PAGES[chave], label="Ver análise →", width="stretch")


def render():
    st.markdown(CSS, unsafe_allow_html=True)
    topbar(None, navegacao=False)

    st.markdown(
        f"""<div class="hero">
            <img src="data:image/png;base64,{_logo_b64('logo-box.png')}" alt="CASA & OBRA"/>
            <h1><span class="c">CASA</span> <span class="o">&amp; OBRA</span> · Painel de Gestão</h1>
            <p>Escolha a análise que deseja visualizar</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    cols = st.columns(4)
    for c, (chave, titulo, _, _, pergunta, ico) in zip(cols, nav.MENU[:4]):
        with c:
            _card(chave, titulo, pergunta, ico)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    _, *cols, _ = st.columns([0.5, 1, 1, 1, 0.5])
    for c, (chave, titulo, _, _, pergunta, ico) in zip(cols, nav.MENU[4:]):
        with c:
            _card(chave, titulo, pergunta, ico)

    st.markdown(
        f'<div class="co-footer" style="margin-top:36px">Dados atualizados até {HOJE:%d/%m/%Y} · '
        f'Desenvolvido por <b>Datalyse</b> · Dados fictícios para demonstração</div>',
        unsafe_allow_html=True,
    )
