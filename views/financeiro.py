"""PÁGINA 5 — Financeiro: quanto tenho a receber e a pagar, e como está o caixa? (data-base 30/09/2026)"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.data import HOJE
from core.filters import itens, vendas
from core.metrics import despesas, div, meses_periodo, pagar, receber, var
from core.theme import (
    CRIT, INFO, MUTED, ORANGE, POS, SEQ, SURFACE, TEXT, YELLOW, SCALE,
    data_br, mes_ano_curto, moeda, moeda_curta, num, pct, rgba, style,
)
from core.ui import chart, footer, html_card, kpi, kpi_row, pill, table
from views._common import shell

PAGE = "finan"
APLICA = {"periodo", "loja"}
TIPOS = ["Boleto", "Crediário próprio", "Cartão (operadora)"]
STATUS = ["A vencer", "Vencido", "Pago no prazo", "Pago com atraso"]
GRUPOS = ["À vista", "Cartão", "A prazo"]


def _extra():
    c = st.columns(2)
    with c[0]:
        st.multiselect("Tipo de recebível", TIPOS, key="p_tiporec", placeholder="Todos")
    with c[1]:
        st.multiselect("Status do título", STATUS, key="p_status", placeholder="Todos")


def _cr(D, ctx):
    cr = receber(D, ctx)
    if st.session_state.get("p_tiporec"):
        cr = cr[cr["tipo_recebivel"].isin(st.session_state["p_tiporec"])]
    if st.session_state.get("p_status"):
        cr = cr[cr["status_titulo"].isin(st.session_state["p_status"])]
    return cr


def _fluxo(D, ctx, cr, ini, fim):
    """Entradas = vendas à vista (data da venda) + recebimentos de títulos; saídas = contas pagas."""
    v = vendas(D, ctx, ini, fim)
    av = v[v["grupo"] == "À vista"].groupby("ano_mes")["valor_total_nf"].sum()
    rec = cr[(cr["data_pagamento"] >= ini) & (cr["data_pagamento"] <= fim)]
    rec = rec.groupby(rec["data_pagamento"].dt.to_period("M").dt.to_timestamp())["valor_recebido"].sum()
    cp = pagar(D, ctx)
    cp = cp[(cp["data_pagamento"] >= ini) & (cp["data_pagamento"] <= fim)]
    sai = cp.groupby(cp["data_pagamento"].dt.to_period("M").dt.to_timestamp())["valor"].sum()
    return av, rec, sai


def render():
    D, ctx = shell(PAGE, "Financeiro", f"Quanto tenho a receber e a pagar, e como está o caixa? · data-base {data_br(HOJE)}",
                   APLICA, _extra)
    cr = _cr(D, ctx)
    aberto = cr[cr["status_titulo"].isin(["A vencer", "Vencido"])]
    venc = cr[cr["status_titulo"] == "Vencido"]
    avencer = cr[cr["status_titulo"] == "A vencer"]
    base_inad = cr.loc[cr["data_vencimento"] <= HOJE, "valor_titulo"].sum()
    inad = div(venc["valor_titulo"].sum(), base_inad)
    cp = pagar(D, ctx)
    cp_aberto = cp[cp["status_conta"] == "A vencer"]

    av, rec, sai = _fluxo(D, ctx, cr, ctx.ini, ctx.fim)
    saldo = av.sum() + rec.sum() - sai.sum()
    avp, recp, saip = _fluxo(D, ctx, cr, ctx.pini, ctx.pfim)
    saldop = avp.sum() + recp.sum() - saip.sum()

    pagos = cr[cr["data_pagamento"].notna()]
    pmr = (pagos["data_pagamento"] - pagos["data_emissao"]).dt.days.mean() if not pagos.empty else None

    c = kpi_row()
    with c[0]:
        kpi("aberto", "A receber em aberto", moeda_curta(aberto["valor_titulo"].sum()), "wallet", tom="hl",
            nota=f"{num(len(aberto))} títulos · prazo médio de recebimento {num(pmr)} dias",
            info="Soma dos títulos a vencer + vencidos na data-base.")
    with c[1]:
        kpi("venc", "Vencidos", moeda_curta(venc["valor_titulo"].sum()), "alert", tom="crit",
            nota=f"{num(len(venc))} títulos em atraso", info="Títulos não pagos com vencimento já passado.")
    with c[2]:
        kpi("avencer", "A vencer", moeda_curta(avencer["valor_titulo"].sum()), "clock",
            nota=f"{num(len(avencer))} títulos", info="Títulos com vencimento depois da data-base.")
    with c[3]:
        kpi("inad", "Inadimplência", pct(inad), "percent", tom="crit" if (inad or 0) > .03 else "",
            nota="vencidos ÷ títulos já vencíveis",
            info="Valor vencido e não pago ÷ valor de todos os títulos com vencimento até a data-base.")
    with c[4]:
        kpi("pagar", "Contas a pagar em aberto", moeda_curta(cp_aberto["valor"].sum()), "file",
            nota=f"{num(len(cp_aberto))} contas a vencer", info="Fornecedores e despesas ainda não pagos.")
    with c[5]:
        kpi("saldo", "Saldo de caixa do período", moeda_curta(saldo), "banknote", delta=var(saldo, saldop),
            comp=ctx.comp, tom="hl" if saldo >= 0 else "crit",
            info="Entradas (vendas à vista + recebimentos de títulos) − saídas (contas pagas) no período.")

    # ------------------------------------------------------------ 5.1 / 5.2
    a, b = st.columns([2, 1])
    with a:
        ms = meses_periodo(ctx)
        ent = av.reindex(ms, fill_value=0) + rec.reindex(ms, fill_value=0)
        sa = sai.reindex(ms, fill_value=0)
        acum = (ent - sa).cumsum()
        x = [mes_ano_curto(m) for m in ms]
        fig = go.Figure()
        fig.add_bar(x=x, y=ent, name="Entradas", marker=dict(color=POS, cornerradius=6),
                    hovertemplate="Entradas: R$ %{y:,.2f}<extra></extra>")
        fig.add_bar(x=x, y=-sa, name="Saídas", marker=dict(color=CRIT, cornerradius=6),
                    customdata=sa, hovertemplate="Saídas: R$ %{customdata:,.2f}<extra></extra>")
        fig.add_scatter(x=x, y=acum, name="Saldo acumulado", mode="lines+markers",
                        line=dict(color=YELLOW, width=2.6, shape="spline"), marker=dict(size=6),
                        hovertemplate="Saldo acumulado: R$ %{y:,.2f}<extra></extra>")
        style(fig, 380)
        fig.update_layout(barmode="relative", hovermode="x unified")
        fig.update_yaxes(tickprefix="R$ ", zeroline=True, zerolinecolor="rgba(255,255,255,0.2)")
        chart("fn_fluxo", "Fluxo de caixa",
              "Verde = entradas · vermelho = saídas · amarelo = saldo acumulado no período", fig,
              pd.DataFrame({"Mês": x, "Entradas": ent.values.round(2), "Saídas": sa.values.round(2),
                            "Saldo acumulado": acum.values.round(2)}))

    with b:
        it = itens(D, ctx)
        g = it.groupby("forma_pagamento", observed=True)["valor_liquido"].sum().sort_values(ascending=False)
        g = g[g > 0]
        tot = g.sum()
        fig = go.Figure(go.Pie(labels=list(g.index), values=g.values, hole=0.64, sort=False,
                               marker=dict(colors=SEQ, line=dict(color=SURFACE, width=3)), textinfo="percent",
                               textfont=dict(color=TEXT, size=10),
                               hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"))
        fig.add_annotation(text=f"<b>{moeda_curta(tot)}</b><br><span style='font-size:11px;color:{MUTED}'>VENDAS</span>",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=16, color=TEXT, family="Space Grotesk"))
        style(fig, 380)
        fig.update_layout(legend=dict(orientation="h", y=-0.03, yanchor="top", x=0.5, xanchor="center",
                                      font=dict(size=10)))
        chart("fn_forma", "Forma de pagamento", "Como os clientes pagam (faturamento do período)", fig,
              pd.DataFrame({"Forma": g.index, "Faturamento": g.values.round(2), "%": (g.values / tot * 100).round(1)}))

    # ------------------------------------------------------------ 5.3 / 5.4 / 5.5
    c1, c2, c3 = st.columns(3)
    with c1:
        piv = it.groupby(["ano_mes", "grupo"], observed=True)["valor_liquido"].sum().unstack().reindex(
            columns=GRUPOS).reindex(ms).fillna(0)
        share = piv.div(piv.sum(axis=1).replace(0, np.nan), axis=0) * 100
        fig = go.Figure()
        for i, gname in enumerate(GRUPOS):
            fig.add_bar(x=x, y=share[gname], name=gname, marker=dict(color=[POS, ORANGE, INFO][i]),
                        hovertemplate=f"{gname}: %{{y:.1f}}%<extra></extra>")
        style(fig, 340)
        fig.update_layout(barmode="stack", hovermode="x unified", bargap=0.2)
        fig.update_yaxes(ticksuffix="%", range=[0, 100])
        chart("fn_mix", "À vista × cartão × a prazo", "Mudança do mix de pagamento mês a mês (100%)", fig,
              share.round(1).reset_index(names="Mês").assign(Mês=x))

    with c2:
        faixas = ["1-30 dias", "31-60 dias", "61-90 dias", "+90 dias"]
        g = venc.groupby("faixa_atraso")["valor_titulo"].agg(["sum", "count"]).reindex(faixas).fillna(0)
        cores = [YELLOW, ORANGE, "#FF8FB1", CRIT]
        fig = go.Figure(go.Bar(
            x=[f.replace("-", "–") for f in faixas], y=g["sum"], marker=dict(color=cores, cornerradius=6),
            text=[f"{moeda_curta(v)}<br>{num(n)} títulos" for v, n in zip(g["sum"], g["count"])],
            textposition="outside", textfont=dict(size=10, color=TEXT), cliponaxis=False,
            hovertemplate="<b>%{x} de atraso</b><br>R$ %{y:,.2f}<extra></extra>",
        ))
        style(fig, 340, legend=False)
        fig.update_yaxes(tickprefix="R$ ", rangemode="tozero", range=[0, max(1, g["sum"].max()) * 1.3])
        chart("fn_aging", "Aging dos vencidos", "Quanto está em atraso, por tempo de atraso", fig,
              g.reset_index().rename(columns={"faixa_atraso": "Faixa", "sum": "Valor", "count": "Títulos"}))

    with c3:
        lim = HOJE + pd.Timedelta(days=60)
        rr = avencer[(avencer["data_vencimento"] > HOJE) & (avencer["data_vencimento"] <= lim)]
        pp = cp_aberto[(cp_aberto["data_vencimento"] > HOJE) & (cp_aberto["data_vencimento"] <= lim)]
        wk = lambda s: ((s - HOJE).dt.days - 1) // 7
        gr = rr.groupby(wk(rr["data_vencimento"]))["valor_titulo"].sum().reindex(range(9), fill_value=0)
        gp = pp.groupby(wk(pp["data_vencimento"]))["valor"].sum().reindex(range(9), fill_value=0)
        lab = [f"{(HOJE + pd.Timedelta(days=7 * i + 1)):%d/%m}" for i in range(9)]
        fig = go.Figure()
        fig.add_bar(x=lab, y=gr.values, name="A receber", marker=dict(color=POS, cornerradius=5),
                    hovertemplate="Semana de %{x}<br>A receber: R$ %{y:,.2f}<extra></extra>")
        fig.add_bar(x=lab, y=-gp.values, name="A pagar", marker=dict(color=CRIT, cornerradius=5), customdata=gp.values,
                    hovertemplate="Semana de %{x}<br>A pagar: R$ %{customdata:,.2f}<extra></extra>")
        style(fig, 340)
        fig.update_layout(barmode="relative")
        fig.update_yaxes(tickprefix="R$ ", zeroline=True, zerolinecolor="rgba(255,255,255,0.25)")
        chart("fn_cal", "Calendário de vencimentos", "Próximos 60 dias, por semana · acima = receber, abaixo = pagar",
              fig, pd.DataFrame({"Semana a partir de": lab, "A receber": gr.values.round(2), "A pagar": gp.values.round(2)}))

    # ------------------------------------------------------------ 5.6 / 5.7
    a, b = st.columns(2)
    with a:
        t = venc.copy()
        t["atraso"] = (HOJE - t["data_vencimento"]).dt.days
        t = t.sort_values(["atraso", "valor_titulo"], ascending=[False, False])
        linhas = []
        for r in t.head(100).itertuples():
            tom = "crit" if r.atraso > 60 else ("warn" if r.atraso > 30 else "info")
            linhas.append({"Cliente": f"<b>{r.cliente}</b>", "Segmento": r.segmento, "Título": r.id_titulo,
                           "Parcela": f"{r.parcela}/{r.total_parcelas}", "Vencimento": data_br(r.data_vencimento),
                           "Atraso": pill(f"{num(r.atraso)} dias", tom), "Valor": moeda(r.valor_titulo)})
        html_card("fn_venc", "Títulos vencidos", f"{num(len(t))} títulos · ordenados pelo maior atraso",
                  table(pd.DataFrame(linhas), {"Parcela": "center", "Atraso": "center", "Valor": "right"}, 420)
                  if linhas else '<div class="empty">Nenhum título vencido 🎉</div>',
                  t[["cliente", "segmento", "id_titulo", "parcela", "total_parcelas", "data_vencimento", "atraso",
                     "valor_titulo", "loja"]].rename(columns={
                      "cliente": "Cliente", "segmento": "Segmento", "id_titulo": "Título", "parcela": "Parcela",
                      "total_parcelas": "Total parcelas", "data_vencimento": "Vencimento", "atraso": "Dias de atraso",
                      "valor_titulo": "Valor", "loja": "Loja"}))

    with b:
        dsp = despesas(D, ctx)
        g = dsp.groupby(["grupo_despesa", "despesa"])["valor"].sum().reset_index()
        gg = g.groupby("grupo_despesa")["valor"].sum().reset_index()
        ids = list(gg["grupo_despesa"]) + [f"{a_}/{b_}" for a_, b_ in zip(g["grupo_despesa"], g["despesa"])]
        labels = list(gg["grupo_despesa"]) + list(g["despesa"])
        parents = [""] * len(gg) + list(g["grupo_despesa"])
        values = list(gg["valor"]) + list(g["valor"])
        fig = go.Figure(go.Treemap(
            ids=ids, labels=labels, parents=parents, values=values, branchvalues="total",
            marker=dict(colors=values, colorscale=SCALE, line=dict(color=SURFACE, width=2)),
            texttemplate="<b>%{label}</b><br>%{customdata}", customdata=[moeda_curta(v) for v in values],
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percentRoot:.1%} do total<extra></extra>",
            textfont=dict(color=TEXT), pathbar=dict(visible=True, textfont=dict(color=TEXT)),
        ))
        style(fig, 470, legend=False, margin=dict(l=4, r=4, t=28, b=4))
        chart("fn_desp", "Despesas por grupo", f"Despesas operacionais do período: {moeda_curta(dsp['valor'].sum())} · clique para abrir",
              fig, g.rename(columns={"grupo_despesa": "Grupo", "despesa": "Despesa", "valor": "Valor"}).round(2))

    footer()
