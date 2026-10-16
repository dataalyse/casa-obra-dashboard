"""PÁGINA 7 — Inteligência de Negócio: o que merece atenção agora e onde estão as oportunidades?"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from core import nav
from core.data import HOJE, LOJA_CURTA
from core.filters import itens
from core.metrics import abc, div, estoque_enriquecido, giro, mensal, meses_periodo, nps, receber
from core.theme import (
    CRIT, DIA_ABREV, INFO, LOJA_COR, MUTED, ORANGE, PLOTLY_CONFIG, POS, SCALE, SEQ, TEXT, YELLOW,
    icon, mes_ano, mes_ano_curto, moeda, moeda_curta, num, pct, rgba, style,
)
from core.ui import card_header, chart, footer, html_card
from views._common import TODOS, shell

PAGE = "intel"


def _alerta(chave: str, cor: str, ico: str, numero: str, frase: str, destino: str, rotulo: str):
    with st.container(key=f"kpi_al_{chave}"):
        st.markdown(
            f"""<div class="alert-card">
                <div class="kpi-top">{icon(ico, 20, cor)}<span class="kpi-label">{rotulo}</span>
                  {icon("arrow-right", 16, MUTED)}</div>
                <div class="alert-num" style="color:{cor}">{numero}</div>
                <div class="alert-txt">{frase}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.page_link(nav.PAGES[destino], label=rotulo)


