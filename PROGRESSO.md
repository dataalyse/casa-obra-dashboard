# PROGRESSO: migração do painel para o novo escopo

> Arquivo de passagem de trabalho (pode ser apagado quando terminar).
> Pedido: alterar o dashboard publicado (Streamlit Cloud + este repo) para seguir o
> `ESCOPO_DASHBOARD_CASA_E_OBRA.md` e usar a base `Base_CASA_E_OBRA.xlsx` no lugar da antiga.

## Decisões tomadas
- **Continua em Streamlit + Plotly** (o escopo pede React/ECharts, mas o app já está publicado no
  Streamlit Cloud). Todo o resto do escopo (páginas, gráficos, cores, regras de cálculo) foi seguido.
- Navegação nativa (`st.navigation`, URLs `/visao-geral`, `/vendas`…), menu lateral, Boas-vindas sem menu.
- Base em `data/Base_CASA_E_OBRA.xlsx` → `python scripts/prepare_data.py` gera `data/parquet/*.parquet`
  (o app lê os parquets; se não existirem, gera sozinho).
- Data-base = 30/09/2026 (`core/data.py: HOJE`).
- Comparativo: se o período anterior começa antes de jan/2025 (início da base) os KPIs mostram
  "— comparação indisponível" em vez de variações enganosas (ex.: padrão "Últimos 12 meses").
- Filtro cruzado: só em gráficos de **barra** (clicar em pizza/rosca não gera evento no Streamlit).
  Implementado em: categoria (Vendas, com drill-down para subcategoria), margem por categoria
  (Rentabilidade), cidade (Clientes). Chips ⚡ removem; Esc limpa.
- Valores de referência conferidos com os dados: faturamento R$ 45.749.132,64 · lucro R$ 13.114.763,98 ·
  margem 28,7% · 29.075 vendas · ticket R$ 1.573,49 · set/2026 R$ 2.913.761,68 · estoque set/26 R$ 2.573.752,30.

## Estrutura
```
app.py              navegação, logo, atalhos de teclado (1–7, F, Esc)
core/data.py        carga + tabelas analíticas (itens = vendas não canceladas com atributos)
core/filters.py     filtros globais persistentes, chips, filtro cruzado, Ctx
core/metrics.py     medidas da seção 5 (resumo, metas, ABC, estoque, giro, NPS…)
core/theme.py       paleta, CSS, tema Plotly, formatadores pt-BR, ícones lucide
core/ui.py          KPI com sparkline, cartão de gráfico com menu ⋯ (ver dados/CSV), tabelas HTML
views/*.py          uma página por arquivo
```

## Status das páginas
| Página | Status |
|---|---|
| 0 Boas-vindas (`views/inicio.py`) | ✅ pronta e testada |
| 1 Visão Geral | ✅ pronta e testada |
| 2 Vendas & Comercial | ✅ pronta e testada (filtro cruzado OK) |
| 3 Estoque | ⚠️ escrita, **não executada ainda** |
| 4 Rentabilidade | ⚠️ escrita, **não executada ainda** |
| 5 Financeiro | ⚠️ escrita, **não executada ainda** |
| 6 Clientes | ⚠️ escrita, **não executada ainda** |
| 7 Inteligência (`views/inteligencia.py`) | ❌ **falta escrever** (hoje não existe o arquivo → o app não sobe) |

## O que falta (em ordem)
1. **Escrever `views/inteligencia.py`** (escopo seção 6, página 7), aplica todos os filtros:
   - 4 cards de alerta com link (`st.page_link(nav.PAGES[...])`):
     risco de ruptura (`estoque_enriquecido(...)["risco_ruptura"]`) → Estoque;
     capital parado (dias_sem_venda > 90) → Estoque;
     "vendem muito, lucram pouco" (fat > mediana e margem < mediana, mesma lógica de rentabilidade.py) → Rentabilidade;
     inadimplência (R$ vencidos e % com atraso > 60 dias) → Financeiro.
   - 7.1 heatmap calendário (uma linha por ano: semana × dia da semana, faturamento diário);
   - 7.2 linha mensal + projeção 3 meses tracejada (média móvel 3m × índice sazonal do mesmo mês do ano
     anterior; índice = mês do ano anterior ÷ MM3 de jul–set do ano anterior) com faixa ±10%;
   - 7.3 radar por loja normalizado 0–100 (faturamento, margem, ticket, NPS, % entregas no prazo, giro);
   - 7.4 área empilhada 100% mensal por canal;
   - 7.5 combo entregas/mês + % no prazo (`fEntregas`, `status_entrega == "Entregue no prazo"`) e cartão
     custo de entrega × frete cobrado;
   - 7.6 4–6 insights gerados por regra (melhor mês, categoria de menor margem, % do sábado de manhã,
     crescimento de Resende desde a inauguração…).
2. Rodar `streamlit run app.py` e abrir **todas** as páginas; corrigir exceções (Estoque, Rentabilidade,
   Financeiro, Clientes nunca rodaram). Testar com período "Tudo", uma loja, filtros extras de cada página,
   e "Personalizado".
3. Conferir os valores de referência com período "Tudo" e sem filtros.
4. Atualizar `requirements.txt` (`streamlit>=1.45`, `pandas>=2.2`, `plotly>=5.24`, `openpyxl`, `pyarrow`),
   `.streamlit/config.toml` (cores: primary #F07335, bg #0A1626, secondary #10233A, text #EAF0F7) e o `README.md`.
5. Apagar este arquivo, fazer merge da branch `wip/novo-escopo` na `main` e push → o Streamlit Cloud
   republica https://casa-obra-dashboard.streamlit.app/ (pode ser preciso "Reboot app" no painel do Streamlit).
