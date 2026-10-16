"""PÁGINA 6 — Clientes: quem compra, com que frequência e quem está sumindo?"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.filters import cross_callback, itens, sel_key
from core.metrics import div, meses_ate, meses_periodo, nps, nps_f, var
from core.theme import (
    CRIT, INFO, MUTED, ORANGE, POS, SCALE, SEQ, SURFACE, SURFACE2, TEXT, YELLOW,
    data_br, icon, mes_ano_curto, moeda, moeda_curta, num, pct, rgba, style,
)
from core.ui import chart, footer, hbar, html_card, kpi, kpi_row, pill, sparkline, table
from views._common import TODOS, shell

PAGE = "clientes"
REC = ["0–30 dias", "31–60 dias", "61–90 dias", "91–180 dias", "180+ dias"]
REC_BINS = [-1, 30, 60, 90, 180, 10**6]
FREQ = ["1 compra", "2–3", "4–6", "7–10", "11+"]
FREQ_BINS = [0, 1, 3, 6, 10, 10**6]


def _extra():
    from core.data import load
    D = load()
    c = st.columns(3)
    with c[0]:
        st.multiselect("Tipo de pessoa", ["PF", "PJ"], key="p_tp", placeholder="PF e PJ")
    with c[1]:
        st.multiselect("Cidade", sorted(D["clientes"]["cidade"].dropna().unique()), key="p_cid", placeholder="Todas")
    with c[2]:
        st.multiselect("Faixa de recência", REC, key="p_rec", placeholder="Todas")


def _clientes(it: pd.DataFrame) -> pd.DataFrame:
    it = it[it["id_cliente"] != "CL00000"]
    if st.session_state.get("p_tp"):
        it = it[it["tipo_pessoa"].isin(st.session_state["p_tp"])]
    if st.session_state.get("p_cid"):
        it = it[it["cidade"].isin(st.session_state["p_cid"])]
    return it


def render():
    D, ctx = shell(PAGE, "Clientes", "Quem compra, com que frequência e quem está sumindo?", TODOS, _extra)
    ref = ctx.data_ref
    cli = D["clientes"].set_index("id_cliente")

    it = _clientes(itens(D, ctx))
    itp = _clientes(itens(D, ctx, ini=ctx.pini, fim=ctx.pfim))
    # histórico até a data de referência (para recência, primeira compra e inativos)
    hist = _clientes(itens(D, ctx, ini=pd.Timestamp("2000-01-01"), fim=ref, cross=False))
    ult = hist.groupby("id_cliente")["data"].max()
    pri = hist.groupby("id_cliente")["data"].min()
    rec_dias = (ref - ult).dt.days

    if st.session_state.get("p_rec"):
        faixa = pd.cut(rec_dias, REC_BINS, labels=REC)
        keep = faixa[faixa.isin(st.session_state["p_rec"])].index
        it = it[it["id_cliente"].isin(keep)]
        itp = itp[itp["id_cliente"].isin(keep)]
        hist = hist[hist["id_cliente"].isin(keep)]
        ult, pri, rec_dias = ult[ult.index.isin(keep)], pri[pri.index.isin(keep)], rec_dias[rec_dias.index.isin(keep)]

    def stats(df, ini, fim):
        g = df.groupby("id_cliente").agg(fat=("valor_liquido", "sum"), n=("id_venda", "nunique"))
        ativos = len(g)
        novos = int(((pri >= ini) & (pri <= fim)).sum()) if not df.empty else 0
        rec = div((g["n"] >= 2).sum(), ativos)
        tk = div(g["fat"].sum(), ativos)
        return g, ativos, novos, rec, tk

    g, ativos, novos, recor, tkc = stats(it, ctx.ini, ctx.fim)
    gp, ativosp, novosp, recorp, tkcp = stats(itp, ctx.pini, ctx.pfim)
    inativos = int((rec_dias > 90).sum())
    nf = nps_f(D, ctx)
    if st.session_state.get("p_tp"):
        nf = nf[nf["tipo_pessoa"].isin(st.session_state["p_tp"])]
    if st.session_state.get("p_cid"):
        nf = nf[nf["cidade"].isin(st.session_state["p_cid"])]
    nps_v = nps(nf)
    nps_p = nps(nps_f(D, ctx, ctx.pini, ctx.pfim))

    # sparkline de clientes ativos por mês
    ms = meses_ate(ctx.fim)
    it12 = _clientes(itens(D, ctx, ini=ms[0], fim=ctx.fim))
    sp_ativos = it12.groupby("ano_mes")["id_cliente"].nunique().reindex(ms, fill_value=0)

    c = kpi_row()
    with c[0]:
        kpi("ativos", "Clientes ativos", num(ativos), "users", delta=var(ativos, ativosp), comp=ctx.comp,
            spark=sp_ativos.values, tom="hl", info="Clientes identificados com pelo menos uma compra no período (sem o balcão anônimo).")
    with c[1]:
        kpi("novos", "Novos clientes", num(novos), "user-plus", delta=var(novos, novosp), comp=ctx.comp,
            info="Clientes cuja primeira compra aconteceu dentro do período.")
    with c[2]:
        kpi("recor", "Recorrentes", pct(recor), "repeat",
            delta=(recor - recorp) if recor is not None and recorp is not None else None, pp=True, comp=ctx.comp,
            info="% dos clientes ativos que compraram 2 vezes ou mais no período.")
    with c[3]:
        kpi("tkc", "Ticket por cliente", moeda(tkc, 0), "receipt", delta=var(tkc, tkcp), comp=ctx.comp,
            info="Faturamento dos clientes identificados ÷ clientes ativos.")
    with c[4]:
        kpi("inativos", "Inativos (+90 dias)", num(inativos), "user-x", tom="warn",
            nota=f"de {num(len(ult))} clientes com histórico",
            info=f"Clientes cuja última compra foi há mais de 90 dias (referência {data_br(ref)}).")
    with c[5]:
        kpi("nps", "NPS", num(nps_v), "smile", delta=(nps_v - nps_p) if nps_v is not None and nps_p is not None else None,
            pp=False, comp=ctx.comp, tom="hl" if (nps_v or 0) > 50 else "",
            info="% promotores (notas 9–10) − % detratores (0–6). Vai de −100 a +100.")

    if it.empty:
        chart("cl_vazio", "Sem dados", "", None)
        footer()
        return

    # ------------------------------------------------------------ 6.1 / 6.2 / 6.3
    c1, c2, c3 = st.columns(3)
    with c1:
        s = it.groupby("segmento", observed=True)["valor_liquido"].sum().sort_values(ascending=False)
        s = s[s > 0]
        tot = s.sum()
        fig = go.Figure(go.Pie(labels=list(s.index), values=s.values, hole=0.64, sort=False,
                               marker=dict(colors=SEQ, line=dict(color=SURFACE, width=3)), textinfo="percent",
                               textfont=dict(color=TEXT, size=10),
                               hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"))
        fig.add_annotation(text=f"<b>{moeda_curta(tot)}</b><br><span style='font-size:11px;color:{MUTED}'>TOTAL</span>",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=16, color=TEXT, family="Space Grotesk"))
        style(fig, 360)
        fig.update_layout(legend=dict(orientation="h", y=-0.03, yanchor="top", x=0.5, xanchor="center", font=dict(size=10)))
        chart("cl_seg", "Faturamento por segmento", "Quem são os clientes que mais compram", fig,
              pd.DataFrame({"Segmento": s.index, "Faturamento": s.values.round(2)}))

    with c2:
        mp = meses_periodo(ctx)
        t = it[it["tipo_cliente_venda"].isin(["Novo", "Recorrente"])]
        piv = t.groupby(["ano_mes", "tipo_cliente_venda"], observed=True)["id_cliente"].nunique().unstack().reindex(
            index=mp, columns=["Novo", "Recorrente"]).fillna(0)
        x = [mes_ano_curto(m) for m in mp]
        fig = go.Figure()
        fig.add_bar(x=x, y=piv["Recorrente"], name="Recorrentes", marker=dict(color=ORANGE),
                    hovertemplate="Recorrentes: %{y:,.0f}<extra></extra>")
        fig.add_bar(x=x, y=piv["Novo"], name="Novos", marker=dict(color=YELLOW),
                    hovertemplate="Novos: %{y:,.0f}<extra></extra>")
        style(fig, 360)
        fig.update_layout(barmode="stack", hovermode="x unified", bargap=0.25)
        chart("cl_novos", "Novos × recorrentes", "Clientes distintos que compraram em cada mês", fig,
              piv.reset_index(drop=True).assign(Mês=x)[["Mês", "Novo", "Recorrente"]].astype({"Novo": int, "Recorrente": int}))

    with c3:
        v = nps_v if nps_v is not None else 0
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=v,
            number=dict(font=dict(family="Space Grotesk", size=42, color=TEXT), valueformat=".0f"),
            gauge=dict(axis=dict(range=[-100, 100], tickfont=dict(color=MUTED, size=10), tickvals=[-100, -50, 0, 50, 100]),
                       bar=dict(color=TEXT, thickness=0.18), bgcolor=SURFACE, borderwidth=0,
                       steps=[dict(range=[-100, 0], color=rgba(CRIT, .55)), dict(range=[0, 50], color=rgba(YELLOW, .5)),
                              dict(range=[50, 100], color=rgba(POS, .6))]),
            domain=dict(x=[0, 1], y=[0.32, 1]),
        ))
        cnt = nf["classificacao_nps"].value_counts(normalize=True).reindex(["Promotor", "Neutro", "Detrator"]).fillna(0)
        for nome, cor in [("Promotor", POS), ("Neutro", YELLOW), ("Detrator", CRIT)]:
            fig.add_bar(x=[cnt[nome] * 100], y=[""], orientation="h", name=f"{nome}es".replace("ores", "ores") if False else
                        {"Promotor": "Promotores", "Neutro": "Neutros", "Detrator": "Detratores"}[nome],
                        marker=dict(color=cor), text=[pct(cnt[nome], 0)], textposition="inside",
                        textfont=dict(color="#0A1626", size=11), xaxis="x", yaxis="y",
                        hovertemplate=f"{nome}: %{{x:.1f}}%<extra></extra>")
        style(fig, 360)
        fig.update_layout(barmode="stack",
                          xaxis=dict(domain=[0.05, 0.95], range=[0, 100], showticklabels=False, showgrid=False),
                          yaxis=dict(domain=[0.05, 0.17], showticklabels=False, showgrid=False),
                          legend=dict(orientation="h", y=0.0, yanchor="top", x=0.5, xanchor="center"))
        chart("cl_nps", "NPS", f"{num(len(nf))} respostas · vermelho < 0 · amarelo 0–50 · verde > 50", fig,
              pd.DataFrame({"Classificação": cnt.index, "%": (cnt.values * 100).round(1)}))

    # ------------------------------------------------------------ 6.4 / 6.5
    a, b = st.columns(2)
    with a:
        rfm = pd.DataFrame({"n": g["n"]}).join(rec_dias.rename("rec"), how="left")
        rfm["fr"] = pd.cut(rfm["n"], FREQ_BINS, labels=FREQ)
        rfm["rc"] = pd.cut(rfm["rec"], REC_BINS, labels=REC)
        mat = rfm.groupby(["rc", "fr"], observed=False).size().unstack().reindex(index=REC, columns=FREQ).fillna(0)

        def rotulo(ri, fi):
            if ri == 0 and fi >= 3:
                return "Campeões"
            if ri <= 1 and fi >= 2:
                return "Fiéis"
            if ri <= 1 and fi == 0:
                return "Novos"
            if ri >= 3 and fi >= 2:
                return "Em risco"
            if ri >= 3:
                return "Hibernando"
            return ""

        txt = [[f"<b>{rotulo(i, j)}</b><br>{int(mat.iat[i, j])}" if rotulo(i, j) else f"{int(mat.iat[i, j])}"
                for j in range(len(FREQ))] for i in range(len(REC))]
        fig = go.Figure(go.Heatmap(z=mat.values, x=FREQ, y=REC, colorscale=SCALE, xgap=3, ygap=3, showscale=False,
                                   text=txt, texttemplate="%{text}", textfont=dict(size=11, color=TEXT),
                                   hovertemplate="Recência %{y} · frequência %{x}<br><b>%{z:,.0f} clientes</b><extra></extra>"))
        style(fig, 380, legend=False)
        fig.update_xaxes(title_text="Frequência (compras no período)", side="bottom")
        fig.update_yaxes(title_text="Recência (dias desde a última compra)", autorange="reversed", showgrid=False)
        chart("cl_rfm", "Segmentação RFM", "Clientes por recência × frequência · campeões no canto superior direito",
              fig, mat.astype(int).reset_index(names="Recência"))

    with b:
        src = _clientes(itens(D, ctx, ignore=("cidade",)))
        cg = src.groupby("cidade", observed=True).agg(fat=("valor_liquido", "sum"), n=("id_cliente", "nunique"))
        cg = cg[cg["fat"] > 0].sort_values("fat", ascending=False)
        sel = ctx.cross.get("cidade")
        cores = [ORANGE if (sel is None or k == sel) else rgba(ORANGE, .3) for k in cg.index]
        fig = hbar(cg.index, cg["fat"], [f"{moeda_curta(f)} · {num(n)} clientes" for f, n in zip(cg["fat"], cg["n"])],
                   cores, height=380, hover="<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>")
        k = sel_key(PAGE, "cidade")
        chart("cl_cid", "Clientes por cidade", "Faturamento e nº de clientes · clique para filtrar a página", fig,
              cg.reset_index().rename(columns={"cidade": "Cidade", "fat": "Faturamento", "n": "Clientes"}).round(2),
              on_select=cross_callback(PAGE, "cidade", k, lambda p: p.get("y")), sel_key=k)

    # ------------------------------------------------------------ 6.6 / 6.7
    a, b = st.columns([2, 1])
    with a:
        top = g.sort_values("fat", ascending=False).head(15)
        mens = it12[it12["id_cliente"].isin(top.index)].groupby(["id_cliente", "ano_mes"])["id_venda"].nunique()
        linhas, dados = [], []
        for idc, r in top.iterrows():
            rd = rec_dias.get(idc)
            tom = "pos" if rd is not None and rd <= 30 else ("warn" if rd is not None and rd <= 90 else "crit")
            serie = mens.get(idc, pd.Series(dtype=float)).reindex(ms, fill_value=0) if idc in mens.index.get_level_values(0) \
                else pd.Series(0, index=ms)
            nome = cli.at[idc, "cliente"] if idc in cli.index else idc
            linhas.append({
                "Cliente": f"<b>{nome}</b>", "Segmento": cli.at[idc, "segmento"], "Cidade": cli.at[idc, "cidade"],
                "Faturamento": moeda(r["fat"], 0), "Compras": num(r["n"]), "Ticket": moeda(r["fat"] / r["n"], 0),
                "Última compra": data_br(ult.get(idc)), "Recência": pill(f"{num(rd)} d", tom),
                "Compras/mês (12m)": f'<div style="width:110px">{sparkline(serie.values)}</div>',
            })
            dados.append({"Cliente": nome, "Segmento": cli.at[idc, "segmento"], "Cidade": cli.at[idc, "cidade"],
                          "Faturamento": round(r["fat"], 2), "Compras": int(r["n"]),
                          "Ticket médio": round(r["fat"] / r["n"], 2), "Última compra": data_br(ult.get(idc)),
                          "Recência (dias)": rd})
        html_card("cl_top", "Top 15 clientes", "Maiores compradores do período",
                  table(pd.DataFrame(linhas), {"Faturamento": "right", "Compras": "right", "Ticket": "right",
                                               "Recência": "center"}, max_height=560),
                  pd.DataFrame(dados))

    with b:
        hist_fat = hist.groupby("id_cliente")["valor_liquido"].sum()
        risco = pd.DataFrame({"fat": hist_fat, "rec": rec_dias}).dropna()
        risco = risco[risco["rec"] > 60].sort_values("fat", ascending=False).head(10)
        cards = []
        for idc, r in risco.iterrows():
            nome = cli.at[idc, "cliente"] if idc in cli.index else idc
            seg = cli.at[idc, "segmento"] if idc in cli.index else ""
            cards.append(
                f'<div class="risk"><div style="width:34px;height:34px;border-radius:50%;background:{rgba(CRIT, .15)};'
                f'display:flex;align-items:center;justify-content:center">{icon("user-x", 16, CRIT)}</div>'
                f'<div><div class="risk-name">{nome}</div><div class="risk-meta">{seg} · {moeda_curta(r["fat"])} no histórico · '
                f'<span style="color:{CRIT}">{num(r["rec"])} dias sem comprar</span></div></div>'
                f'<span class="risk-btn">{icon("phone", 12, ORANGE)} Contatar</span></div>'
            )
        html_card("cl_risco", "Clientes em risco", "Bons clientes há mais de 60 dias sem comprar",
                  "".join(cards) or '<div class="empty">Nenhum cliente em risco</div>',
                  risco.reset_index().rename(columns={"index": "Cliente", "id_cliente": "Cliente", "fat": "Faturamento histórico",
                                                      "rec": "Dias sem comprar"}).round(2))

    footer()
