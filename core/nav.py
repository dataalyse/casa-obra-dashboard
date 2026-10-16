"""Registro das páginas (st.Page) para links internos (st.page_link)."""

PAGES: dict = {}

# (chave, título, rota, ícone material, pergunta exibida nos cards da página inicial, ícone lucide)
MENU = [
    ("visao", "Visão Geral", "visao-geral", ":material/dashboard:", "Como a loja está indo?", "dashboard"),
    ("vendas", "Vendas & Comercial", "vendas", ":material/shopping_cart:", "O que, quanto e quem está vendendo?", "cart"),
    ("estoque", "Estoque", "estoque", ":material/inventory_2:", "O que falta, o que sobra e o que comprar?", "boxes"),
    ("rentab", "Rentabilidade", "rentabilidade", ":material/trending_up:", "Onde está o lucro de verdade?", "trending"),
    ("finan", "Financeiro", "financeiro", ":material/account_balance_wallet:", "Quanto vou receber e pagar?", "wallet"),
    ("clientes", "Clientes", "clientes", ":material/group:", "Quem são e como compram?", "users"),
    ("intel", "Inteligência", "inteligencia", ":material/auto_awesome:", "Alertas e oportunidades", "sparkles"),
]

# rótulo curto usado na barra de navegação do topo
NAV_LABEL = {"visao": "Visão Geral", "vendas": "Vendas", "estoque": "Estoque", "rentab": "Rentabilidade",
             "finan": "Financeiro", "clientes": "Clientes", "intel": "Inteligência"}

# descrição exibida nos cards da página inicial
DESC = {
    "visao": "Faturamento, lucro, metas e o caminho do faturamento até o resultado.",
    "vendas": "Canais, categorias, horários de pico, ranking de vendedores e orçamentos.",
    "estoque": "Situação do estoque, curva ABC, capital parado e sugestão de compra.",
    "rentab": "Margem por produto e categoria, efeito dos descontos e ranking de lucro.",
    "finan": "Fluxo de caixa, contas a receber e a pagar, inadimplência e despesas.",
    "clientes": "Segmentos, recorrência, NPS e os clientes que estão sumindo.",
    "intel": "Alertas, sazonalidade, projeção e comparativo entre as lojas.",
}
