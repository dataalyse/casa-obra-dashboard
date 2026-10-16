# CASA & OBRA · Painel de Gestão (Streamlit)

Dashboard demonstrativo da **Datalyse** para uma rede de 3 lojas de materiais de construção no Sul
Fluminense (Centro · Volta Redonda, Barra Mansa e Resende). Dados fictícios de jan/2025 a set/2026,
com data-base em **30/09/2026**.

🔗 https://casa-obra-dashboard.streamlit.app/

## Páginas

| # | Página | Pergunta que responde |
|---|---|---|
| 0 | Boas-vindas | Mini-KPIs de set/2026 e atalhos para as análises |
| 1 | Visão Geral | Como a loja está indo? (faturamento, margem, meta, cascata até o resultado) |
| 2 | Vendas & Comercial | O que, quanto e quem está vendendo? (canais, categorias, horários, vendedores, orçamentos) |
| 3 | Estoque | O que falta, o que sobra e o que comprar? (situação, curva ABC, capital parado, sugestão de reposição) |
| 4 | Rentabilidade | Onde está o lucro de verdade? (matriz faturamento × margem, descontos, ranking de lucro) |
| 5 | Financeiro | Quanto vou receber e pagar? (fluxo de caixa, aging, calendário de vencimentos, despesas) |
| 6 | Clientes | Quem são e como compram? (segmentos, RFM, NPS, clientes em risco) |
| 7 | Inteligência | Alertas, sazonalidade, projeção, comparativo entre lojas e insights automáticos |

**Recursos:** filtros globais que persistem entre páginas (período com atalhos, loja, departamento,
categoria, canal, segmento, vendedor) com chips removíveis · comparativo com período anterior ou ano
anterior · filtro cruzado clicando nas barras (categoria → subcategoria) · menu **⋯** em cada gráfico com
"Ver dados" e exportação CSV · PNG pelo ícone de câmera · modo apresentação · atalhos `1`–`7`, `F` e `Esc`.

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura

```
app.py                     navegação (st.navigation), logo e atalhos de teclado
core/data.py               carga da base e tabelas analíticas
core/filters.py            filtros globais, chips e filtro cruzado
core/metrics.py            regras de cálculo (faturamento, margem, metas, ABC, estoque, giro, NPS…)
core/theme.py              paleta Casa&Obra, CSS, tema dos gráficos, formatação pt-BR
core/ui.py                 cartões de KPI, cartões de gráfico, tabelas
views/                     uma página por arquivo
scripts/prepare_data.py    converte o Excel em parquet
data/Base_CASA_E_OBRA.xlsx base de dados (21 abas, modelo estrela)
data/parquet/              base pré-processada lida pelo app
assets/                    logos (horizontal, ícone e caixa)
```

## Atualizar os dados

1. Substitua `data/Base_CASA_E_OBRA.xlsx` por uma planilha com as mesmas abas e colunas.
2. Rode `python scripts/prepare_data.py` para regenerar `data/parquet/`.
3. Se a data-base mudar, ajuste `HOJE` em `core/data.py`.

## Regras importantes

- Vendas com `status_venda = "Cancelada"` ficam fora de todos os indicadores de venda.
- `id_cliente = CL00000` (balcão não identificado) entra no faturamento, mas não nas análises de clientes.
- Vendas sem vendedor são do e-commerce e aparecem como "E-commerce" nos rankings.
- Estoque é uma foto mensal: usa sempre o último mês do período filtrado.
- Quando o período de comparação começa antes de jan/2025, os indicadores mostram
  "comparação indisponível" em vez de uma variação enganosa.

## Identidade visual

Laranja `#F07335` · amarelo `#F0FA28` · azul `#1F4E79` sobre tema escuro `#0A1626`.
Tipografia Space Grotesk (títulos e números) e Inter (texto).

---
Desenvolvido por **Datalyse** · Dados fictícios para demonstração
