"""
Casa&Obra — Painel de Vendas
Renderização das três páginas do painel: Análise de Vendas, Vendas por
Vendedor e Vendas por Produtos.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (
    COLORS, CATEGORY_PALETTE, MESES_PT,
    fmt_moeda, fmt_num, fmt_pct, plotly_layout_defaults,
)


# ----------------------------------------------------------------------------
# Componentes reutilizáveis
# ----------------------------------------------------------------------------
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


def kpi_card(label: str, value: str, note: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
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


# ----------------------------------------------------------------------------
# PÁGINA 1 — ANÁLISE DE VENDAS
# ----------------------------------------------------------------------------
def view_analise(df: pd.DataFrame):
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

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("Total de Vendas", fmt_moeda(total_vendas))
    with c2:
        kpi_card("Pedidos", fmt_num(n_pedidos), "linhas de venda")
    with c3:
        kpi_card("Ticket Médio", fmt_moeda(ticket_medio))
    with c4:
        kpi_card("Desconto Concedido", fmt_moeda(total_desconto),
                  fmt_pct(100 * total_desconto / (total_vendas + total_desconto)) + " sobre o bruto")
    with c5:
        kpi_card("Margem Estimada", fmt_moeda(margem_total),
                  fmt_pct(100 * margem_total / total_vendas) + " de margem")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 1])
    with col_a:
        chart_card_open("Evolução Mensal de Vendas")
        serie = df.groupby("AnoMes", as_index=False)["Valor_Total"].sum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=serie["AnoMes"], y=serie["Valor_Total"],
            mode="lines", fill="tozeroy",
            line=dict(color=COLORS["orange"], width=2.5),
            fillcolor="rgba(232,117,46,0.15)",
            hovertemplate="%{x|%b/%Y}<br>R$ %{y:,.2f}<extra></extra>",
            name="Vendas",
        ))
        fig = plotly_layout_defaults(fig, height=340, legend=False)
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()

    with col_b:
        chart_card_open("Vendas por Categoria")
        cat = df.groupby("Categoria", as_index=False)["Valor_Total"].sum().sort_values(
            "Valor_Total", ascending=False
        )
        fig = go.Figure(go.Pie(
            labels=cat["Categoria"], values=cat["Valor_Total"], hole=0.55,
            marker=dict(colors=CATEGORY_PALETTE, line=dict(color="white", width=2)),
            textinfo="percent", textfont=dict(size=11),
            hovertemplate="%{label}<br>R$ %{value:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=340, legend=True)
        fig.update_layout(legend=dict(orientation="v", x=1, y=0.5, font=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()

    col_c, col_d = st.columns(2)
    with col_c:
        chart_card_open("Vendas por Ano")
        ano = df.groupby("Ano", as_index=False)["Valor_Total"].sum()
        fig = go.Figure(go.Bar(
            x=ano["Ano"].astype(str), y=ano["Valor_Total"],
            marker_color=COLORS["navy"],
            hovertemplate="%{x}<br>R$ %{y:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=300, legend=False)
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()

    with col_d:
        chart_card_open("Vendas por Forma de Pagamento")
        pag = df.groupby("Forma_Pagamento", as_index=False)["Valor_Total"].sum().sort_values(
            "Valor_Total", ascending=True
        )
        fig = go.Figure(go.Bar(
            x=pag["Valor_Total"], y=pag["Forma_Pagamento"], orientation="h",
            marker_color=COLORS["orange"],
            hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=300, legend=False)
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()


# ----------------------------------------------------------------------------
# PÁGINA 2 — VENDAS POR VENDEDOR
# ----------------------------------------------------------------------------
def view_vendedor(df: pd.DataFrame):
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

    col_a, col_b = st.columns([1, 1.3])
    with col_a:
        chart_card_open("Ranking de Vendas por Vendedor")
        r = resumo.sort_values("Total", ascending=True)
        fig = go.Figure(go.Bar(
            x=r["Total"], y=r["Vendedor"], orientation="h",
            marker_color=[CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)] for i in range(len(r))],
            text=[fmt_moeda(v) for v in r["Total"]],
            textposition="outside",
            hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=360, legend=False)
        fig.update_xaxes(visible=False)
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()

    with col_b:
        chart_card_open("Evolução Mensal por Vendedor")
        eve = df.groupby(["AnoMes", "Vendedor"], as_index=False)["Valor_Total"].sum()
        fig = px.line(
            eve, x="AnoMes", y="Valor_Total", color="Vendedor",
            color_discrete_sequence=CATEGORY_PALETTE,
        )
        fig.update_traces(line=dict(width=2))
        fig = plotly_layout_defaults(fig, height=360, legend=True)
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()

    col_c, col_d = st.columns([1.3, 1])
    with col_c:
        chart_card_open("Categoria de Produto por Vendedor")
        piv = df.groupby(["Vendedor", "Categoria"], as_index=False)["Valor_Total"].sum()
        fig = px.bar(
            piv, x="Vendedor", y="Valor_Total", color="Categoria",
            color_discrete_sequence=CATEGORY_PALETTE, barmode="stack",
        )
        fig = plotly_layout_defaults(fig, height=340, legend=True)
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()

    with col_d:
        chart_card_open("Ticket Médio por Vendedor")
        t = resumo.sort_values("Ticket", ascending=True)
        fig = go.Figure(go.Bar(
            x=t["Ticket"], y=t["Vendedor"], orientation="h",
            marker_color=COLORS["slate"],
            hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=340, legend=False)
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()

    chart_card_open("Detalhamento por Vendedor")
    tabela = resumo.copy()
    tabela["Total"] = tabela["Total"].apply(fmt_moeda)
    tabela["Ticket"] = tabela["Ticket"].apply(fmt_moeda)
    tabela["Desconto"] = tabela["Desconto"].apply(fmt_moeda)
    tabela["Margem"] = tabela["Margem"].apply(fmt_moeda)
    tabela.columns = ["Vendedor", "Total Vendido", "Pedidos", "Ticket Médio", "Desconto Total", "Margem Estimada"]
    st.dataframe(tabela, use_container_width=True, hide_index=True)
    chart_card_close()


# ----------------------------------------------------------------------------
# PÁGINA 3 — VENDAS POR PRODUTOS
# ----------------------------------------------------------------------------
def view_produtos(df: pd.DataFrame):
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

    col_a, col_b = st.columns([1.3, 1])
    with col_a:
        chart_card_open("Top 15 Produtos por Faturamento")
        top15 = prod.head(15).sort_values("Total", ascending=True)
        fig = go.Figure(go.Bar(
            x=top15["Total"], y=top15["Nome_Produto"], orientation="h",
            marker_color=COLORS["orange"],
            hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=420, legend=False)
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()

    with col_b:
        chart_card_open("Participação por Categoria")
        cat = df.groupby("Categoria", as_index=False)["Valor_Total"].sum().sort_values(
            "Valor_Total", ascending=False
        )
        fig = go.Figure(go.Pie(
            labels=cat["Categoria"], values=cat["Valor_Total"], hole=0.55,
            marker=dict(colors=CATEGORY_PALETTE, line=dict(color="white", width=2)),
            textinfo="percent", textfont=dict(size=11),
            hovertemplate="%{label}<br>R$ %{value:,.2f}<extra></extra>",
        ))
        fig = plotly_layout_defaults(fig, height=420, legend=True)
        fig.update_layout(legend=dict(orientation="v", x=1, y=0.5, font=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)
        chart_card_close()

    chart_card_open("Categoria e Subcategoria — Mapa de Faturamento")
    sub = df.groupby(["Categoria", "Subcategoria"], as_index=False)["Valor_Total"].sum()
    fig = px.treemap(
        sub, path=["Categoria", "Subcategoria"], values="Valor_Total",
        color="Categoria", color_discrete_sequence=CATEGORY_PALETTE,
    )
    fig.update_traces(
        hovertemplate="%{label}<br>R$ %{value:,.2f}<extra></extra>",
        textfont=dict(family="Work Sans", size=12),
    )
    fig = plotly_layout_defaults(fig, height=420, legend=False)
    fig.update_layout(margin=dict(l=4, r=4, t=10, b=4))
    st.plotly_chart(fig, use_container_width=True)
    chart_card_close()

    chart_card_open("Detalhamento de Produtos")
    tabela = prod.copy()
    tabela["Total"] = tabela["Total"].apply(fmt_moeda)
    tabela.columns = ["Produto", "Total Vendido", "Quantidade", "Categoria"]
    st.dataframe(tabela, use_container_width=True, hide_index=True, height=320)
    chart_card_close()
