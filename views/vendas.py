"""PÁGINA 2 — Vendas & Desempenho Comercial: o que, quando, por onde e quem vende mais?"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.data import LOJA_CURTA
from core.filters import cross_callback, itens, sel_key
from core.metrics import div, resumo, spark12, var
from core.theme import (
    DIA_ABREV, INFO, MUTED, ORANGE, PLOTLY_CONFIG, SCALE, SEQ, SURFACE, TEXT, YELLOW,
    data_br, moeda, moeda_curta, num, pct, rgba, style,
)
from core.ui import bar_cell, card_header, chart, footer, hbar, html_card, kpi, kpi_row, pill, table, tone_meta
from views._common import TODOS, shell

PAGE = "vendas"
GRAN = {"Dia": "D", "Semana": "W-MON", "Mês": "MS"}


def _extra():
    c = st.columns([1.2, 4])
    with c[0]:
        st.session_state.setdefault("p_gran", "Mês")
        st.segmented_control("Granularidade da evolução", list(GRAN), key="p_gran")


def _orcamentos(D, ctx, ini, fim):
    o = D["orcamentos"]
    o = o[(o["data_orcamento"] >= ini) & (o["data_orcamento"] <= fim)]
    if ctx.loja_ids:
        o = o[o["id_loja"].isin(ctx.loja_ids)]
    if ctx.vends:
        o = o[o["vendedor"].isin(ctx.vends)]
    if ctx.canais:
        o = o[o["canal"].isin(ctx.canais)]
    return o


def _conv(o):
    c = (o["status_orcamento"] == "Convertido").sum()
    p = (o["status_orcamento"] == "Perdido").sum()
    return div(c, c + p)


def render():
    D, ctx = shell(PAGE, "Vendas & Comercial", "O que, quando, por onde e quem vende mais?", TODOS, _extra)

    it = itens(D, ctx)
    itp = itens(D, ctx, ini=ctx.pini, fim=ctx.pfim)
    r, rp = resumo(it), resumo(itp)
    o, op = _orcamentos(D, ctx, ctx.ini, ctx.fim), _orcamentos(D, ctx, ctx.pini, ctx.pfim)
    conv, convp = _conv(o), _conv(op)

    c = kpi_row()
    with c[0]:
        kpi("fat", "Faturamento", moeda_curta(r["fat"]), "dollar", delta=var(r["fat"], rp["fat"]), comp=ctx.comp,
            spark=spark12(D, ctx, "fat"), tom="hl", info="Soma do valor líquido das vendas (sem frete e sem canceladas).")
    with c[1]:
        kpi("n", "Nº de vendas", num(r["n"]), "cart", delta=var(r["n"], rp["n"]), comp=ctx.comp,
            spark=spark12(D, ctx, "n"), info="Quantidade de vendas (notas) concluídas.")
    with c[2]:
        kpi("itens", "Itens vendidos", num(r["linhas"]), "package", delta=var(r["linhas"], rp["linhas"]),
            comp=ctx.comp, info=f"Linhas de produto nas vendas · {num(r['itens_venda'], 1)} itens por venda em média.")
    with c[3]:
        kpi("ticket", "Ticket médio", moeda(r["ticket"]), "receipt", delta=var(r["ticket"], rp["ticket"]),
            comp=ctx.comp, spark=spark12(D, ctx, "ticket"), info="Faturamento ÷ nº de vendas.")
    with c[4]:
        kpi("desc", "Descontos concedidos", moeda_curta(r["desc"]), "tag",
            nota=f'<span style="color:var(--brand-yellow);font-weight:600">{pct(r["desc_pct"])}</span> do faturamento bruto',
            info="Soma dos descontos dados nos itens. Percentual = descontos ÷ faturamento bruto.")
    with c[5]:
        kpi("conv", "Conversão de orçamentos", pct(conv), "file",
            delta=(conv - convp) if conv is not None and convp is not None else None, pp=True, comp=ctx.comp,
            info="Orçamentos convertidos ÷ (convertidos + perdidos). Orçamentos em aberto não entram na conta.")

    if it.empty:
        chart("vd_vazio", "Sem dados", "", None)
        footer()
        return

    # ---------------------------------------------------------------- 2.1 / 2.2
    a, b = st.columns([2, 1])
    with a:
        gran = st.session_state.get("p_gran") or "Mês"
        f = GRAN[gran]
        s = it.groupby(pd.Grouper(key="data", freq=f))["valor_liquido"].sum()
        sp = itp.groupby(pd.Grouper(key="data", freq=f))["valor_liquido"].sum()
        n = min(len(s), len(sp))
        fig = go.Figure()
        if n and ctx.comp is not None:
            prev_vals = list(sp.values[:n]) + [None] * (len(s) - n)
            fig.add_scatter(x=s.index, y=prev_vals, name=f"Período anterior", mode="lines",
                            line=dict(color=rgba(INFO, .75), dash="dash", width=1.6, shape="spline"),
                            hovertemplate="Anterior: R$ %{y:,.2f}<extra></extra>")
        fig.add_scatter(x=s.index, y=s.values, name="Faturamento", mode="lines", fill="tozeroy",
                        line=dict(color=ORANGE, width=2.6, shape="spline"),
                        fillgradient=dict(type="vertical", colorscale=[[0, rgba(ORANGE, 0)], [1, rgba(ORANGE, .35)]]),
                        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Faturamento: <b>R$ %{y:,.2f}</b><extra></extra>")
        style(fig, 380)
        fig.update_layout(hovermode="x unified",
                          xaxis=dict(rangeslider=dict(visible=True, thickness=0.07, bgcolor=SURFACE,
                                                      bordercolor="rgba(255,255,255,0.08)"), type="date"))
        fig.update_yaxes(tickprefix="R$ ", rangemode="tozero")
        tab = pd.DataFrame({"Data": [data_br(d) for d in s.index], "Faturamento": s.values.round(2)})
        chart("vd_evol", "Evolução das vendas",
              f"Faturamento por {gran.lower()} · tracejado = período anterior · arraste a barra inferior para dar zoom",
              fig, tab)

    with b:
        g = it.groupby("canal", observed=True)["valor_liquido"].sum().sort_values(ascending=False)
        g = g[g > 0]
        tot = g.sum()
        fig = go.Figure(go.Pie(labels=list(g.index), values=g.values, hole=0.66, sort=False,
                               marker=dict(colors=SEQ, line=dict(color=SURFACE, width=3)), textinfo="percent",
                               textfont=dict(color=TEXT, size=11),
                               hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent} do total<extra></extra>"))
        fig.add_annotation(text=f"<b>{moeda_curta(tot)}</b><br><span style='font-size:11px;color:{MUTED}'>TOTAL</span>",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=17, color=TEXT, family="Space Grotesk"))
        style(fig, 380)
        fig.update_layout(legend=dict(orientation="h", y=-0.05, yanchor="top", x=0.5, xanchor="center"))
        chart("vd_canal", "Vendas por canal", "Participação de cada canal no faturamento", fig,
              pd.DataFrame({"Canal": g.index, "Faturamento": g.values.round(2), "%": (g.values / tot * 100).round(1)}))

    # ---------------------------------------------------------------- 2.3 / 2.4 / 2.5
    c1, c2, c3 = st.columns(3)
    with c1:
        cat_sel = ctx.cross.get("categoria")
        if cat_sel:
            src = itens(D, ctx, ignore=("subcategoria",))
            g = src.groupby("subcategoria", observed=True)["valor_liquido"].sum()
            campo, titulo = "subcategoria", f"Faturamento por subcategoria — {cat_sel}"
            sub = "Clique numa barra para filtrar · remova o chip ⚡ Categoria para voltar"
        else:
            src = itens(D, ctx, ignore=("categoria", "subcategoria"))
            g = src.groupby("categoria", observed=True)["valor_liquido"].sum()
            campo, titulo = "categoria", "Faturamento por categoria"
            sub = "Clique numa barra para filtrar a página e abrir as subcategorias"
        g = g[g > 0].sort_values(ascending=False)
        tot = g.sum()
        sel = ctx.cross.get(campo)
        cores = [ORANGE if (sel is None or k == sel) else rgba(ORANGE, .3) for k in g.index]
        fig = hbar(g.index, g.values, [f"{moeda_curta(v)} · {pct(v / tot)}" for v in g.values], cores, height=400,
                   hover="<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>")
        k = sel_key(PAGE, campo)
        chart("vd_cat", titulo, sub, fig,
              pd.DataFrame({campo.title(): g.index, "Faturamento": g.values.round(2), "%": (g.values / tot * 100).round(1)}),
              on_select=cross_callback(PAGE, campo, k, lambda p: p.get("y")), sel_key=k)

    with c2:
        hz = it.drop_duplicates("id_venda")
        hz = hz[(hz["dow"] <= 5) & hz["hora_int"].between(7, 18)]
        mat = hz.pivot_table(index="dow", columns="hora_int", values="id_venda", aggfunc="count").reindex(
            index=range(6), columns=range(7, 19)).fillna(0)
        fig = go.Figure(go.Heatmap(
            z=mat.values, x=[f"{h}h" for h in mat.columns], y=DIA_ABREV[:6], colorscale=SCALE, xgap=3, ygap=3,
            showscale=False, hovertemplate="<b>%{y}, %{x}</b><br>%{z:,.0f} vendas<extra></extra>",
        ))
        style(fig, 400, legend=False)
        fig.update_yaxes(autorange="reversed", showgrid=False)
        fig.update_xaxes(side="top")
        tab = mat.astype(int)
        tab.index = DIA_ABREV[:6]
        tab.columns = [f"{h}h" for h in tab.columns]
        chart("vd_heat", "Mapa de calor de movimento", "Nº de vendas por dia da semana × hora do dia", fig,
              tab.reset_index(names="Dia"))

    with c3:
        modo = st.session_state.get("p_top_modo") or "Faturamento"
        col = "valor_liquido" if modo == "Faturamento" else "quantidade"
        g = it.groupby("produto", observed=True)[col].sum().sort_values(ascending=False).head(10)
        textos = [moeda_curta(v) if modo == "Faturamento" else num(v) for v in g.values]
        cores = [ORANGE if i < 3 else rgba(ORANGE, .55) for i in range(len(g))]
        fig = hbar(g.index, g.values, textos, cores, height=345, rank=True,
                   hover="<b>%{y}</b><br>%{text}<extra></extra>")
        with st.container(key="card_vd_top"):
            card_header("vd_top", "Top 10 produtos", "Ranking do período · alterne entre faturamento e quantidade",
                        pd.DataFrame({"Produto": g.index, modo: g.values.round(2)}))
            st.session_state.setdefault("p_top_modo", "Faturamento")
            st.segmented_control("Ordenar por", ["Faturamento", "Quantidade"], key="p_top_modo",
                                 label_visibility="collapsed")
            st.plotly_chart(fig, key="pl_vd_top", config=PLOTLY_CONFIG, use_container_width=True)

    # ---------------------------------------------------------------- 2.6 / 2.7
    a, b = st.columns([2, 1])
    with a:
        vend = D["vendedores"].drop_duplicates("vendedor").set_index("vendedor")
        g = it.groupby("vendedor", observed=True).agg(fat=("valor_liquido", "sum"), n=("id_venda", "nunique"))
        g = g[g["fat"] > 0].sort_values("fat", ascending=False)
        mt = D["metas"]
        mt = mt[(mt["nivel_meta"] == "Vendedor") & (mt["mes"] >= ctx.ini.to_period("M").to_timestamp())
                & (mt["mes"] <= ctx.mes_ref)]
        meta_v = mt.groupby("id_vendedor")["meta_faturamento"].sum()
        linhas, dados = [], []
        mx = g["fat"].max()
        for i, (nome, row) in enumerate(g.iterrows(), 1):
            cad = nome in vend.index
            idv = vend.at[nome, "id_vendedor"] if cad else None
            loja = LOJA_CURTA.get(vend.at[nome, "id_loja"], "—") if cad else "Online"
            meta_ = meta_v.get(idv) if idv is not None else None
            at = div(row["fat"], meta_)
            com = row["fat"] * (vend.at[nome, "comissao_pct"] if cad else 0)
            tk = row["fat"] / row["n"]
            linhas.append({
                "#": f"<b>{i}º</b>", "Vendedor": f"<b>{nome}</b>", "Loja": loja,
                "Faturamento": bar_cell(moeda(row["fat"], 0), row["fat"] / mx),
                "Vendas": num(row["n"]), "Ticket médio": moeda(tk),
                "% meta": pill(pct(at) if at is not None else "sem meta", tone_meta(at)),
                "Comissão": moeda(com),
            })
            dados.append({"Posição": i, "Vendedor": nome, "Loja": loja, "Faturamento": round(row["fat"], 2),
                          "Vendas": int(row["n"]), "Ticket médio": round(tk, 2),
                          "% meta": round(at * 100, 1) if at is not None else None, "Comissão": round(com, 2)})
        html_card("vd_rank", "Ranking de vendedores",
                  "% da meta individual no período · verde ≥ 100% · amarelo ≥ 85% · vermelho abaixo",
                  table(pd.DataFrame(linhas), {"#": "center", "Vendas": "right", "Ticket médio": "right",
                                               "% meta": "center", "Comissão": "right"}, max_height=540),
                  pd.DataFrame(dados))

    with b:
        emit = len(o)
        convs = o[o["status_orcamento"] == "Convertido"]
        perd = o[o["status_orcamento"] == "Perdido"]
        fig = go.Figure(go.Funnel(
            y=["Emitidos", "Convertidos"], x=[emit, len(convs)],
            text=[f"{num(emit)} · {moeda_curta(o['valor_orcado'].sum())}",
                  f"{num(len(convs))} · {moeda_curta(convs['valor_orcado'].sum())}"],
            textinfo="text", textfont=dict(color="#0A1626", size=12),
            marker=dict(color=[ORANGE, YELLOW]), connector=dict(fillcolor=rgba(ORANGE, .12)),
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} orçamentos<extra></extra>",
        ))
        style(fig, 170, legend=False, margin=dict(l=8, r=8, t=6, b=6))
        fig.update_yaxes(showgrid=False)
        mot = perd["motivo_perda"].value_counts()
        fig2 = go.Figure(go.Pie(labels=list(mot.index), values=mot.values, hole=0.62, sort=False,
                                marker=dict(colors=SEQ, line=dict(color=SURFACE, width=2)), textinfo="percent",
                                textfont=dict(size=10, color=TEXT),
                                hovertemplate="<b>%{label}</b><br>%{value:,.0f} orçamentos perdidos<br>%{percent}<extra></extra>"))
        fig2.add_annotation(text=f"<b>{num(len(perd))}</b><br><span style='font-size:10px;color:{MUTED}'>PERDIDOS</span>",
                            x=0.5, y=0.5, showarrow=False, font=dict(size=15, color=TEXT, family="Space Grotesk"))
        style(fig2, 330)
        fig2.update_layout(legend=dict(orientation="h", y=-0.02, yanchor="top", x=0.5, xanchor="center",
                                       font=dict(size=10)))
        with st.container(key="card_vd_funil"):
            card_header("vd_funil", "Funil de orçamentos", f"Conversão de {pct(conv)} · e por que perdemos",
                        pd.DataFrame({"Etapa": ["Emitidos", "Convertidos", "Perdidos", "Em aberto"],
                                      "Qtd": [emit, len(convs), len(perd), emit - len(convs) - len(perd)]}))
            st.plotly_chart(fig, key="pl_vd_funil", config=PLOTLY_CONFIG, use_container_width=True)
            st.markdown('<p class="card-title" style="margin-top:4px">Motivos de perda</p>', unsafe_allow_html=True)
            st.plotly_chart(fig2, key="pl_vd_motivos", config=PLOTLY_CONFIG, use_container_width=True)

    footer()
