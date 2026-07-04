"""
Casa&Obra — Painel de Vendas
Renderização das páginas do painel: Início, Análise de Vendas, Vendas por
Vendedor e Vendas por Produtos.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (
    COLORS, CATEGORY_PALETTE, PAGINAS,
    fmt_moeda, fmt_num, fmt_pct, plotly_layout_defaults, variacao_pct,
)


# ----------------------------------------------------------------------------
# Componentes reutilizáveis
# ----------------------------------------------------------------------------
def nav_bar(atual: str, incluir_inicio: bool = True):
    """Botões de navegação entre as páginas (substituem a barra lateral).

    Importante: NÃO chama st.rerun() aqui. Isso é proposital — esta função
    roda antes de filtros_bar() dentro de cada página, e um rerun imediato
    interromperia o script antes dos widgets de filtro (mais abaixo na
    mesma página) serem instanciados nesta execução. Como o Streamlit
    descarta o estado de um widget que não é registrado durante uma
    execução completa, isso apagaria os filtros ao trocar de página. Por
    isso o rerun é adiado para o fim do script, em app.py, depois que a
    página atual (com seus filtros) já renderizou por inteiro.
    """
    paginas = PAGINAS if incluir_inicio else [p for p in PAGINAS if p[1] != "Início"]
    cols = st.columns(len(paginas))
    for col, (label, chave) in zip(cols, paginas):
        with col:
            tipo = "primary" if chave == atual else "secondary"
            if st.button(label, key=f"nav_{chave}", width="stretch", type=tipo) and chave != atual:
                st.session_state["pagina"] = chave
                st.session_state["_trocar_pagina"] = True
    st.markdown("<br>", unsafe_allow_html=True)


def filtros_bar(df: pd.DataFrame):
    """Controles de filtro (período, categoria, vendedor, forma de pagamento),
    exibidos logo abaixo dos cartões de indicadores de cada página."""
    data_min, data_max = df["Data_Venda"].min().date(), df["Data_Venda"].max().date()
    with st.container(border=True):
        st.markdown(
            f"<p style='font-size:12px; font-weight:700; color:{COLORS['muted']}; "
            "text-transform:uppercase; letter-spacing:0.6px; margin-bottom:8px;'>Filtros</p>",
            unsafe_allow_html=True,
        )
        c1, c2, c3, c4 = st.columns([1.3, 1, 1, 1])
        with c1:
            st.date_input(
                "Período", value=st.session_state.get("flt_periodo", (data_min, data_max)),
                min_value=data_min, max_value=data_max, key="flt_periodo",
            )
        with c2:
            st.multiselect("Categoria", sorted(df["Categoria"].unique()), key="flt_categorias")
        with c3:
            st.multiselect("Vendedor", sorted(df["Vendedor"].unique()), key="flt_vendedores")
        with c4:
            st.multiselect("Forma de Pagamento", sorted(df["Forma_Pagamento"].unique()), key="flt_formas")
    st.markdown("<br>", unsafe_allow_html=True)


def page_header(titulo: str, subtitulo: str):
    st.markdown(
        f"""
        <div class="page-header">
            <div>
                <p class="page-title">{titulo}</p>
                <p class="page-subtitle">{subtitulo}</p>
            </div>
        </div>
        <div class="ruler-divider"></div>
        """,
        unsafe_allow_html=True,
    )


def _delta_html(delta_pct):
    if delta_pct is None:
        return ""
    seta = "▲" if delta_pct >= 0 else "▼"
    classe = "kpi-delta-up" if delta_pct >= 0 else "kpi-delta-down"
    valor = f"{abs(delta_pct):.1f}".replace(".", ",")
    return f'<span class="kpi-delta {classe}">{seta} {valor}%</span>'


def kpi_card(label: str, value: str, note: str = "", delta_pct: float | None = None):
    delta_html = _delta_html(delta_pct)
    rodape = ""
    if delta_html or note:
        rodape = f'<div class="kpi-row">{delta_html}' + (
            f'<span class="kpi-note" style="margin:0;">{note}</span>' if note else ""
        ) + "</div>"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {rodape}
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_card_open(title: str):
    st.markdown(
        f"""<div class="chart-card"><div class="chart-card-title">{title}</div>""",
        unsafe_allow_html=True,
    )


def chart_card_close():
    st.markdown("</div>", unsafe_allow_html=True)


_CORES_ESCURAS = {COLORS["slate"], COLORS["orange_dark"], COLORS["navy"]}


def _cor_texto_para(cores):
    """Escolhe texto claro sobre fundos escuros e texto escuro sobre fundos
    claros, para os rótulos de valor ficarem legíveis dentro das barras."""
    return [COLORS["text"] if c in _CORES_ESCURAS else COLORS["navy"] for c in cores]


def _donut(labels, values, height):
    total = sum(values)
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.68,
        marker=dict(colors=CATEGORY_PALETTE, line=dict(color=COLORS["surface"], width=3)),
        textinfo="percent", textfont=dict(size=11, color=COLORS["text"]),
        hovertemplate="%{label}<br>R$ %{value:,.2f}<extra></extra>",
        sort=False,
    ))
    fig = plotly_layout_defaults(fig, height=height, legend=True)
    fig.update_layout(
        legend=dict(orientation="v", x=1, y=0.5, font=dict(size=10.5, color=COLORS["muted"])),
        annotations=[dict(
            text=f"<b>{fmt_moeda(total)}</b><br><span style='font-size:10px;color:{COLORS['muted']}'>TOTAL</span>",
            x=0.5, y=0.5, showarrow=False, font=dict(size=14, color=COLORS["text"], family="IBM Plex Mono"),
        )],
    )
    return fig


# ----------------------------------------------------------------------------
# PÁGINA 0 — INÍCIO
# ----------------------------------------------------------------------------
def view_inicio(df: pd.DataFrame, df_prev: pd.DataFrame, saudacao: str, data_extenso: str):
    st.markdown(
        f"""
        <div class="hero-card">
            <span class="hero-tag">Casa&amp;Obra</span>
            <p class="hero-greeting">{saudacao}! Aqui está o resumo do seu negócio.</p>
            <p class="hero-date">{data_extenso}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_bar("Início", incluir_inicio=False)

    if df.empty:
        st.warning("Nenhum dado para os filtros selecionados.")
        return

    total_vendas = df["Valor_Total"].sum()
    n_pedidos = len(df)
    ticket_medio = df["Valor_Total"].mean()
    margem_total = df["Margem"].sum()

    total_prev = df_prev["Valor_Total"].sum() if not df_prev.empty else None
    pedidos_prev = len(df_prev) if not df_prev.empty else None
    ticket_prev = df_prev["Valor_Total"].mean() if not df_prev.empty else None
    margem_prev = df_prev["Margem"].sum() if not df_prev.empty else None

    d_vendas = variacao_pct(total_vendas, total_prev)
    d_pedidos = variacao_pct(n_pedidos, pedidos_prev)
    d_ticket = variacao_pct(ticket_medio, ticket_prev)
    d_margem = variacao_pct(margem_total, margem_prev)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total de Vendas", fmt_moeda(total_vendas),
                  "vs. período anterior" if d_vendas is not None else "", d_vendas)
    with c2:
        kpi_card("Pedidos", fmt_num(n_pedidos),
                  "vs. período anterior" if d_pedidos is not None else "", d_pedidos)
    with c3:
        kpi_card("Ticket Médio", fmt_moeda(ticket_medio),
                  "vs. período anterior" if d_ticket is not None else "", d_ticket)
    with c4:
        kpi_card("Margem Estimada", fmt_moeda(margem_total),
                  "vs. período anterior" if d_margem is not None else "", d_margem)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 1])
    with col_a:
        chart_card_open("Evolução de Vendas no Período")
        serie = df.groupby("AnoMes", as_index=False)["Valor_Total"].sum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=serie["AnoMes"], y=serie["Valor_Total"],
            mode="lines", fill="tozeroy", line_shape="spline",
            line=dict(color=COLORS["orange"], width=3),
            fillcolor="rgba(232,117,46,0.22)",
            hovertemplate="%{x|%b/%Y}<br>R$ %{y:,.2f}<extra></extra>",
            name="Vendas",
        ))
        fig = plotly_layout_defaults(fig, height=320, legend=False)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    with col_b:
        chart_card_open("Mix por Categoria")
        cat = df.groupby("Categoria", as_index=False)["Valor_Total"].sum().sort_values(
            "Valor_Total", ascending=False
        )
        fig = _donut(cat["Categoria"], cat["Valor_Total"], height=320)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    resumo_vend = df.groupby("Vendedor", as_index=False)["Valor_Total"].sum().sort_values(
        "Valor_Total", ascending=False
    )
    top_vendedor = resumo_vend.iloc[0]
    prod = df.groupby("Nome_Produto", as_index=False)["Valor_Total"].sum().sort_values(
        "Valor_Total", ascending=False
    )
    top_produto = prod.iloc[0]
    cat_lider = df.groupby("Categoria")["Valor_Total"].sum().idxmax()

    h1, h2, h3 = st.columns(3)
    with h1:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div class="highlight-kicker">Vendedor Destaque</div>
                <p class="highlight-title">{top_vendedor['Vendedor']}</p>
                <span class="highlight-sub">{fmt_moeda(top_vendedor['Valor_Total'])}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with h2:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div class="highlight-kicker">Produto Mais Vendido</div>
                <p class="highlight-title">{top_produto['Nome_Produto']}</p>
                <span class="highlight-sub">{fmt_moeda(top_produto['Valor_Total'])}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with h3:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div class="highlight-kicker">Categoria Líder</div>
                <p class="highlight-title">{cat_lider}</p>
                <span class="highlight-sub">&nbsp;</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ----------------------------------------------------------------------------
