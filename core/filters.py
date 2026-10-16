"""
Filtros globais (escopo, seção 3): estado único em st.session_state que
persiste entre páginas, barra de filtros com chips removíveis, filtro cruzado
por página e aplicação dos filtros sobre as tabelas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd
import streamlit as st

from core.data import DATA_MIN, HOJE, LOJA_ID
from core.theme import data_br

PRESETS = ["Este mês", "Mês anterior", "Últimos 3 meses", "Últimos 12 meses", "2025", "2026 (YTD)", "Tudo",
           "Personalizado"]
LOJAS = ["Todas", "Volta Redonda", "Barra Mansa", "Resende"]
COMPS = ["Período anterior", "Ano anterior"]

DEFAULTS = {
    "f_periodo": "Últimos 12 meses",
    "f_datas": (pd.Timestamp("2025-10-01").date(), HOJE.date()),
    "f_loja": "Todas",
    "f_depto": [],
    "f_cat": [],
    "f_canal": [],
    "f_seg": [],
    "f_vend": [],
    "f_comp": "Período anterior",
}
GLOBAIS = ["periodo", "loja", "depto", "cat", "canal", "seg", "vend"]
NAO_SE_APLICA = "Este filtro não se aplica a esta página"

CROSS_LABEL = {
    "categoria": "Categoria", "subcategoria": "Subcategoria", "canal": "Canal", "loja": "Loja",
    "cidade": "Cidade", "segmento": "Segmento", "departamento": "Departamento", "produto": "Produto",
    "situacao_estoque": "Situação", "forma_pagamento": "Pagamento", "grupo_despesa": "Grupo de despesa",
}


@dataclass
class Ctx:
    page: str
    ini: pd.Timestamp
    fim: pd.Timestamp
    pini: pd.Timestamp
    pfim: pd.Timestamp
    comp: str | None  # None = período de comparação fora da base
    lojas: list[str] | None
    deptos: list[str]
    cats: list[str]
    canais: list[str]
    segs: list[str]
    vends: list[str]
    applies: set
    cross: dict = field(default_factory=dict)

    @property
    def loja_ids(self) -> list[str] | None:
        return [LOJA_ID[l] for l in self.lojas] if self.lojas else None

    @property
    def meses(self) -> int:
        return (self.fim.year - self.ini.year) * 12 + self.fim.month - self.ini.month + 1

    @property
    def mes_ref(self) -> pd.Timestamp:
        """Primeiro dia do último mês do período (referência para fotos mensais)."""
        return self.fim.to_period("M").to_timestamp()

    @property
    def data_ref(self) -> pd.Timestamp:
        return min(self.fim, HOJE)


# ----------------------------------------------------------------------------
# ESTADO
# ----------------------------------------------------------------------------
def init_state():
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)
    st.session_state.setdefault("cross", {})
    st.session_state.setdefault("cross_ver", 0)
    # Reatribuir as chaves dos widgets impede que o Streamlit descarte o
    # valor quando o widget não é desenhado (troca de página).
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and k.startswith(("f_", "p_")):
            st.session_state[k] = st.session_state[k]


def reset_all(page: str | None = None):
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and k.startswith("p_"):
            del st.session_state[k]
    st.session_state["cross"] = {}
    st.session_state["cross_ver"] += 1


def _clear(key: str):
    st.session_state[key] = DEFAULTS[key]


def _remove_item(key: str, item):
    st.session_state[key] = [x for x in st.session_state[key] if x != item]


def cross_get(page: str) -> dict:
    return st.session_state["cross"].setdefault(page, {})


def cross_set(page: str, campo: str, valor):
    cur = cross_get(page)
    if valor is None or cur.get(campo) == valor:
        cur.pop(campo, None)
    else:
        cur[campo] = valor


def cross_remove(page: str, campo: str):
    cross_get(page).pop(campo, None)
    if campo == "categoria":
        cross_get(page).pop("subcategoria", None)
    st.session_state["cross_ver"] += 1


def cross_clear(page: str):
    st.session_state["cross"][page] = {}
    st.session_state["cross_ver"] += 1


def cross_callback(page: str, campo: str, widget_key: str, extrator: Callable[[dict], object]):
    """Callback do st.plotly_chart(on_select=...): clique num ponto liga/desliga o filtro."""

    def _cb():
        estado = st.session_state.get(widget_key)
        pontos = (estado or {}).get("selection", {}).get("points", []) if estado else []
        if not pontos:
            cross_get(page).pop(campo, None)
            return
        valor = extrator(pontos[0])
        if valor is not None:
            cross_get(page)[campo] = valor

    return _cb


def sel_key(page: str, chart: str) -> str:
    return f"sel_{page}_{chart}_{st.session_state['cross_ver']}"


# ----------------------------------------------------------------------------
# PERÍODO
# ----------------------------------------------------------------------------
def period_bounds(preset: str, datas) -> tuple[pd.Timestamp, pd.Timestamp]:
    fim_mes = HOJE.to_period("M")
    if preset == "Este mês":
        return fim_mes.start_time.normalize(), HOJE
    if preset == "Mês anterior":
        p = fim_mes - 1
        return p.start_time.normalize(), p.end_time.normalize()
    if preset == "Últimos 3 meses":
        return (fim_mes - 2).start_time.normalize(), HOJE
    if preset == "Últimos 12 meses":
        return (fim_mes - 11).start_time.normalize(), HOJE
    if preset == "2025":
        return pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")
    if preset == "2026 (YTD)":
        return pd.Timestamp("2026-01-01"), HOJE
    if preset == "Tudo":
        return DATA_MIN, HOJE
    if isinstance(datas, (tuple, list)) and len(datas) == 2:
        return pd.Timestamp(datas[0]), pd.Timestamp(datas[1])
    if isinstance(datas, (tuple, list)) and len(datas) == 1:
        return pd.Timestamp(datas[0]), pd.Timestamp(datas[0])
    return (fim_mes - 11).start_time.normalize(), HOJE


def prev_bounds(ini: pd.Timestamp, fim: pd.Timestamp, modo: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    if modo == "Ano anterior":
        return ini - pd.DateOffset(years=1), fim - pd.DateOffset(years=1)
    # períodos em meses fechados → mesmos N meses imediatamente antes
    if ini.day == 1 and (fim + pd.Timedelta(days=1)).day == 1 or (ini.day == 1 and fim == HOJE):
        n = (fim.year - ini.year) * 12 + fim.month - ini.month + 1
        pini = ini - pd.DateOffset(months=n)
        pfim = (ini - pd.Timedelta(days=1))
        return pini, pfim
    dur = fim - ini
    pfim = ini - pd.Timedelta(days=1)
    return pfim - dur, pfim


# ----------------------------------------------------------------------------
# BARRA DE FILTROS
# ----------------------------------------------------------------------------
def filter_bar(D: dict, page: str, applies: set, extra: Callable[[], None] | None = None) -> Ctx:
    prod = D["produtos"]
    vend = D["vendedores"]

    # dependências: categorias do departamento e vendedores da loja
    deptos = sorted(prod["departamento"].dropna().unique())
    sel_dep = st.session_state["f_depto"]
    cats = sorted(prod.loc[prod["departamento"].isin(sel_dep) if sel_dep else slice(None), "categoria"].unique())
    st.session_state["f_cat"] = [c for c in st.session_state["f_cat"] if c in cats]
    if st.session_state.get("f_loja") not in LOJAS:
        st.session_state["f_loja"] = "Todas"
    loja = st.session_state.get("f_loja") or "Todas"
    vs = vend if loja == "Todas" else vend[vend["id_loja"] == LOJA_ID[loja]]
    vend_opts = sorted(vs["vendedor"].unique()) + ["E-commerce"]
    st.session_state["f_vend"] = [v for v in st.session_state["f_vend"] if v in vend_opts]

    def dis(nome):
        return nome not in applies

    def hlp(nome, txt=None):
        return NAO_SE_APLICA if dis(nome) else txt

    present = st.session_state.get("f_present", False)
    if not present:
        with st.container(key="filtros"):
            c = st.columns([1.25, 2.1, 1.5, 1.5], vertical_alignment="bottom")
            with c[0]:
                st.selectbox("Período", PRESETS, key="f_periodo", disabled=dis("periodo"), help=hlp("periodo"))
            with c[1]:
                st.segmented_control("Loja", LOJAS, key="f_loja", disabled=dis("loja"), help=hlp("loja"))
            with c[2]:
                st.segmented_control("Comparar com", COMPS, key="f_comp", disabled=dis("periodo"),
                                     help=hlp("periodo", "Base da variação ▲▼ mostrada nos indicadores"))
            with c[3]:
                if st.session_state["f_periodo"] == "Personalizado":
                    st.date_input("Intervalo", key="f_datas", min_value=DATA_MIN.date(), max_value=HOJE.date(),
                                  format="DD/MM/YYYY", disabled=dis("periodo"))
                else:
                    ini, fim = period_bounds(st.session_state["f_periodo"], None)
                    st.markdown(
                        f'<div style="font-size:12px;color:var(--text-muted);padding-bottom:10px">'
                        f'{data_br(ini)} a {data_br(fim)}</div>', unsafe_allow_html=True)
            c = st.columns(5)
            with c[0]:
                st.multiselect("Departamento", deptos, key="f_depto", placeholder="Todos",
                               disabled=dis("depto"), help=hlp("depto"))
            with c[1]:
                st.multiselect("Categoria", cats, key="f_cat", placeholder="Todas",
                               disabled=dis("cat"), help=hlp("cat"))
            with c[2]:
                st.multiselect("Canal de venda", sorted(D["canais"]["canal"]), key="f_canal", placeholder="Todos",
                               disabled=dis("canal"), help=hlp("canal"))
            with c[3]:
                st.multiselect("Segmento de cliente", sorted(D["clientes"]["segmento"].dropna().unique()),
                               key="f_seg", placeholder="Todos", disabled=dis("seg"), help=hlp("seg"))
            with c[4]:
                st.multiselect("Vendedor", vend_opts, key="f_vend", placeholder="Todos",
                               disabled=dis("vend"), help=hlp("vend"))
            if extra is not None:
                extra()
            _chips(page)

    ini, fim = period_bounds(st.session_state["f_periodo"], st.session_state.get("f_datas"))
    modo = st.session_state.get("f_comp") or "Período anterior"
    pini, pfim = prev_bounds(ini, fim, modo)
    loja = st.session_state.get("f_loja") or "Todas"

    def g(nome, key):
        return list(st.session_state[key]) if nome in applies else []

    return Ctx(
        page=page, ini=ini, fim=fim, pini=pini, pfim=pfim,
        comp=None if pini < DATA_MIN else ("ano anterior" if modo == "Ano anterior" else "período anterior"),
        lojas=[loja] if (loja != "Todas" and "loja" in applies) else None,
        deptos=g("depto", "f_depto"), cats=g("cat", "f_cat"), canais=g("canal", "f_canal"),
        segs=g("seg", "f_seg"), vends=g("vend", "f_vend"), applies=applies,
        cross=dict(cross_get(page)),
    )


def _chips(page: str):
    chips = []
    if st.session_state["f_periodo"] != DEFAULTS["f_periodo"]:
        chips.append(("periodo", f"Período: {st.session_state['f_periodo']}", _clear, ("f_periodo",)))
    if (st.session_state.get("f_loja") or "Todas") != "Todas":
        chips.append(("loja", f"Loja: {st.session_state['f_loja']}", _clear, ("f_loja",)))
    for key, rot in [("f_depto", "Depto"), ("f_cat", "Categoria"), ("f_canal", "Canal"), ("f_seg", "Segmento"),
                     ("f_vend", "Vendedor")]:
        for item in st.session_state[key]:
            chips.append((f"{key}_{item}", f"{rot}: {item}", _remove_item, (key, item)))
    cross = cross_get(page)
    if not chips and not cross:
        return
    with st.container(horizontal=True, gap="small"):
        for i, (k, label, fn, args) in enumerate(chips):
            st.button(f"{label}  ✕", key=f"chip_{i}_{k}", on_click=fn, args=args)
        for campo, valor in cross.items():
            st.button(f"⚡ {CROSS_LABEL.get(campo, campo)}: {valor}  ✕", key=f"chip_cross_{campo}",
                      on_click=cross_remove, args=(page, campo), help="Filtro cruzado (clique no gráfico)")
        st.button("Limpar filtros", key="chip_limpar_all", on_click=reset_all, type="tertiary")


# ----------------------------------------------------------------------------
# APLICAÇÃO
# ----------------------------------------------------------------------------
def itens(D: dict, ctx: Ctx, ini=None, fim=None, cross: bool = True, ignore: tuple = (),
          lojas: bool = True) -> pd.DataFrame:
    it = D["itens"]
    ini = ctx.ini if ini is None else ini
    fim = ctx.fim if fim is None else fim
    m = (it["data"] >= ini) & (it["data"] <= fim)
    if lojas and ctx.lojas and "loja" not in ignore:
        m &= it["loja"].isin(ctx.lojas)
    if ctx.deptos and "departamento" not in ignore:
        m &= it["departamento"].isin(ctx.deptos)
    if ctx.cats and "categoria" not in ignore:
        m &= it["categoria"].isin(ctx.cats)
    if ctx.canais and "canal" not in ignore:
        m &= it["canal"].isin(ctx.canais)
    if ctx.segs and "segmento" not in ignore:
        m &= it["segmento"].isin(ctx.segs)
    if ctx.vends and "vendedor" not in ignore:
        m &= it["vendedor"].isin(ctx.vends)
    if cross:
        for campo, valor in ctx.cross.items():
            if campo in ignore or campo not in it.columns:
                continue
            m &= it[campo] == valor
    return it.loc[m]


def vendas(D: dict, ctx: Ctx, ini=None, fim=None, incluir_canceladas: bool = False) -> pd.DataFrame:
    """Cabeçalhos de venda com filtros de cabeçalho (sem categoria)."""
    v = D["vendas"]
    ini = ctx.ini if ini is None else ini
    fim = ctx.fim if fim is None else fim
    m = (v["data"] >= ini) & (v["data"] <= fim)
    if not incluir_canceladas:
        m &= ~v["cancelada"]
    if ctx.lojas:
        m &= v["loja"].isin(ctx.lojas)
    if ctx.canais:
        m &= v["canal"].isin(ctx.canais)
    if ctx.segs:
        m &= v["segmento"].isin(ctx.segs)
    if ctx.vends:
        m &= v["vendedor"].isin(ctx.vends)
    for campo, valor in ctx.cross.items():
        if campo in v.columns:
            m &= v[campo] == valor
    return v.loc[m]


def by_loja(df: pd.DataFrame, ctx: Ctx, col: str = "id_loja") -> pd.DataFrame:
    if ctx.loja_ids:
        return df[df[col].isin(ctx.loja_ids)]
    return df
