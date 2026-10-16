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