# PÁGINA 1 — ANÁLISE DE VENDAS
# ----------------------------------------------------------------------------
def view_analise(df: pd.DataFrame, df_prev: pd.DataFrame | None = None, df_full: pd.DataFrame | None = None):
    nav_bar("Análise de Vendas")
    page_header(
        "Análise de Vendas",
        "Visão geral do desempenho comercial da Casa&Obra no período selecionado.",
    )

    if df.empty:
        st.warning("Nenhum dado para os filtros selecionados.")
        return

    total_vendas = df["Valor_Total"].sum()
    n_pedidos = len(df)
    ticket_medio = df["Valor_Total"].mean()
    total_desconto = df["Desconto"].sum()
    margem_total = df["Margem"].sum()

    df_prev = df_prev if df_prev is not None else pd.DataFrame(columns=df.columns)
    total_prev = df_prev["Valor_Total"].sum() if not df_prev.empty else None
    ticket_prev = df_prev["Valor_Total"].mean() if not df_prev.empty else None
    margem_prev = df_prev["Margem"].sum() if not df_prev.empty else None

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("Total de Vendas", fmt_moeda(total_vendas), delta_pct=variacao_pct(total_vendas, total_prev))
    with c2:
        kpi_card("Pedidos", fmt_num(n_pedidos), "linhas de venda")
    with c3:
        kpi_card("Ticket Médio", fmt_moeda(ticket_medio), delta_pct=variacao_pct(ticket_medio, ticket_prev))
    with c4:
        kpi_card("Desconto Concedido", fmt_moeda(total_desconto),
                  fmt_pct(100 * total_desconto / (total_vendas + total_desconto)) + " sobre o bruto")
    with c5:
        kpi_card("Margem Estimada", fmt_moeda(margem_total), delta_pct=variacao_pct(margem_total, margem_prev))

    st.markdown("<br>", unsafe_allow_html=True)
    filtros_bar(df_full if df_full is not None else df)

    col_a, col_b = st.columns([2, 1])
    with col_a:
        chart_card_open("Evolução Mensal de Vendas")
        serie = df.groupby("AnoMes", as_index=False)["Valor_Total"].sum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=serie["AnoMes"], y=serie["Valor_Total"],
            mode="lines", fill="tozeroy", line_shape="spline",
            line=dict(color=COLORS["orange"], width=3),
            fillcolor="rgba(232,117,46,0.22)",
            hovertemplate="%{x|%b/%Y}<br>R$ %{y:,.2f}<extra></extra>",
            name="Vendas",
        ))
        fig = plotly_layout_defaults(fig, height=340, legend=False)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    with col_b:
        chart_card_open("Vendas por Categoria")
        cat = df.groupby("Categoria", as_index=False)["Valor_Total"].sum().sort_values(
            "Valor_Total", ascending=False
        )
        fig = _donut(cat["Categoria"], cat["Valor_Total"], height=340)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    col_c, col_d = st.columns(2)
    with col_c:
        chart_card_open("Vendas por Ano")
        ano = df.groupby("Ano", as_index=False)["Valor_Total"].sum()
        fig = go.Figure(go.Bar(
            x=ano["Ano"].astype(str), y=ano["Valor_Total"],
            marker=dict(color=COLORS["orange"], cornerradius=8),
            text=[fmt_moeda(v) for v in ano["Valor_Total"]],
            textposition="inside",
            textfont=dict(color=COLORS["text"]),
            hovertemplate="%{x}<br>R$ %{y:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=300, legend=False)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    with col_d:
        chart_card_open("Vendas por Forma de Pagamento")
        pag = df.groupby("Forma_Pagamento", as_index=False)["Valor_Total"].sum().sort_values(
            "Valor_Total", ascending=True
        )
        fig = go.Figure(go.Bar(
            x=pag["Valor_Total"], y=pag["Forma_Pagamento"], orientation="h",
            marker=dict(color=COLORS["lime"], cornerradius=8),
            text=[fmt_moeda(v) for v in pag["Valor_Total"]],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color=COLORS["navy"]),
            hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=300, legend=False)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()


# ----------------------------------------------------------------------------
# PÁGINA 2 — VENDAS POR VENDEDOR
# ----------------------------------------------------------------------------
def view_vendedor(df: pd.DataFrame, df_full: pd.DataFrame | None = None):
    nav_bar("Vendas por Vendedor")
    page_header(
        "Vendas por Vendedor",
        "Desempenho comparado da equipe de vendas da Casa&Obra.",
    )

    if df.empty:
        st.warning("Nenhum dado para os filtros selecionados.")
        return

    resumo = df.groupby("Vendedor", as_index=False).agg(
        Total=("Valor_Total", "sum"),
        Pedidos=("Valor_Total", "count"),
        Ticket=("Valor_Total", "mean"),
        Desconto=("Desconto", "sum"),
        Margem=("Margem", "sum"),
    ).sort_values("Total", ascending=False)

    lider = resumo.iloc[0]
    ticket_geral = df["Valor_Total"].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Vendedor Líder", lider["Vendedor"], fmt_moeda(lider["Total"]))
    with c2:
        kpi_card("Vendedores Ativos", fmt_num(resumo.shape[0]))
    with c3:
        kpi_card("Ticket Médio Geral", fmt_moeda(ticket_geral))
    with c4:
        kpi_card("Margem Média/Vendedor", fmt_moeda(resumo["Margem"].mean()))

    st.markdown("<br>", unsafe_allow_html=True)
    filtros_bar(df_full if df_full is not None else df)

    col_a, col_b = st.columns([1, 1.3])
    with col_a:
        chart_card_open("Ranking de Vendas por Vendedor")
        r = resumo.sort_values("Total", ascending=True)
        cores_r = [CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)] for i in range(len(r))]
        fig = go.Figure(go.Bar(
            x=r["Total"], y=r["Vendedor"], orientation="h",
            marker=dict(color=cores_r, cornerradius=8),
            text=[fmt_moeda(v) for v in r["Total"]],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color=_cor_texto_para(cores_r)),
            hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=360, legend=False)
        fig.update_xaxes(visible=False)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    with col_b:
        chart_card_open("Evolução Mensal de Vendas")
        eve = df.groupby("AnoMes", as_index=False)["Valor_Total"].sum()
        fig = go.Figure(go.Bar(
            x=eve["AnoMes"], y=eve["Valor_Total"],
            marker=dict(color="rgba(232,117,46,0.45)", line=dict(color=COLORS["orange"], width=1.5), cornerradius=4),
            text=[fmt_moeda(v) for v in eve["Valor_Total"]],
            textposition="inside",
            textfont=dict(color=COLORS["text"], size=9),
            textangle=-90,
            hovertemplate="%{x|%b/%Y}<br>R$ %{y:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=360, legend=False)
        fig.update_layout(bargap=0.55)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    col_c, col_d = st.columns([1.3, 1])
    with col_c:
        chart_card_open("Mix de Categoria por Vendedor")
        piv = df.groupby(["Vendedor", "Categoria"], as_index=False)["Valor_Total"].sum()
        piv["Pct"] = piv.groupby("Vendedor")["Valor_Total"].transform(lambda s: 100 * s / s.sum())
        ordem_vend = resumo.sort_values("Total", ascending=True)["Vendedor"].tolist()
        fig = go.Figure()
        for i, categoria in enumerate(sorted(piv["Categoria"].unique())):
            serie = piv[piv["Categoria"] == categoria].set_index("Vendedor").reindex(ordem_vend)
            cor = CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)]
            fig.add_trace(go.Bar(
                y=ordem_vend, x=serie["Pct"], orientation="h", name=categoria,
                marker=dict(color=cor, cornerradius=6),
                text=[f"{v:.0f}%" if pd.notna(v) else "" for v in serie["Pct"]],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color=_cor_texto_para([cor])[0]),
                hovertemplate=f"{categoria}<br>" + "%{y}: %{x:.1f}%<extra></extra>",
            ))
        fig.update_layout(barmode="stack")
        fig = plotly_layout_defaults(fig, height=340, legend=True)
        fig.update_xaxes(ticksuffix="%")
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    with col_d:
        chart_card_open("Ticket Médio por Vendedor")
        t = resumo.sort_values("Ticket", ascending=True)
        fig = go.Figure(go.Bar(
            x=t["Ticket"], y=t["Vendedor"], orientation="h",
            marker=dict(
                color=t["Ticket"], colorscale=[[0, COLORS["slate_light"]], [1, COLORS["orange"]]],
                cornerradius=8,
            ),
            text=[fmt_moeda(v) for v in t["Ticket"]],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color=COLORS["text"]),
            hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=340, legend=False)
        fig.update_xaxes(visible=False)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    chart_card_open("Detalhamento por Vendedor")
    tabela = resumo.copy()
    tabela["Total"] = tabela["Total"].apply(fmt_moeda)
    tabela["Ticket"] = tabela["Ticket"].apply(fmt_moeda)
    tabela["Desconto"] = tabela["Desconto"].apply(fmt_moeda)
    tabela["Margem"] = tabela["Margem"].apply(fmt_moeda)
    tabela.columns = ["Vendedor", "Total Vendido", "Pedidos", "Ticket Médio", "Desconto Total", "Margem Estimada"]
    st.dataframe(tabela, width="stretch", hide_index=True)
    chart_card_close()


