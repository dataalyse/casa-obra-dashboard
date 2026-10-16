"""PÁGINA 3 — Gestão e Controle de Estoque: o que falta, o que sobra e o que comprar?"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.filters import itens
from core.metrics import abc, estoque_enriquecido, giro, mensal, meses_ate, var
from core.theme import (
    BLUE, CRIT, INFO, MUTED, ORANGE, POS, SCALE, SEQ, SIT_COR, SURFACE, TEXT, YELLOW,
    mes_ano, mes_ano_curto, moeda, moeda_curta, num, rgba, style,
)
from core.ui import chart, footer, html_card, kpi, kpi_row, pill, table
from views._common import shell

PAGE = "estoque"
APLICA = {"periodo", "loja", "depto", "cat"}
SITS = ["Normal", "Abaixo do mínimo", "Ruptura", "Excesso"]


def _extra():
    from core.data import load
    D = load()
    c = st.columns(3)
    with c[0]:
        st.multiselect("Situação do estoque", SITS, key="p_sit", placeholder="Todas")
    with c[1]:
        st.multiselect("Fornecedor", sorted(D["fornecedores"]["fornecedor"]), key="p_forn", placeholder="Todos")
    with c[2]:
        st.multiselect("Classe ABC", ["A", "B", "C"], key="p_abc", placeholder="Todas")


def _base(D, ctx):
    e = estoque_enriquecido(D, ctx)
    cls = abc(itens(D, ctx, cross=False)).set_index("produto")["classe"]
    e["classe"] = e["produto"].map(cls).fillna("C")
    if st.session_state.get("p_sit"):
        e = e[e["situacao_estoque"].isin(st.session_state["p_sit"])]
    if st.session_state.get("p_forn"):
        e = e[e["fornecedor"].isin(st.session_state["p_forn"])]
    if st.session_state.get("p_abc"):
        e = e[e["classe"].isin(st.session_state["p_abc"])]
    return e


def render():
    D, ctx = shell(PAGE, "Estoque", "O que está faltando, o que está sobrando e o que preciso comprar?", APLICA, _extra)
    e = _base(D, ctx)
    mes = ctx.mes_ref

    # série de 12 meses do valor em estoque (mesmos filtros de loja/categoria)
    ms = meses_ate(ctx.fim)
    hist = D["estoque"][D["estoque"]["mes"].isin(ms)]
    if ctx.loja_ids:
        hist = hist[hist["id_loja"].isin(ctx.loja_ids)]
    if ctx.deptos:
        hist = hist[hist["departamento"].isin(ctx.deptos)]
    if ctx.cats:
        hist = hist[hist["categoria"].isin(ctx.cats)]
    if st.session_state.get("p_forn"):
        hist = hist[hist["fornecedor"].isin(st.session_state["p_forn"])]
    serie_val = hist.groupby("mes")["valor_estoque_final"].sum().reindex(ms, fill_value=0)

    valor = e["valor_estoque_final"].sum()
    valor_ant = serie_val.iloc[-2] if len(serie_val) > 1 else None
    skus = e.loc[e["estoque_final"] > 0, "id_produto"].nunique()
    abaixo = int((e["situacao_estoque"] == "Abaixo do mínimo").sum())
    rupt = int((e["situacao_estoque"] == "Ruptura").sum())
    gir = giro(D, ctx)
    parado = e.loc[e["parado"], "valor_estoque_final"].sum()

    c = kpi_row()
    with c[0]:
        kpi("valor", "Valor em estoque", moeda_curta(valor), "boxes", delta=var(valor, valor_ant), comp="mês anterior",
            spark=serie_val.values, tom="hl",
            info=f"Valor de custo do estoque final em {mes_ano(mes)} (foto do último mês do período).")
    with c[1]:
        kpi("skus", "SKUs com saldo", num(skus), "package", nota=f"de {num(e['id_produto'].nunique())} produtos cadastrados",
            info="Produtos com estoque final maior que zero no último mês do período.")
    with c[2]:
        kpi("abaixo", "Abaixo do mínimo", num(abaixo), "alert", tom="warn" if abaixo else "",
            nota="itens (loja × produto) para repor", info="Combinações loja × produto com saldo abaixo do estoque mínimo.")
    with c[3]:
        kpi("rupt", "Em ruptura", num(rupt), "x-circle", tom="crit" if rupt else "",
            nota="itens zerados na prateleira", info="Combinações loja × produto sem estoque (ruptura).")
    with c[4]:
        kpi("giro", "Giro de estoque", f"{num(gir, 1)}x" if gir else "—", "refresh",
            nota="vezes por ano (anualizado)",
            info="CMV dos últimos 12 meses ÷ valor médio do estoque nesses 12 meses. Quanto maior, mais rápido o estoque vira venda.")
    with c[5]:
        kpi("parado", "Capital parado", moeda_curta(parado), "lock", tom="crit" if parado else "",
            nota=f"{num(e['parado'].sum())} itens sem venda há 90+ dias ou em excesso",
            info="Valor em estoque dos produtos sem venda há mais de 90 dias ou com situação 'Excesso'.")

    if e.empty:
        chart("es_vazio", "Sem dados", "", None)
        footer()
        return

    # ------------------------------------------------------------ 3.1 / 3.2 / 3.3
    c1, c2, c3 = st.columns([3, 5, 4])
    with c1:
        g = e["situacao_estoque"].value_counts().reindex(SITS).fillna(0)
        fig = go.Figure(go.Pie(
            labels=SITS, values=g.values, hole=0.66, sort=False,
            marker=dict(colors=[SIT_COR[s] for s in SITS], line=dict(color=SURFACE, width=3)),
            textinfo="percent", textfont=dict(color="#0A1626", size=11),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} itens<br>%{percent}<extra></extra>",
        ))
        fig.add_annotation(text=f"<b>{num(g.sum())}</b><br><span style='font-size:10px;color:{MUTED}'>ITENS</span>",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=17, color=TEXT, family="Space Grotesk"))
        style(fig, 360)
        fig.update_layout(legend=dict(orientation="h", y=-0.05, yanchor="top", x=0.5, xanchor="center"))
        chart("es_sit", "Situação do estoque", f"Loja × produto em {mes_ano(mes)}", fig,
              pd.DataFrame({"Situação": SITS, "Itens": g.values.astype(int)}))

    with c2:
        t = e.groupby(["categoria", "subcategoria"], observed=True).apply(
            lambda d: pd.Series({"valor": d["valor_estoque_final"].sum(),
                                 "cob": np.average(d["cobertura_dias"].clip(upper=365), weights=d["valor_estoque_final"])
                                 if d["valor_estoque_final"].sum() > 0 else 0}),
            include_groups=False,
        ).reset_index()
        t = t[t["valor"] > 0]
        cat = t.groupby("categoria").apply(
            lambda d: pd.Series({"valor": d["valor"].sum(), "cob": np.average(d["cob"], weights=d["valor"])}),
            include_groups=False,
        ).reset_index()
        ids = list(cat["categoria"]) + [f"{a}/{b}" for a, b in zip(t["categoria"], t["subcategoria"])]
        labels = list(cat["categoria"]) + list(t["subcategoria"])
        parents = [""] * len(cat) + list(t["categoria"])
        values = list(cat["valor"]) + list(t["valor"])
        cores = list(cat["cob"]) + list(t["cob"])
        fig = go.Figure(go.Treemap(
            ids=ids, labels=labels, parents=parents, values=values, branchvalues="total",
            marker=dict(colors=cores, colorscale=SCALE, cmin=0, cmax=max(90, np.nanpercentile(cores, 95)),
                        line=dict(color=SURFACE, width=2),
                        colorbar=dict(title=dict(text="Cobertura<br>(dias)", font=dict(size=10, color=MUTED)),
                                      tickfont=dict(size=10, color=MUTED), thickness=10, len=0.8)),
            texttemplate="<b>%{label}</b><br>%{customdata[0]}", customdata=np.c_[[moeda_curta(v) for v in values], cores],
            hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Cobertura média: %{customdata[1]:.0f} dias<extra></extra>",
            textfont=dict(color=TEXT), pathbar=dict(visible=True, textfont=dict(color=TEXT)),
        ))
        style(fig, 360, legend=False, margin=dict(l=4, r=4, t=28, b=4))
        chart("es_tree", "Valor em estoque por categoria",
              "Tamanho = valor · cor = cobertura em dias (escuro = pouca, amarelo = muita) · clique para abrir",
              fig, t.rename(columns={"categoria": "Categoria", "subcategoria": "Subcategoria", "valor": "Valor",
                                     "cob": "Cobertura (dias)"}).round(1))

    with c3:
        itm = itens(D, ctx, ini=ms[0], fim=ctx.fim, cross=False)
        cmv = mensal(itm, ms)["cmv"]
        x = [mes_ano_curto(d) for d in ms]
        fig = go.Figure()
        fig.add_scatter(x=x, y=serie_val.values, name="Valor em estoque", mode="lines+markers",
                        line=dict(color=INFO, width=2.6, shape="spline"), marker=dict(size=5),
                        hovertemplate="Estoque: R$ %{y:,.2f}<extra></extra>")
        fig.add_scatter(x=x, y=cmv.values, name="CMV do mês", mode="lines+markers",
                        line=dict(color=ORANGE, width=2.6, shape="spline"), marker=dict(size=5),
                        hovertemplate="CMV: R$ %{y:,.2f}<extra></extra>")
        style(fig, 360)
        fig.update_layout(hovermode="x unified")
        fig.update_yaxes(tickprefix="R$ ", rangemode="tozero")
        chart("es_evol", "Estoque × CMV", "Valor em estoque no fim de cada mês contra o custo do que foi vendido",
              fig, pd.DataFrame({"Mês": x, "Valor em estoque": serie_val.values.round(2), "CMV": cmv.values.round(2)}))

    # ------------------------------------------------------------ 3.4 / 3.5
    a, b = st.columns(2)
    with a:
        p = abc(itens(D, ctx))
        if p.empty:
            chart("es_abc", "Curva ABC", "", None)
        else:
            cor = {"A": ORANGE, "B": YELLOW, "C": INFO}
            fig = go.Figure()
            n = len(p)
            ia = int((p["classe"] == "A").sum())
            ib = int((p["classe"] == "B").sum())
            for x0, x1, cl in [(-0.5, ia - 0.5, "A"), (ia - 0.5, ia + ib - 0.5, "B"), (ia + ib - 0.5, n - 0.5, "C")]:
                fig.add_vrect(x0=x0, x1=x1, fillcolor=rgba(cor[cl], .07), line_width=0,
                              annotation_text=f"<b>{cl}</b>", annotation_position="top left",
                              annotation_font=dict(color=cor[cl], size=13))
            fig.add_bar(x=list(range(n)), y=p["fat"], marker=dict(color=[cor[c_] for c_ in p["classe"]]),
                        customdata=np.c_[p["produto"], p["classe"], p["acum"] * 100], name="Faturamento",
                        hovertemplate="<b>%{customdata[0]}</b><br>R$ %{y:,.2f}<br>Classe %{customdata[1]} · "
                                      "acumulado %{customdata[2]:.1f}%<extra></extra>")
            fig.add_scatter(x=list(range(n)), y=p["acum"] * 100, yaxis="y2", name="% acumulado", mode="lines",
                            line=dict(color=TEXT, width=2), hovertemplate="Acumulado: %{y:.1f}%<extra></extra>")
            for lim in (80, 95):
                fig.add_shape(type="line", xref="paper", x0=0, x1=1, yref="y2", y0=lim, y1=lim,
                              line=dict(color=YELLOW, dash="dash", width=1))
            style(fig, 380)
            fig.update_layout(bargap=0.05, yaxis2=dict(overlaying="y", side="right", range=[0, 102], ticksuffix="%",
                                                       showgrid=False, tickfont=dict(color=MUTED, size=11)))
            fig.update_xaxes(showticklabels=False, title_text=f"{n} produtos ordenados por faturamento")
            fig.update_yaxes(tickprefix="R$ ")
            chart("es_abc", "Curva ABC (Pareto)",
                  f"A = {ia} produtos fazem 80% do faturamento · B = {ib} até 95% · C = {n - ia - ib} restantes",
                  fig, p[["produto", "categoria", "fat", "acum", "classe"]].rename(
                      columns={"produto": "Produto", "categoria": "Categoria", "fat": "Faturamento",
                               "acum": "% acumulado", "classe": "Classe"}).round(3))

    with b:
        cr = e[e["estoque_minimo"] > 0].copy()
        cr["rel"] = cr["estoque_final"] / cr["estoque_minimo"]
        cr = cr.sort_values(["rel", "venda_dia"], ascending=[True, False]).head(15)
        lab = [f"{p_} · {l_}" for p_, l_ in zip(cr["produto"], cr["loja"])][::-1]
        fig = go.Figure()
        fig.add_bar(y=lab, x=cr["estoque_minimo"].values[::-1], orientation="h", name="Estoque mínimo",
                    marker=dict(color=rgba(INFO, .45), cornerradius=4),
                    hovertemplate="<b>%{y}</b><br>Mínimo: %{x:,.0f}<extra></extra>")
        fig.add_bar(y=lab, x=cr["estoque_final"].values[::-1], orientation="h", name="Estoque atual",
                    marker=dict(color=[SIT_COR.get(s, ORANGE) for s in cr["situacao_estoque"].values[::-1]], cornerradius=4),
                    hovertemplate="<b>%{y}</b><br>Atual: %{x:,.0f}<extra></extra>")
        style(fig, 380)
        fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.05)
        fig.update_yaxes(showgrid=False, tickfont=dict(size=10))
        fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
        chart("es_min", "Estoque atual × mínimo", "Os 15 itens mais críticos (menor relação atual ÷ mínimo)", fig,
              cr[["produto", "loja", "estoque_final", "estoque_minimo", "situacao_estoque"]].rename(
                  columns={"produto": "Produto", "loja": "Loja", "estoque_final": "Atual", "estoque_minimo": "Mínimo",
                           "situacao_estoque": "Situação"}))

    # ------------------------------------------------------------ 3.6 / 3.7
    a, b = st.columns([1, 2])
    with a:
        faixas = ["31–60 dias", "61–90 dias", "90+ dias"]
        s = e[e["dias_sem_venda"] > 30].copy()
        s["faixa"] = pd.cut(s["dias_sem_venda"], [30, 60, 90, 10**6], labels=faixas)
        deps = sorted(e["departamento"].dropna().unique())
        fig = go.Figure()
        for i, d in enumerate(deps):
            sd = s[s["departamento"] == d].groupby("faixa", observed=False).agg(
                v=("valor_estoque_final", "sum"), n=("id_produto", "count")).reindex(faixas).fillna(0)
            fig.add_bar(x=faixas, y=sd["v"], name=d, marker=dict(color=SEQ[i % len(SEQ)]),
                        customdata=sd["n"], hovertemplate=f"<b>{d}</b><br>%{{x}}<br>R$ %{{y:,.2f}} · %{{customdata:,.0f}} SKUs<extra></extra>")
        tot = s.groupby("faixa", observed=False).agg(v=("valor_estoque_final", "sum"), n=("id_produto", "count")).reindex(faixas).fillna(0)
        for f_, row in tot.iterrows():
            fig.add_annotation(x=f_, y=row["v"], text=f"<b>{moeda_curta(row['v'])}</b><br>{num(row['n'])} SKUs",
                               showarrow=False, yshift=18, font=dict(size=10, color=TEXT))
        style(fig, 420)
        fig.update_layout(barmode="stack")
        fig.update_traces(marker_cornerradius=4)
        fig.update_yaxes(tickprefix="R$ ", rangemode="tozero", range=[0, max(1, tot["v"].max()) * 1.3])
        chart("es_parado", "Produtos sem movimentação", "Valor parado por tempo sem venda, por departamento",
              fig, tot.reset_index().rename(columns={"faixa": "Faixa", "v": "Valor parado", "n": "SKUs"}))

    with b:
        rep = e[e["sugestao"] > 0].copy()
        rep["prio"] = np.where(rep["risco_ruptura"] | (rep["situacao_estoque"] == "Ruptura"), 0,
                               np.where(rep["situacao_estoque"] == "Abaixo do mínimo", 1, 2))
        rep = rep.sort_values(["prio", "cobertura_dias", "valor_sugestao"], ascending=[True, True, False])
        linhas = []
        for _, r in rep.head(80).iterrows():
            alerta = pill("🔴 Risco de ruptura", "crit") if r["prio"] == 0 else (
                pill("🟡 Abaixo do mínimo", "warn") if r["prio"] == 1 else pill("Reposição", "info"))
            linhas.append({
                "Alerta": alerta, "Produto": f"<b>{r['produto']}</b>", "Loja": r["loja"], "Fornecedor": r["fornecedor"],
                "Atual": num(r["estoque_final"]), "Mínimo": num(r["estoque_minimo"]),
                "Cobertura": f"{num(r['cobertura_dias'])} d", "Lead time": f"{int(r['lead_time_dias'])} d",
                "Venda/dia": num(r["venda_dia"], 1), "Qtd. sugerida": f"<b style='color:{YELLOW}'>{num(r['sugestao'])}</b>",
                "Valor estimado": moeda(r["valor_sugestao"]),
            })
        dados = rep[["produto", "loja", "fornecedor", "estoque_final", "estoque_minimo", "cobertura_dias",
                     "lead_time_dias", "venda_dia", "sugestao", "valor_sugestao", "risco_ruptura"]].rename(columns={
            "produto": "Produto", "loja": "Loja", "fornecedor": "Fornecedor", "estoque_final": "Estoque atual",
            "estoque_minimo": "Mínimo", "cobertura_dias": "Cobertura (dias)", "lead_time_dias": "Lead time (dias)",
            "venda_dia": "Venda média/dia", "sugestao": "Qtd sugerida", "valor_sugestao": "Valor estimado",
            "risco_ruptura": "Risco de ruptura"}).round(2)
        body = table(pd.DataFrame(linhas), {c_: "right" for c_ in ["Atual", "Mínimo", "Cobertura", "Lead time",
                                                                     "Venda/dia", "Qtd. sugerida", "Valor estimado"]},
                     max_height=400) if linhas else '<div class="empty">Nenhuma reposição necessária</div>'
        html_card("es_repor", "Sugestão de reposição",
                  f"{num(len(rep))} itens · {moeda_curta(rep['valor_sugestao'].sum())} em compras sugeridas · "
                  "venda média de 3 meses × (lead time + 15 dias) + mínimo − saldo · exporte em ⋯", body, dados)

    footer()
