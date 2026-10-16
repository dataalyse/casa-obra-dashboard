"""PÁGINA 0 — Boas-vindas (sem filtros e sem menu lateral)."""

from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import streamlit as st

from core import nav
from core.data import HOJE, ROOT, load
from core.metrics import nps, resumo
from core.theme import BLUE, MUTED, ORANGE, YELLOW, icon, moeda_curta, num, pct, rgba, mes_ano


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


CSS = f"""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] {{ display:none !important; }}
.blob {{ position:fixed; width:520px; height:520px; border-radius:50%; filter: blur(110px); opacity:.35; z-index:0; pointer-events:none; }}
.blob.a {{ background:{ORANGE}; top:-160px; left:-120px; animation: drift 18s ease-in-out infinite alternate; }}
.blob.b {{ background:{BLUE}; bottom:-200px; right:-140px; opacity:.6; animation: drift 22s ease-in-out infinite alternate-reverse; }}
@keyframes drift {{ from {{ transform: translate(0,0) scale(1); }} to {{ transform: translate(120px,80px) scale(1.15); }} }}
.hero {{ text-align:center; position:relative; z-index:1; margin-top:10px; }}
.hero img {{ width:180px; filter: drop-shadow(0 10px 40px {rgba(ORANGE, .35)}); }}
.hero h1 {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:44px; margin:18px 0 6px 0; line-height:1.15; }}
.hero h1 .c {{ color:{ORANGE}; }} .hero h1 .o {{ color:{YELLOW}; }}
.hero p {{ color:{MUTED}; font-size:16px; margin:0; }}
.mini {{ text-align:center; }}
.mini .l {{ font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:{MUTED}; font-weight:600; }}
.mini .v {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:30px; margin-top:4px; animation: coCount .8s both; }}
.mini .s {{ font-size:11.5px; color:{MUTED}; }}
.section-t {{ text-align:center; font-family:'Space Grotesk',sans-serif; font-size:20px; font-weight:600; margin:30px 0 14px 0; }}
.navc {{ display:flex; flex-direction:column; gap:10px; min-height:150px; padding:6px 2px; }}
.navc .ic {{ width:46px; height:46px; border-radius:12px; display:flex; align-items:center; justify-content:center; background:{rgba(ORANGE, .12)}; }}
.navc .n {{ font-family:'Space Grotesk',sans-serif; font-size:18px; font-weight:600; }}
.navc .q {{ color:{MUTED}; font-size:13.5px; flex:1; }}
.navc .go {{ align-self:flex-end; }}
div[class*="st-key-nav_"] {{
  background:{rgba("#10233A", .85)}; backdrop-filter: blur(12px); border:1px solid rgba(255,255,255,.08);
  border-radius:16px; padding:16px 18px; transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
  animation: coFade .55s both;
}}
div[class*="st-key-nav_"]:hover {{ transform: translateY(-4px); border-color:{ORANGE}; box-shadow: 0 0 0 1px {ORANGE}55, 0 8px 32px {ORANGE}22; }}
div[class*="st-key-mini_"] {{ background:{rgba("#10233A", .7)}; border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:14px; }}
</style>
<div class="blob a"></div><div class="blob b"></div>
"""


def render():
    D = load()
    st.markdown(CSS, unsafe_allow_html=True)

    logo = _b64(ROOT / "assets" / "logo-box.png")
    st.markdown(
        f"""<div class="hero">
            <img src="data:image/png;base64,{logo}" alt="CASA & OBRA"/>
            <h1>Bem-vindo(a) ao painel da <span class="c">CASA</span> <span class="o">&amp; OBRA</span></h1>
            <p>Acompanhe vendas, estoque, rentabilidade e finanças das 3 lojas em um só lugar.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # mini-KPIs do último mês (set/2026)
    ini = HOJE.to_period("M").start_time.normalize()
    it = D["itens"]
    r = resumo(it[(it["data"] >= ini) & (it["data"] <= HOJE)])
    n = D["nps"]
    nps_mes = nps(n[(n["data_resposta"] >= ini) & (n["data_resposta"] <= HOJE)])
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    _, *cols, _ = st.columns([1, 2, 2, 2, 2, 1])
    minis = [
        ("Faturamento", moeda_curta(r["fat"])),
        ("Margem bruta", pct(r["margem"])),
        ("Nº de vendas", num(r["n"])),
        ("NPS", num(nps_mes)),
    ]
    for c, (l, v) in zip(cols, minis):
        with c:
            with st.container(key=f"mini_{l}"):
                st.markdown(f'<div class="mini"><div class="l">{l}</div><div class="v">{v}</div>'
                            f'<div class="s">{mes_ano(ini)}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-t">Por onde começar?</div>', unsafe_allow_html=True)

    linhas = [nav.MENU[:4], nav.MENU[4:]]
    for linha in linhas:
        if len(linha) == 4:
            cols = st.columns(4)
        else:
            _, *cols, _ = st.columns([0.5, 1, 1, 1, 0.5])
        for c, (chave, titulo, _, _, pergunta, ico) in zip(cols, linha):
            with c:
                with st.container(key=f"nav_{chave}"):
                    st.markdown(
                        f"""<div class="navc">
                            <div class="ic">{icon(ico, 26)}</div>
                            <div class="n">{titulo}</div>
                            <div class="q">{pergunta}</div>
                            <div class="go">{icon("arrow-right", 20, ORANGE)}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    st.page_link(nav.PAGES[chave], label=titulo)

    st.markdown(
        f'<div class="co-footer" style="margin-top:36px">Dados atualizados até {HOJE:%d/%m/%Y} · '
        f'Desenvolvido por <b>Datalyse</b></div>',
        unsafe_allow_html=True,
    )
