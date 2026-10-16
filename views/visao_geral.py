"""PÁGINA 1 — Visão Geral: como está o desempenho geral da loja?"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.filters import itens
from core.metrics import despesas, div, mensal, meses_periodo, metas, metas_mensal, resumo, spark12, var
from core.theme import (
    CRIT, INFO, LOJA_COR, MUTED, ORANGE, POS, SEQ, SURFACE, SURFACE2, TEXT, YELLOW,
    mes_ano_curto, moeda, moeda_curta, num, pct, rgba, style,
)
from core.ui import chart, footer, kpi, kpi_row
from views._common import TODOS, shell

PAGE = "visao"


def render():
    D, ctx = shell(PAGE, "Visão Geral", "Como está o desempenho geral da loja?", TODOS)

    it = itens(D, ctx)
    itp = itens(D, ctx, ini=ctx.pini, fim=ctx.pfim)
    r, rp = resumo(it), resumo(itp)
    meta, metap = metas(D, ctx), metas(D, ctx, ctx.pini, ctx.pfim)
    ating, atingp = div(r["fat"], meta), div(rp["fat"], metap)
    sp = spark12(D, ctx, "fat")
    spl = spark12(D, ctx, "lucro")
    spm = spark12(D, ctx, "margem")
    spn = spark12(D, ctx, "n")
    spt = spark12(D, ctx, "ticket")

    c = kpi_row()
    with c[0]:
        kpi("fat", "Faturamento", moeda_curta(r["fat"]), "dollar", delta=var(r["fat"], rp["fat"]), comp=ctx.comp,
            spark=sp, tom="hl", link="vendas", info="Soma do valor líquido das vendas (sem frete e sem canceladas).")
    with c[1]:
        kpi("lucro", "Lucro bruto", moeda_curta(r["lucro"]), "trending", delta=var(r["lucro"], rp["lucro"]),
            comp=ctx.comp, spark=spl, link="rentab", info="Faturamento menos o custo dos produtos vendidos (CMV).")
    with c[2]:
        kpi("margem", "Margem bruta", pct(r["margem"]), "percent",
            delta=(r["margem"] - rp["margem"]) if r["margem"] is not None and rp["margem"] is not None else None,
            pp=True, comp=ctx.comp, spark=spm, link="rentab", info="Lucro bruto ÷ faturamento.")
    with c[3]:
        kpi("n", "Nº de vendas", num(r["n"]), "cart", delta=var(r["n"], rp["n"]), comp=ctx.comp, spark=spn,
            link="vendas", info="Quantidade de vendas (notas) concluídas no período.")
    with c[4]:
        kpi("ticket", "Ticket médio", moeda(r["ticket"]), "receipt", delta=var(r["ticket"], rp["ticket"]),
            comp=ctx.comp, spark=spt, link="vendas", info="Faturamento ÷ nº de vendas: quanto cada cliente gasta, em média, por compra.")
    with c[5]:
        kpi("meta", "Atingimento de meta", pct(ating), "target",
            delta=(ating - atingp) if ating is not None and atingp is not None else None, pp=True, comp=ctx.comp,
            tom="hl" if (ating or 0) >= 1 else "", link="vendas",
            info="Faturamento ÷ meta de faturamento das lojas (ou dos vendedores filtrados) no período.")

    if it.empty:
        chart("vg_vazio", "Sem dados", "", None)
        footer()
        return

    # ------------------------------------------------------------------ 1.1 / 1.2
    a, b = st.columns([2, 1])
    ms = meses_periodo(ctx)
    m = mensal(it, ms)
    ant = mensal(itens(D, ctx, ini=ms[0] - pd.DateOffset(years=1), fim=ctx.fim - pd.DateOffset(years=1)),
                 ms - pd.DateOffset(years=1))
    m["fat_aa"] = ant["fat"].values
    with a:
        x = [mes_ano_curto(d) for d in m.index]
        varaa = [var(f, p) for f, p in zip(m["fat"], m["fat_aa"])]
        cd = np.array([[moeda(p) if p else "—", pct(v, sinal=True) if v is not None else "—"]
                       for p, v in zip(m["fat_aa"], varaa)], dtype=object)
        fig = go.Figure()
        fig.add_bar(x=x, y=m["fat"], name="Faturamento", marker=dict(color=ORANGE, cornerradius=6),
                    customdata=cd,
                    hovertemplate="<b>%{x}</b><br>Faturamento: <b>R$ %{y:,.2f}</b><br>Ano anterior: %{customdata[0]}"
                                  "<br>Variação: %{customdata[1]}<extra></extra>")
        fig.add_scatter(x=x, y=m["fat_aa"].replace(0, np.nan), name="Mesmo mês do ano anterior", mode="lines",
                        line=dict(color=INFO, dash="dash", width=2, shape="spline"),
                        hovertemplate="Ano anterior: R$ %{y:,.2f}<extra></extra>")
        fig.add_scatter(x=x, y=m["margem"] * 100, name="Margem %", yaxis="y2", mode="lines+markers",
                        line=dict(color=YELLOW, width=2.5, shape="spline"), marker=dict(size=6),
                        hovertemplate="Margem: %{y:.1f}%<extra></extra>")
        style(fig, 360)
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, ticksuffix="%",
                                      tickfont=dict(color=MUTED, size=11), rangemode="tozero"),
                          hovermode="x unified")
        fig.update_yaxes(tickprefix="R$ ", selector=dict(anchor="x"))
        tab = pd.DataFrame({"Mês": x, "Faturamento": m["fat"].round(2), "Margem %": (m["margem"] * 100).round(1),
                            "Mesmo mês ano anterior": m["fat_aa"].round(2)})
        chart("vg_evol", "Evolução do faturamento",
              "Barras = faturamento do mês · linha amarela = margem % · tracejado = mesmo mês do ano anterior",
              fig, tab)

    with b:
        perc = (ating or 0) * 100
        maxv = max(120, np.ceil(perc / 10) * 10 + 10)
        steps = []
        n_steps = 12
        for i in range(n_steps):
            t = i / (n_steps - 1)
            # gradiente laranja → amarelo
            r_, g_, b_ = (int(0xF0 + (0xF0 - 0xF0) * t), int(0x73 + (0xFA - 0x73) * t), int(0x35 + (0x28 - 0x35) * t))
            steps.append(dict(range=[maxv * i / n_steps, maxv * (i + 1) / n_steps],
                              color=f"rgba({r_},{g_},{b_},{0.18 + 0.5 * (i * maxv / n_steps <= perc)})"))
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=perc,
            number=dict(suffix="%", valueformat=".1f", font=dict(family="Space Grotesk", size=44, color=TEXT)),
            gauge=dict(
                shape="angular", axis=dict(range=[0, maxv], tickcolor=MUTED, tickfont=dict(color=MUTED, size=10),
                                           ticksuffix="%"),
                bar=dict(color="rgba(0,0,0,0)", thickness=0.0), bgcolor=SURFACE, borderwidth=0,
                steps=steps,
                threshold=dict(line=dict(color=TEXT, width=3), thickness=0.95, value=perc),
            ),
        ))
        fig.add_annotation(x=0.5, y=-0.12, xref="paper", yref="paper", showarrow=False,
                           text=f"<b>{moeda_curta(r['fat'])}</b> realizado de <b>{moeda_curta(meta)}</b> de meta",
                           font=dict(size=13, color=TEXT))
        fig.add_annotation(x=0.5, y=-0.24, xref="paper", yref="paper", showarrow=False,
                           text="Meta de 100% = linha de chegada", font=dict(size=11, color=MUTED))
        style(fig, 360, legend=False, margin=dict(l=30, r=30, t=30, b=70))
        chart("vg_gauge", "Meta × realizado", "Quanto do objetivo de faturamento do período já foi atingido",
              fig, pd.DataFrame({"Realizado": [round(r["fat"], 2)], "Meta": [meta], "Atingimento %": [round(perc, 1)]}))

    # ------------------------------------------------------------------ 1.3 / 1.4 / 1.5
    c1, c2, c3 = st.columns(3)
    with c1:
        if ctx.lojas:
            g = it.groupby("vendedor", observed=True)["valor_liquido"].sum().sort_values(ascending=False)
            g = g[g > 0]
            if len(g) > 7:
                g = pd.concat([g.iloc[:6], pd.Series({"Outros": g.iloc[6:].sum()})])
            titulo, sub, campo = (f"Faturamento por vendedor — {ctx.lojas[0]}",
                                  "Detalhe da loja selecionada (loja → vendedor)", None)
            cores = SEQ[: len(g)]
        else:
            src = itens(D, ctx, ignore=("loja",))
            g = src.groupby("loja", observed=True)["valor_liquido"].sum().reindex(["Centro", "Barra Mansa", "Resende"]).dropna()
            titulo, sub, campo = ("Faturamento por loja", "Escolha uma loja no filtro para detalhar por vendedor", "loja")
            cores = [LOJA_COR[k] for k in g.index]
        tot = g.sum()
        fig = go.Figure(go.Pie(
            labels=list(g.index), values=g.values, hole=0.66, sort=False,
            marker=dict(colors=cores, line=dict(color=SURFACE, width=3)),
            textinfo="percent", textfont=dict(color=TEXT, size=12),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent} do total<extra></extra>",
        ))
        fig.add_annotation(text=f"<b>{moeda_curta(tot)}</b><br><span style='font-size:11px;color:{MUTED}'>TOTAL</span>",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=18, color=TEXT, family="Space Grotesk"))
        style(fig, 330)
        fig.update_layout(legend=dict(orientation="h", y=-0.08, yanchor="top", x=0.5, xanchor="center"))
        tab = pd.DataFrame({"Item": g.index, "Faturamento": g.values.round(2), "% do total": (g.values / tot * 100).round(1)})
        chart("vg_loja", titulo, sub, fig, tab)

    with c2:
        mm = metas_mensal(D, ctx)
        bl = pd.DataFrame({"real": m["fat"], "meta": mm.reindex(m.index)}).tail(12)
        bl = bl.iloc[::-1]
        y = [mes_ano_curto(d) for d in bl.index]
        bateu = bl["real"] >= bl["meta"].fillna(np.inf)
        cores = [POS if b_ else CRIT for b_ in bateu]
        at = (bl["real"] / bl["meta"]).values
        fig = go.Figure()
        fig.add_bar(y=y, x=bl["meta"], orientation="h", marker=dict(color=rgba("#FFFFFF", .06), cornerradius=4),
                    width=0.8, hoverinfo="skip", showlegend=False)
        fig.add_bar(y=y, x=bl["real"], orientation="h", marker=dict(color=cores, cornerradius=4), width=0.42,
                    name="Realizado", customdata=np.c_[bl["meta"].fillna(0), at * 100],
                    hovertemplate="<b>%{y}</b><br>Realizado: R$ %{x:,.2f}<br>Meta: R$ %{customdata[0]:,.2f}"
                                  "<br>Atingimento: %{customdata[1]:.1f}%<extra></extra>")
        fig.add_scatter(y=y, x=bl["meta"], mode="markers", name="Meta",
                        marker=dict(symbol="line-ns", size=22, line=dict(color=YELLOW, width=3)),
                        hovertemplate="Meta: R$ %{x:,.2f}<extra></extra>")
        style(fig, 330)
        fig.update_layout(barmode="overlay")
        fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickprefix="R$ ")
        fig.update_yaxes(showgrid=False)
        tab = pd.DataFrame({"Mês": y, "Realizado": bl["real"].round(2).values, "Meta": bl["meta"].values,
                            "Atingimento %": (at * 100).round(1)})
        chart("vg_bullet", "Meta × realizado por mês",
              "Verde = meta batida · vermelho = abaixo · traço amarelo = meta (últimos 12 meses do período)", fig, tab)

    with c3:
        dsp = despesas(D, ctx)["valor"].sum()
        res = r["lucro"] - dsp
        etapas = ["Fat.<br>bruto", "Descon-<br>tos", "Fat.<br>líquido", "CMV", "Lucro<br>bruto", "Despe-<br>sas", "Resul-<br>tado"]
        vals = [r["bruto"], -r["desc"], r["fat"], -r["cmv"], r["lucro"], -dsp, res]
        fig = go.Figure(go.Waterfall(
            x=etapas, y=[r["bruto"], -r["desc"], 0, -r["cmv"], 0, -dsp, 0],
            measure=["absolute", "relative", "total", "relative", "total", "relative", "total"],
            text=[moeda_curta(v) for v in vals], textposition="outside", textfont=dict(size=10, color=TEXT),
            increasing=dict(marker=dict(color=POS)), decreasing=dict(marker=dict(color=CRIT)),
            totals=dict(marker=dict(color=ORANGE)), connector=dict(line=dict(color="rgba(255,255,255,0.15)", width=1)),
            hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>",
        ))
        style(fig, 330, legend=False)
        fig.update_yaxes(tickprefix="R$ ", rangemode="tozero")
        fig.update_xaxes(tickangle=0, tickfont=dict(size=10))
        fig.update_layout(margin=dict(l=8, r=8, t=36, b=8))
        tab = pd.DataFrame({"Etapa": [e.replace("-<br>", "").replace("<br>", " ") for e in etapas], "Valor": np.round(vals, 2)})
        chart("vg_cascata", "Do faturamento ao resultado",
              f"Margem operacional: {pct(div(res, r['fat']))} · despesas das lojas no período", fig, tab)

    footer()