def render():
    D, ctx = shell(PAGE, "Inteligência de Negócio", "O que merece atenção agora e onde estão as oportunidades?", TODOS)
    it = itens(D, ctx)

    # ------------------------------------------------------------ central de alertas
    e = estoque_enriquecido(D, ctx)
    n_risco = int(e["risco_ruptura"].sum())
    parado = e.loc[e["dias_sem_venda"] > 90, "valor_estoque_final"].sum()
    prod = abc(it)
    if not prod.empty:
        prod["margem"] = prod["lucro"] / prod["fat"]
        n_ruim = int(((prod["fat"] > prod["fat"].median()) & (prod["margem"] < prod["margem"].median())).sum())
    else:
        n_ruim = 0
    cr = receber(D, ctx)
    venc = cr[cr["status_titulo"] == "Vencido"]
    atraso = (HOJE - venc["data_vencimento"]).dt.days
    v_venc = venc["valor_titulo"].sum()
    p60 = div(venc.loc[atraso > 60, "valor_titulo"].sum(), v_venc)

    c = st.columns(4)
    with c[0]:
        _alerta("ruptura", CRIT, "alert", num(n_risco),
                f"🔴 {num(n_risco)} produtos podem acabar antes da próxima reposição", "estoque", "Risco de ruptura")
    with c[1]:
        _alerta("parado", YELLOW, "lock", moeda_curta(parado),
                f"🟡 {moeda_curta(parado)} imobilizados em produtos sem venda há 90+ dias", "estoque", "Capital parado")
    with c[2]:
        _alerta("margem", ORANGE, "trending-down", num(n_ruim),
                f"🟠 {num(n_ruim)} produtos vendem muito e lucram pouco (quadrante de baixa margem)", "rentab",
                "Vendem muito, lucram pouco")
    with c[3]:
        _alerta("inad", CRIT, "wallet", moeda_curta(v_venc),
                f"🔴 {moeda_curta(v_venc)} vencidos, sendo {pct(p60)} há mais de 60 dias", "finan", "Inadimplência")

    if it.empty:
        chart("in_vazio", "Sem dados", "", None)
        footer()
        return

    # ------------------------------------------------------------ 7.1 calendário
    dia = it.groupby("data")["valor_liquido"].sum()
    dias = pd.date_range(ctx.ini, ctx.fim, freq="D")
    dia = dia.reindex(dias)
    anos = sorted(set(dias.year))
    fig = make_subplots(rows=len(anos), cols=1, vertical_spacing=0.12 if len(anos) > 1 else 0.0,
                        subplot_titles=[str(a) for a in anos])
    zmax = np.nanpercentile(dia.values, 98) if dia.notna().any() else 1
    for i, ano in enumerate(anos, 1):
        d = dia[dia.index.year == ano]
        jan1 = pd.Timestamp(f"{ano}-01-01")
        sem = ((d.index - jan1).days + jan1.weekday()) // 7
        z = np.full((7, 54), np.nan)
        txt = np.full((7, 54), "", dtype=object)
        for dt, s, v in zip(d.index, sem, d.values):
            z[dt.weekday(), s] = v
            txt[dt.weekday(), s] = f"{dt:%d/%m/%Y} ({DIA_ABREV[dt.weekday()]})<br>" + (moeda(v) if v == v else "sem vendas")
        ticks = [((pd.Timestamp(f"{ano}-{m:02d}-01") - jan1).days + jan1.weekday()) // 7 for m in range(1, 13)]
        fig.add_trace(go.Heatmap(z=z, x=list(range(54)), y=DIA_ABREV, colorscale=SCALE, zmin=0, zmax=zmax,
                                 xgap=2, ygap=2, showscale=(i == 1), text=txt,
                                 hovertemplate="%{text}<extra></extra>",
                                 colorbar=dict(thickness=10, len=0.8, tickprefix="R$ ", tickfont=dict(color=MUTED, size=10))),
                      row=i, col=1)
        fig.update_xaxes(tickvals=ticks, ticktext=["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out",
                                                   "nov", "dez"], row=i, col=1, showgrid=False, range=[-0.5, 53.5])
        fig.update_yaxes(autorange="reversed", showgrid=False, row=i, col=1, tickfont=dict(size=9))
    style(fig, 150 + 150 * len(anos), legend=False, margin=dict(l=8, r=8, t=30, b=8))
    fig.update_annotations(font=dict(color=TEXT, size=12, family="Space Grotesk"), x=0, xanchor="left")
    melhor = dia.idxmax() if dia.notna().any() else None
    chart("in_cal", "Sazonalidade", f"Faturamento diário · quanto mais amarelo, mais vendeu"
          + (f" · melhor dia: {melhor:%d/%m/%Y} ({moeda_curta(dia.max())})" if melhor is not None else ""),
          fig, pd.DataFrame({"Data": dia.index.strftime("%d/%m/%Y"), "Faturamento": dia.values.round(2)}))

    # ------------------------------------------------------------ 7.2 / 7.3
    a, b = st.columns([2, 1])
    with a:
        ms = meses_periodo(ctx)
        m = mensal(it, ms)["fat"]
        ult = ms[-1]
        futuros = pd.date_range(ult + pd.DateOffset(months=1), periods=3, freq="MS")
        mm3 = m.iloc[-3:].mean()
        base_aa = pd.date_range(end=ult - pd.DateOffset(years=1), periods=3, freq="MS")
        hist = mensal(itens(D, ctx, ini=base_aa[0], fim=futuros[-1] - pd.DateOffset(years=1) + pd.offsets.MonthEnd(0)),
                      pd.date_range(base_aa[0], futuros[-1] - pd.DateOffset(years=1), freq="MS"))["fat"]
        mm3_aa = hist.reindex(base_aa).mean()
        proj = []
        for f in futuros:
            v_aa = hist.get(f - pd.DateOffset(years=1), np.nan)
            idx = v_aa / mm3_aa if mm3_aa and v_aa == v_aa and v_aa > 0 else 1.0
            proj.append(mm3 * idx)
        xa = [mes_ano_curto(d) for d in ms]
        xp = [xa[-1]] + [mes_ano_curto(d) for d in futuros]
        yp = [m.iloc[-1]] + proj
        fig = go.Figure()
        fig.add_scatter(x=xp, y=[v * 1.1 for v in yp], mode="lines", line=dict(width=0), hoverinfo="skip",
                        showlegend=False)
        fig.add_scatter(x=xp, y=[v * 0.9 for v in yp], mode="lines", line=dict(width=0), fill="tonexty",
                        fillcolor=rgba(YELLOW, .12), name="Faixa ±10%", hoverinfo="skip")
        fig.add_scatter(x=xa, y=m.values, mode="lines+markers", name="Realizado",
                        line=dict(color=ORANGE, width=2.8, shape="spline"), marker=dict(size=6),
                        hovertemplate="<b>%{x}</b><br>Realizado: R$ %{y:,.2f}<extra></extra>")
        fig.add_scatter(x=xp, y=yp, mode="lines+markers", name="Projeção",
                        line=dict(color=YELLOW, width=2.4, dash="dash"), marker=dict(size=7, symbol="diamond"),
                        hovertemplate="<b>%{x}</b><br>Projeção: R$ %{y:,.2f}<extra></extra>")
        style(fig, 380)
        fig.update_yaxes(tickprefix="R$ ", rangemode="tozero")
        chart("in_proj", "Tendência e projeção",
              f"Próximos 3 meses = média dos últimos 3 meses × sazonalidade do ano anterior · total projetado "
              f"{moeda_curta(sum(proj))}", fig,
              pd.DataFrame({"Mês": xa + [mes_ano_curto(d) for d in futuros],
                            "Realizado": list(m.values.round(2)) + [None] * 3,
                            "Projeção": [None] * len(xa) + [round(p, 2) for p in proj]}))

    with b:
        src = itens(D, ctx, ignore=("loja",))
        ent = D["entregas"]
        ent = ent[(ent["data_prevista"] >= ctx.ini) & (ent["data_prevista"] <= ctx.fim) & (ent["status_entrega"] != "Em rota")]
        n = D["nps"]
        n = n[(n["data_resposta"] >= ctx.ini) & (n["data_resposta"] <= ctx.fim)]
        rows = []
        for lid, nome in LOJA_CURTA.items():
            s = src[src["id_loja"] == lid]
            if s.empty:
                continue
            fat = s["valor_liquido"].sum()
            el = ent[ent["id_loja"] == lid]
            rows.append({"Loja": nome, "Faturamento": fat, "Margem": s["lucro_bruto"].sum() / fat,
                         "Ticket": fat / s["id_venda"].nunique(), "NPS": nps(n[n["id_loja"] == lid]) or 0,
                         "Entregas no prazo": (el["status_entrega"] == "Entregue no prazo").mean() if len(el) else 0,
                         "Giro de estoque": giro(D, ctx, loja_ids=[lid]) or 0})
        rd = pd.DataFrame(rows).set_index("Loja")
        eixos = list(rd.columns)
        norm = rd.clip(lower=0) / rd.clip(lower=0).max().replace(0, np.nan) * 100
        fig = go.Figure()
        for loja, r in norm.iterrows():
            vals = list(r.fillna(0).values) + [r.fillna(0).values[0]]
            fig.add_scatterpolar(r=vals, theta=eixos + [eixos[0]], name=loja, fill="toself",
                                 line=dict(color=LOJA_COR[loja], width=2), fillcolor=rgba(LOJA_COR[loja], .15),
                                 hovertemplate=f"<b>{loja}</b><br>%{{theta}}: %{{r:.0f}} / 100<extra></extra>")
        style(fig, 380)
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                     radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor="rgba(255,255,255,0.08)"),
                                     angularaxis=dict(gridcolor="rgba(255,255,255,0.08)", tickfont=dict(size=10, color=MUTED))),
                          legend=dict(orientation="h", y=-0.08, yanchor="top", x=0.5, xanchor="center"))
        tab = rd.copy()
        tab["Margem"] = (tab["Margem"] * 100).round(1)
        tab["Entregas no prazo"] = (tab["Entregas no prazo"] * 100).round(1)
        chart("in_radar", "Comparativo entre lojas", "Cada eixo de 0 a 100 (100 = melhor loja naquele indicador)",
              fig, tab.round(2).reset_index())

    # ------------------------------------------------------------ 7.4 / 7.5
    a, b = st.columns(2)
    with a:
        piv = it.groupby(["ano_mes", "canal"], observed=True)["valor_liquido"].sum().unstack().reindex(ms).fillna(0)
        ordem = piv.sum().sort_values(ascending=False).index
        fig = go.Figure()
        for i, canal in enumerate(ordem):
            fig.add_scatter(x=xa, y=piv[canal], name=canal, mode="lines", stackgroup="one", groupnorm="percent",
                            line=dict(width=0.5, color=SEQ[i % len(SEQ)]),
                            hovertemplate=f"{canal}: %{{y:.1f}}%<extra></extra>")
        style(fig, 360)
        fig.update_layout(hovermode="x unified")
        fig.update_yaxes(ticksuffix="%", range=[0, 100])
        share = piv.div(piv.sum(axis=1).replace(0, np.nan), axis=0)
        dig = [c_ for c_ in piv.columns if c_ in ("WhatsApp", "E-commerce")]
        d0, d1 = share[dig].iloc[:3].sum(axis=1).mean(), share[dig].iloc[-3:].sum(axis=1).mean()
        chart("in_canais", "Crescimento dos canais digitais",
              f"Participação de cada canal mês a mês · WhatsApp + e-commerce: {pct(d0)} → {pct(d1)}",
              fig, (share * 100).round(1).reset_index(drop=True).assign(Mês=xa))

    with b:
        ent2 = D["entregas"]
        ent2 = ent2[(ent2["data_prevista"] >= ctx.ini) & (ent2["data_prevista"] <= ctx.fim)]
        if ctx.loja_ids:
            ent2 = ent2[ent2["id_loja"].isin(ctx.loja_ids)]
        ent2 = ent2.assign(mes=ent2["data_prevista"].dt.to_period("M").dt.to_timestamp())
        conc = ent2[ent2["status_entrega"] != "Em rota"]
        g = ent2.groupby("mes").size().reindex(ms, fill_value=0)
        ok = conc.groupby("mes")["status_entrega"].apply(lambda s: (s == "Entregue no prazo").mean()).reindex(ms)
        fig = go.Figure()
        fig.add_bar(x=xa, y=g.values, name="Entregas", marker=dict(color=INFO, cornerradius=5),
                    hovertemplate="Entregas: %{y:,.0f}<extra></extra>")
        fig.add_scatter(x=xa, y=ok.values * 100, name="% no prazo", yaxis="y2", mode="lines+markers",
                        line=dict(color=YELLOW, width=2.5, shape="spline"), marker=dict(size=6),
                        hovertemplate="No prazo: %{y:.1f}%<extra></extra>")
        style(fig, 300)
        fig.update_layout(hovermode="x unified",
                          yaxis2=dict(overlaying="y", side="right", showgrid=False, ticksuffix="%", range=[0, 105],
                                      tickfont=dict(color=MUTED, size=11)))
        custo, frete = ent2["custo_entrega"].sum(), ent2["frete_cobrado"].sum()
        cob = div(frete, custo)
        with st.container(key="card_in_log"):
            card_header("in_log", "Desempenho logístico",
                        f"{num(len(ent2))} entregas · {pct((conc['status_entrega'] == 'Entregue no prazo').mean() if len(conc) else None)} no prazo",
                        pd.DataFrame({"Mês": xa, "Entregas": g.values, "% no prazo": (ok.values * 100).round(1)}))
            st.plotly_chart(fig, key="pl_in_log", config=PLOTLY_CONFIG, use_container_width=True)
            st.markdown(
                f"""<div style="display:flex;gap:12px;flex-wrap:wrap;margin:2px 0 8px 0">
                  <div style="flex:1;min-width:140px;background:var(--surface-2);border-radius:12px;padding:10px 14px">
                    <div class="kpi-label">Custo de entrega</div>
                    <div style="font-family:'Space Grotesk';font-size:22px;font-weight:700;color:{CRIT}">{moeda_curta(custo)}</div></div>
                  <div style="flex:1;min-width:140px;background:var(--surface-2);border-radius:12px;padding:10px 14px">
                    <div class="kpi-label">Frete cobrado</div>
                    <div style="font-family:'Space Grotesk';font-size:22px;font-weight:700;color:{POS}">{moeda_curta(frete)}</div></div>
                  <div style="flex:1;min-width:140px;background:var(--surface-2);border-radius:12px;padding:10px 14px">
                    <div class="kpi-label">Frete cobre o custo</div>
                    <div style="font-family:'Space Grotesk';font-size:22px;font-weight:700;color:{YELLOW}">{pct(cob, 0)}</div></div>
                </div>""",
                unsafe_allow_html=True,
            )

    # ------------------------------------------------------------ 7.6 insights
    ins = []
    mm = mensal(it, ms)
    if mm["fat"].max() > 0:
        bm = mm["fat"].idxmax()
        ins.append(("trending", f"O melhor mês do período foi <b>{mes_ano(bm)}</b>, com <b>{moeda_curta(mm['fat'].max())}</b> "
                                f"de faturamento."))
    cg = it.groupby("categoria", observed=True).agg(f=("valor_liquido", "sum"), l=("lucro_bruto", "sum"))
    cg = cg[cg["f"] > 0]
    if not cg.empty:
        cg["m"] = cg["l"] / cg["f"]
        ins.append(("percent", f"A categoria <b>{cg['m'].idxmin()}</b> tem a menor margem (<b>{pct(cg['m'].min())}</b>); "
                               f"a de maior margem é <b>{cg['m'].idxmax()}</b> ({pct(cg['m'].max())})."))
    vd = it.drop_duplicates("id_venda")
    sab = vd[vd["dow"] == 5]
    if len(sab):
        ins.append(("clock", f"No sábado, <b>{pct((sab['hora_int'] < 12).mean())}</b> das vendas acontecem pela manhã "
                             f"(antes das 12h): é a hora de reforçar o balcão."))
    res = it[it["loja"] == "Resende"]
    if not res.empty:
        rm = mensal(res, pd.date_range("2025-06-01", HOJE.to_period("M").to_timestamp(), freq="MS"))["fat"]
        # desde a inauguração (02/06/2025) até o fim do período, com os mesmos filtros (exceto período)
        res_all = itens(D, ctx, ini=pd.Timestamp("2025-06-01"), fim=ctx.fim)
        rm = mensal(res_all[res_all["loja"] == "Resende"],
                    pd.date_range("2025-06-01", ctx.mes_ref, freq="MS"))["fat"] if ctx.fim >= pd.Timestamp("2025-07-01") else rm.iloc[:0]
        rm = rm[rm > 0]
        if len(rm) >= 2:
            ins.append(("activity", f"A loja de <b>Resende</b> cresceu <b>{pct(rm.iloc[-1] / rm.iloc[0] - 1, 0)}</b> desde a "
                                    f"inauguração ({mes_ano(rm.index[0])} → {mes_ano(rm.index[-1])})."))
    if dig and d0 == d0 and d1 == d1:
        ins.append(("phone", f"Os canais digitais (WhatsApp + e-commerce) foram de <b>{pct(d0)}</b> para <b>{pct(d1)}</b> "
                             f"do faturamento entre o início e o fim do período."))
    pix = div(it.loc[it["forma_pagamento"] == "PIX", "valor_liquido"].sum(), it["valor_liquido"].sum())
    if pix:
        ins.append(("banknote", f"O <b>PIX</b> já responde por <b>{pct(pix)}</b> do faturamento, sem taxa de cartão."))
    body = "".join(f'<div class="insight">{icon(ic, 18)}<div>{t}</div></div>' for ic, t in ins)
    html_card("in_insights", "Insights automáticos", "Frases geradas a partir dos dados filtrados", body,
              pd.DataFrame({"Insight": [pd.Series([t]).str.replace(r"<[^>]+>", "", regex=True)[0] for _, t in ins]}))

    footer()
