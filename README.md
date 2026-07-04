# Casa&Obra — Painel de Vendas (Streamlit)

Dashboard interativo em Python para a loja de materiais de construção **Casa&Obra**,
com base na planilha `Vendas_Materiais_Construcao_Com_Valor_Total.xlsx`.

## Estrutura

```
casa_obra_dashboard/
├── app.py          # arquivo principal (rodar este)
├── views.py        # as 3 páginas: Análise, Vendedor, Produtos
├── styles.py       # identidade visual (CSS)
├── utils.py        # carga de dados e funções auxiliares
├── requirements.txt
├── assets/         # logos Casa&Obra
└── data/
    └── vendas.xlsx # planilha de vendas
```

## Como rodar

1. Instale as dependências (recomendado usar um ambiente virtual):
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o app:
   ```bash
   streamlit run app.py
   ```

3. O navegador abrirá automaticamente em `http://localhost:8501`.

## Páginas

- **📊 Análise de Vendas** — KPIs gerais, evolução mensal, vendas por categoria,
  por ano e por forma de pagamento.
- **🧑‍🔧 Vendas por Vendedor** — ranking da equipe, evolução mensal por
  vendedor, mix de categorias por vendedor e tabela detalhada.
- **🧱 Vendas por Produtos** — top produtos, participação por categoria,
  mapa (treemap) de categoria/subcategoria e tabela completa de produtos.

Todos os filtros da barra lateral (período, categoria, vendedor e forma de
pagamento) se aplicam simultaneamente às três páginas.

## Atualizar os dados

Basta substituir o arquivo `data/vendas.xlsx` por uma nova planilha com as
mesmas colunas:

`Data_Venda, Nome_Cliente, Nome_Produto, Categoria, Subcategoria, Unidade,
Quantidade, Preço_Unitário, Desconto, Valor_Total, Custo_Unitário,
Forma_Pagamento, Vendedor`

## Identidade visual

Paleta baseada na logo Casa&Obra (laranja `#E8752E`, marinho `#22314A` e
lima `#E4F222`), tipografia Archivo Black + Work Sans + IBM Plex Mono, e um
conceito de "planta baixa": cartões com cantos de projeto técnico e uma régua
de três cores como divisor de seções.