# ----------------------------------------------------------------------------
# PÁGINA 3 — VENDAS POR PRODUTOS
# ----------------------------------------------------------------------------
def view_produtos(df: pd.DataFrame, df_full: pd.DataFrame | None = None):
    nav_bar("Vendas por Produtos")
    page_header(
        "Vendas por Produtos",
        "Produtos, categorias e subcategorias que mais vendem na Casa&Obra.",
    )

    if df.empty:
        st.warning("Nenhum dado para os filtros selecionados.")
        return

    prod = df.groupby("Nome_Produto", as_index=False).agg(
        Total=("Valor_Total", "sum"),
        Qtd=("Quantidade", "sum"),
        Categoria=("Categoria", "first"),
    ).sort_values("Total", ascending=False)

    top_produto = prod.iloc[0]
    cat_lider = df.groupby("Categoria")["Valor_Total"].sum().idxmax()
    qtd_total = df["Quantidade"].sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Produto Mais Vendido", top_produto["Nome_Produto"], fmt_moeda(top_produto["Total"]))
    with c2:
        kpi_card("Categoria Líder", cat_lider)
    with c3:
        kpi_card("Itens Vendidos", fmt_num(qtd_total), "unidades/pacotes/sacos")
    with c4:
        kpi_card("Produtos no Catálogo", fmt_num(df["Nome_Produto"].nunique()))

    st.markdown("<br>", unsafe_allow_html=True)
    filtros_bar(df_full if df_full is not None else df)

    col_a, col_b = st.columns([1.3, 1])
    with col_a:
        chart_card_open("Top 15 Produtos por Faturamento")
        top15 = prod.head(15).sort_values("Total", ascending=True)
        fig = go.Figure(go.Bar(
            x=top15["Total"], y=top15["Nome_Produto"], orientation="h",
            marker=dict(
                color=top15["Total"], colorscale=[[0, COLORS["slate_light"]], [1, COLORS["orange"]]],
                cornerradius=6,
            ),
            text=[fmt_moeda(v) for v in top15["Total"]],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color=COLORS["text"], size=10),
            hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=420, legend=False)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    with col_b:
        chart_card_open("Participação por Categoria")
        cat = df.groupby("Categoria", as_index=False)["Valor_Total"].sum().sort_values(
            "Valor_Total", ascending=False
        )
        fig = _donut(cat["Categoria"], cat["Valor_Total"], height=420)
        st.plotly_chart(fig, width="stretch")
        chart_card_close()

    chart_card_open("Categoria e Subcategoria — Mapa de Faturamento")
    sub = df.groupby(["Categoria", "Subcategoria"], as_index=False)["Valor_Total"].sum()
    fig = px.treemap(
        sub, path=["Categoria", "Subcategoria"], values="Valor_Total",
        color="Categoria", color_discrete_sequence=CATEGORY_PALETTE,
    )
    fig.update_traces(
        marker=dict(line=dict(color=COLORS["surface"], width=2)),
        textfont=dict(family="Work Sans", size=12, color=COLORS["navy"]),
        hovertemplate="%{label}<br>R$ %{value:,.2f}<extra></extra>",
    )
    fig = plotly_layout_defaults(fig, height=420, legend=False)
    fig.update_layout(margin=dict(l=4, r=4, t=10, b=4))
    st.plotly_chart(fig, width="stretch")
    chart_card_close()

    chart_card_open("Detalhamento de Produtos")
    tabela = prod.copy()
    tabela["Total"] = tabela["Total"].apply(fmt_moeda)
    tabela.columns = ["Produto", "Total Vendido", "Quantidade", "Categoria"]
    st.dataframe(tabela, width="stretch", hide_index=True, height=320)
    chart_card_close()
