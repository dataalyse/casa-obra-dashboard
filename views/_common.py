"""Moldura comum das páginas de análise: cabeçalho, filtros, modo apresentação."""

from __future__ import annotations

from typing import Callable

import streamlit as st

from core.data import load
from core.filters import Ctx, cross_clear, filter_bar
from core.ui import header

TODOS = {"periodo", "loja", "depto", "cat", "canal", "seg", "vend"}


def shell(page: str, titulo: str, sub: str, applies: set, extra: Callable[[], None] | None = None) -> tuple[dict, Ctx]:
    D = load()
    c1, c2 = st.columns([8, 1.3], vertical_alignment="center")
    with c1:
        header(titulo, sub)
    with c2:
        st.toggle("Modo apresentação", key="f_present",
                  help="Esconde o menu lateral e a barra de filtros (para prints do portfólio)")
    if st.session_state.get("f_present"):
        st.markdown(
            "<style>[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl'],"
            "[data-testid='stExpandSidebarButton']{display:none!important}</style>",
            unsafe_allow_html=True,
        )
    ctx = filter_bar(D, page, applies, extra)
    with st.container(key="esc_cross"):
        st.button("esc", key="esc_btn", on_click=cross_clear, args=(page,))
    st.markdown("<style>.st-key-esc_cross{display:none}</style>", unsafe_allow_html=True)
    return D, ctx
