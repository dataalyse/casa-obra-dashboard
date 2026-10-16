"""PÁGINA 4 — Rentabilidade e Custos: quais produtos e categorias geram lucro de verdade?"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.filters import cross_callback, itens, sel_key
from core.metrics import abc, despesas, div, mensal, meses_periodo, resumo, spark12, var
from core.theme import (
    CRIT, INFO, MUTED, ORANGE, POS, SEQ, SURFACE, TEXT, YELLOW,
    mes_ano_curto, moeda, moeda_curta, num, pct, rgba, style,
)
from core.ui import TONS, bar_cell, chart, footer, hbar, html_card, kpi, kpi_row, pill, table
from views._common import TODOS, shell

PAGE = "rentab"
DEP_COR = {}


def _extra():
    c = st.columns([2, 3])
    with c[0]:
        st.session_state.setdefault("p_margem", (0, 60))
        st.slider("Faixa de margem do produto (%)", 0, 60, key="p_margem", step=1,
                  help="Filtra os produtos exibidos na matriz e no ranking pela margem bruta")


def _dep_cores(D):
    deps = sorted(D["categorias"]["departamento"].unique())
    return {d: SEQ[i] for i, d in enumerate(deps)}


def render():
    D, ctx = shell(PAGE, "Rentabilidade & Custos", "Quais produtos e categorias geram lucro de verdade?", TODOS, _extra)
    cores_dep = _dep_cores(D)

    it = itens(D, ctx)
    itp = itens(D, ctx, ini=ctx.pini, fim=ctx.pfim)
    r, rp = resumo(it), resumo(itp)
    dsp = despesas(D, ctx)["valor"].sum()
    dspp = despesas(D, ctx, ctx.pini, ctx.pfim)["valor"].sum()
    mop = div(r["lucro"] - dsp, r["fat"])
    mopp = div(rp["lucro"] - dspp, rp["fat"])
    m_sem = div(r["bruto"] - r["cmv"], r["bruto"])
    impacto = (m_sem - r["margem"]) if m_sem is not None and r["margem"] is not None else None
    m_semp = div(rp["bruto"] - rp["cmv"], rp["bruto"])
    impactop = (m_semp - rp["margem"]) if m_semp is not None and rp["margem"] is not None else None

    def dpp(a, b):
        return (a - b) if a is not None and b is not None else None

    c = kpi_row()
    with c[0]:
        kpi("lucro", "Lucro bruto", moeda_curta(r["lucro"]), "trending", delta=var(r["lucro"], rp["lucro"]),
            comp=ctx.comp, spark=spark12(D, ctx, "lucro"), tom="hl", info="Faturamento − CMV.")
    with c[1]:
        kpi("margem", "Margem bruta", pct(r["margem"]), "percent", delta=dpp(r["margem"], rp["margem"]), pp=True,
            comp=ctx.comp, spark=spark12(D, ctx, "margem"), info="Lucro bruto ÷ faturamento.")
    with c[2]:
        kpi("cmv", "CMV", moeda_curta(r["cmv"]), "package", delta=var(r["cmv"], rp["cmv"]), comp=ctx.comp,
            inverso=True, spark=spark12(D, ctx, "cmv"),
            info="Custo das mercadorias vendidas: quanto custaram os produtos que saíram.")
    with c[3]:
        kpi("desc", "Descontos", moeda_curta(r["desc"]), "tag", delta=var(r["desc"], rp["desc"]), comp=ctx.comp,
            inverso=True, info="Soma dos descontos concedidos nos itens vendidos.")
    with c[4]:
        kpi("impacto", "Impacto do desconto", f"{num((impacto or 0) * 100, 1)} p.p.", "trending-down",
            delta=dpp(impacto, impactop), pp=True, inverso=True, comp=ctx.comp, tom="warn",
            info="Quantos pontos de margem o desconto tira: margem sem desconto − margem real.")
    with c[5]:
        kpi("mop", "Margem operacional", pct(mop), "activity", delta=dpp(mop, mopp), pp=True, comp=ctx.comp,
            info="(Lucro bruto − despesas operacionais das lojas) ÷ faturamento.")

    if it.empty:
        chart("rt_vazio", "Sem dados", "", None)
        footer()
        return

    lo, hi = st.session_state.get("p_margem", (0, 60))
    prod = abc(it)
    prod["margem"] = prod["lucro"] / prod["fat"]
    prod_f = prod[(prod["margem"] * 100 >= lo) & (prod["margem"] * 100 <= hi)]

    # ------------------------------------------------------------ 4.1 / 4.2
    a, b = st.columns([2, 1])
    with a:
        p = prod_f
        if p.empty:
            chart("rt_matriz", "Matriz faturamento × margem", "", None)
        else:
            mx, my = prod["fat"].median(), prod["margem"].median() * 100
            fig = go.Figure()
            xmin, xmax = min(p["fat"].min(), mx) * 0.7, max(p["fat"].max(), mx) * 1.5
            ymin = min(0, p["margem"].min() * 100 - 2)
            ymax = max(p["margem"].max() * 100, my) + 3
            # quadrante "vendem muito, lucram pouco" sombreado + medianas (como traços: eixo X em log)
            fig.add_scatter(x=[mx, xmax, xmax, mx, mx], y=[ymin, ymin, my, my, ymin], fill="toself", mode="none",
                            fillcolor=rgba(CRIT, .10), hoverinfo="skip", showlegend=False)
            fig.add_scatter(x=[mx, mx], y=[ymin, ymax], mode="lines", line=dict(color=MUTED, dash="dot", width=1),
                            hoverinfo="skip", showlegend=False)
            fig.add_scatter(x=[xmin, xmax], y=[my, my], mode="lines", line=dict(color=MUTED, dash="dot", width=1),
                            hoverinfo="skip", showlegend=False)
            sz = np.sqrt(p["lucro"].clip(lower=0))
            sz = 8 + 34 * sz / (sz.max() or 1)
            for d in sorted(p["departamento"].dropna().unique()):
                pdp = p[p["departamento"] == d]
                fig.add_scatter(
                    x=pdp["fat"], y=pdp["margem"] * 100, mode="markers", name=d,
                    marker=dict(size=sz[pdp.index], color=rgba(cores_dep[d], .75), line=dict(color=cores_dep[d], width=1)),
                    customdata=np.c_[pdp["produto"], pdp["categoria"], [moeda(v) for v in pdp["lucro"]]],
                    hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Faturamento: R$ %{x:,.2f}"
                                  "<br>Margem: %{y:.1f}%<br>Lucro: %{customdata[2]}<extra></extra>",
                )
            for txt, xa, ya, cor in [("⭐ Estrelas", 0.98, 0.98, POS), ("⚠ Vendem muito, lucram pouco", 0.98, 0.02, CRIT),
                                     ("💎 Nicho rentável", 0.02, 0.98, INFO), ("🔍 Revisar", 0.02, 0.02, MUTED)]:
                fig.add_annotation(xref="paper", yref="paper", x=xa, y=ya, text=f"<b>{txt}</b>", showarrow=False,
                                   xanchor="right" if xa > 0.5 else "left", yanchor="top" if ya > 0.5 else "bottom",
                                   font=dict(color=cor, size=12), bgcolor=rgba(SURFACE, .7))
            style(fig, 440)
            fig.update_xaxes(type="log", title_text="Faturamento (escala log)", tickprefix="R$ ", showgrid=True,
                             gridcolor="rgba(255,255,255,0.06)")
            fig.update_yaxes(title_text="Margem bruta %", ticksuffix="%", range=[ymin, ymax])
            fig.update_xaxes(range=[np.log10(xmin), np.log10(xmax)])
            n_ruim = int(((prod["fat"] > mx) & (prod["margem"] * 100 < my)).sum())
            chart("rt_matriz", "Matriz faturamento × margem",
                  f"Cada bolha é um produto (tamanho = lucro) · linhas = medianas · {n_ruim} produtos vendem muito e lucram pouco",
                  fig, p[["produto", "categoria", "departamento", "fat", "margem", "lucro"]].rename(columns={
                      "produto": "Produto", "categoria": "Categoria", "departamento": "Departamento", "fat": "Faturamento",
                      "margem": "Margem", "lucro": "Lucro"}).round(3))

    with b:
        src = itens(D, ctx, ignore=("categoria",))
        g = src.groupby("categoria", observed=True).agg(fat=("valor_liquido", "sum"), lucro=("lucro_bruto", "sum"))
        g = g[g["fat"] > 0]
        g["m"] = g["lucro"] / g["fat"]
        g = g.sort_values("m", ascending=False)
        media = g["lucro"].sum() / g["fat"].sum()
        sel = ctx.cross.get("categoria")
        cores = [(CRIT if m < .2 else (YELLOW if m <= .3 else POS)) for m in g["m"]]
        cores = [c_ if (sel is None or k == sel) else rgba(c_, .3) for c_, k in zip(cores, g.index)]
        fig = hbar(g.index, g["m"] * 100, [pct(m) for m in g["m"]], cores, height=440,
                   hover="<b>%{y}</b><br>Margem: %{x:.1f}%<extra></extra>")
        fig.add_vline(x=media * 100, line=dict(color=TEXT, dash="dash", width=1.5),
                      annotation_text=f"média {pct(media)}", annotation_font=dict(color=TEXT, size=10),
                      annotation_position="bottom right")
        k = sel_key(PAGE, "categoria")
        chart("rt_cat", "Margem por categoria", "Vermelho < 20% · amarelo 20–30% · verde > 30% · clique para filtrar",
              fig, g.reset_index().rename(columns={"categoria": "Categoria", "fat": "Faturamento", "lucro": "Lucro",
                                                   "m": "Margem"}).round(3),
              on_select=cross_callback(PAGE, "categoria", k, lambda p_: p_.get("y")), sel_key=k)

    # ------------------------------------------------------------ 4.3 / 4.4 / 4.5
    c1, c2, c3 = st.columns(3)
    with c1:
        g = it.groupby("departamento", observed=True)["lucro_bruto"].sum().sort_values(ascending=False)
        g = g[g > 0]
        tot = g.sum()
        fig = go.Figure(go.Pie(labels=list(g.index), values=g.values, hole=0.66, sort=False,
                               marker=dict(colors=[cores_dep[d] for d in g.index], line=dict(color=SURFACE, width=3)),
                               textinfo="percent", textfont=dict(color="#0A1626", size=11),
                               hovertemplate="<b>%{label}</b><br>Lucro: R$ %{value:,.2f}<br>%{percent}<extra></extra>"))
        fig.add_annotation(text=f"<b>{moeda_curta(tot)}</b><br><span style='font-size:11px;color:{MUTED}'>LUCRO</span>",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=17, color=TEXT, family="Space Grotesk"))
        style(fig, 340)
        fig.update_layout(legend=dict(orientation="h", y=-0.05, yanchor="top", x=0.5, xanchor="center"))
        chart("rt_dep", "Lucro por departamento", "De onde vem o lucro bruto", fig,
              pd.DataFrame({"Departamento": g.index, "Lucro": g.values.round(2)}))

    with c2:
        faixas = ["0%", "até 3%", "3–5%", "5–7%", "7–10%", "> 10%"]
        d = it["desconto_pct"]
        f = pd.cut(d, [-1, 0.00001, 0.03, 0.05, 0.07, 0.10, 10], labels=faixas, include_lowest=True)
        g = it.groupby(f, observed=False).agg(fat=("valor_liquido", "sum"), lucro=("lucro_bruto", "sum")).reindex(faixas)
        g["m"] = g["lucro"] / g["fat"].replace(0, np.nan)
        fig = go.Figure()
        fig.add_bar(x=faixas, y=g["fat"], name="Faturamento", marker=dict(color=ORANGE, cornerradius=6),
                    hovertemplate="<b>Desconto %{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>")
        fig.add_scatter(x=faixas, y=g["m"] * 100, name="Margem média", yaxis="y2", mode="lines+markers+text",
                        line=dict(color=YELLOW, width=2.5), marker=dict(size=7),
                        text=[pct(m) for m in g["m"]], textposition="top center", textfont=dict(color=YELLOW, size=10),
                        hovertemplate="Margem: %{y:.1f}%<extra></extra>")
        style(fig, 340)
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, ticksuffix="%",
                                      tickfont=dict(color=MUTED, size=11), rangemode="tozero"))
        fig.update_yaxes(tickprefix="R$ ", selector=dict(anchor="x"))
        chart("rt_desc", "Desconto × margem", "Quanto mais desconto, menor a margem? Faturamento e margem por faixa",
              fig, g.reset_index(names="Faixa").rename(columns={"fat": "Faturamento", "lucro": "Lucro", "m": "Margem"}).round(3))

    with c3:
        ms = meses_periodo(ctx)
        fig = go.Figure()
        tab = {"Mês": [mes_ano_curto(m_) for m_ in ms]}
        for dname in sorted(it["departamento"].dropna().unique()):
            mm = mensal(it[it["departamento"] == dname], ms)["margem"] * 100
            tab[dname] = mm.round(1).values
            fig.add_scatter(x=tab["Mês"], y=mm.values, name=dname, mode="lines",
                            line=dict(color=cores_dep[dname], width=2.2, shape="spline"),
                            hovertemplate=f"{dname}: %{{y:.1f}}%<extra></extra>")
        style(fig, 340)
        fig.update_layout(hovermode="x unified")
        fig.update_yaxes(ticksuffix="%")
        chart("rt_evol", "Evolução da margem por departamento", "Margem bruta % mês a mês", fig, pd.DataFrame(tab))

    # ------------------------------------------------------------ 4.6
    top = prod_f.sort_values("lucro", ascending=False).head(20)
    tot_l = prod["lucro"].sum()
    linhas = []
    for i, r_ in enumerate(top.itertuples(), 1):
        m = r_.margem
        cor = CRIT if m < .2 else (YELLOW if m <= .3 else POS)
        linhas.append({
            "#": f"{i}º", "Produto": f"<b>{r_.produto}</b>", "Categoria": r_.categoria,
            "Faturamento": moeda(r_.fat, 0), "CMV": moeda(r_.cmv, 0), "Lucro": f"<b>{moeda(r_.lucro, 0)}</b>",
            "Margem": bar_cell(pct(m), m / 0.6, cor), "% do lucro": pct(r_.lucro / tot_l),
            "ABC": pill(r_.classe, {"A": "pos", "B": "warn", "C": "info"}[r_.classe]),
        })
    html_card("rt_rank", "Ranking de contribuição para o lucro", "Top 20 produtos por lucro bruto no período",
              table(pd.DataFrame(linhas), {"#": "center", "Faturamento": "right", "CMV": "right", "Lucro": "right",
                                           "% do lucro": "right", "ABC": "center"}, max_height=520)
              if linhas else '<div class="empty">Sem dados</div>',
              top[["produto", "categoria", "fat", "cmv", "lucro", "margem", "classe"]].rename(columns={
                  "produto": "Produto", "categoria": "Categoria", "fat": "Faturamento", "cmv": "CMV",
                  "lucro": "Lucro", "margem": "Margem", "classe": "Classe ABC"}).round(3))

    footer()
