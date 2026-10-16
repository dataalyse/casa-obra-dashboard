"""
Carga da base Casa&Obra (parquets gerados por scripts/prepare_data.py) e
montagem das tabelas analíticas usadas pelas páginas.

Tabelas principais devolvidas por `load()`:
- itens    → fVendasItens de vendas NÃO canceladas, já com os atributos do
             cabeçalho (data, loja, canal, cliente, vendedor, pagamento) e do
             produto (categoria, subcategoria, departamento, fornecedor).
             Quase todos os indicadores de venda saem daqui.
- vendas   → fVendas (todas, inclusive canceladas) com os mesmos atributos.
- demais fatos/dimensões com os nomes das abas.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data" / "parquet"
XLSX = ROOT / "data" / "Base_CASA_E_OBRA.xlsx"

HOJE = pd.Timestamp("2026-09-30")          # data-base de todos os cálculos
DATA_MIN = pd.Timestamp("2025-01-01")

LOJA_CURTA = {"L01": "Centro", "L02": "Barra Mansa", "L03": "Resende"}
LOJA_ID = {v: k for k, v in LOJA_CURTA.items()}


def _read(nome: str) -> pd.DataFrame:
    return pd.read_parquet(PARQUET / f"{nome}.parquet")


@st.cache_resource(show_spinner="Carregando a base da Casa&Obra…")
def load() -> dict[str, pd.DataFrame]:
    if not (PARQUET / "fVendas.parquet").exists():
        from scripts.prepare_data import prepare
        prepare()

    t = {p.stem: _read(p.stem) for p in PARQUET.glob("*.parquet")}

    lojas = t["dLojas"].copy()
    lojas["loja"] = lojas["id_loja"].map(LOJA_CURTA)
    prod = t["dProdutos"].merge(t["dCategorias"][["id_categoria", "departamento"]], on="id_categoria", how="left")
    prod = prod.merge(t["dFornecedores"][["id_fornecedor", "fornecedor", "lead_time_dias"]], on="id_fornecedor", how="left")
    cli = t["dClientes"]
    vend = t["dVendedores"]
    pag = t["dFormaPagamento"]
    can = t["dCanais"]

    v = t["fVendas"].copy()
    v["data"] = pd.to_datetime(v["data"])
    v["loja"] = v["id_loja"].map(LOJA_CURTA)
    v = v.merge(cli[["id_cliente", "segmento", "cidade", "tipo_pessoa"]], on="id_cliente", how="left")
    v = v.merge(vend[["id_vendedor", "vendedor"]], on="id_vendedor", how="left")
    v["vendedor"] = v["vendedor"].fillna("E-commerce")
    v = v.merge(can[["id_canal", "canal"]], on="id_canal", how="left")
    v = v.merge(pag[["id_pagamento", "forma_pagamento", "grupo"]], on="id_pagamento", how="left")
    v["segmento"] = v["segmento"].fillna("Não identificado")
    v["ano_mes"] = v["data"].dt.to_period("M").dt.to_timestamp()
    v["hora_int"] = pd.to_numeric(v["hora"].str[:2], errors="coerce")
    v["dow"] = v["data"].dt.dayofweek
    v["cancelada"] = v["status_venda"].eq("Cancelada")

    cab = [
        "id_venda", "data", "ano_mes", "id_loja", "loja", "id_cliente", "id_vendedor", "vendedor",
        "canal", "forma_pagamento", "grupo", "segmento", "cidade", "tipo_pessoa", "tipo_cliente_venda",
        "hora_int", "dow",
    ]
    it = t["fVendasItens"].merge(v.loc[~v["cancelada"], cab], on="id_venda", how="inner")
    it = it.merge(
        prod[["id_produto", "produto", "categoria", "subcategoria", "departamento", "id_fornecedor", "fornecedor"]],
        on="id_produto", how="left",
    )
    for c in ["loja", "vendedor", "canal", "forma_pagamento", "grupo", "segmento", "cidade",
              "categoria", "subcategoria", "departamento", "produto", "fornecedor", "tipo_cliente_venda"]:
        it[c] = it[c].astype("category")

    est = t["fEstoqueMensal"].copy()
    est["mes"] = pd.to_datetime(est["ano_mes"] + "-01")
    est["loja"] = est["id_loja"].map(LOJA_CURTA)
    est = est.merge(
        prod[["id_produto", "produto", "categoria", "subcategoria", "departamento", "id_fornecedor",
              "fornecedor", "lead_time_dias"]],
        on="id_produto", how="left",
    )

    metas = t["fMetas"].copy()
    metas["mes"] = pd.to_datetime(metas["ano_mes"] + "-01")

    desp = t["fDespesas"].copy()
    desp["mes"] = pd.to_datetime(desp["ano_mes"] + "-01")

    cr = t["fContasReceber"].merge(cli[["id_cliente", "cliente", "segmento"]], on="id_cliente", how="left")
    cr["loja"] = cr["id_loja"].map(LOJA_CURTA)
    cp = t["fContasPagar"].copy()
    cp["loja"] = cp["id_loja"].map(LOJA_CURTA)

    orc = t["fOrcamentos"].merge(vend[["id_vendedor", "vendedor"]], on="id_vendedor", how="left")
    orc = orc.merge(can[["id_canal", "canal"]], on="id_canal", how="left")
    orc["vendedor"] = orc["vendedor"].fillna("E-commerce")

    nps = t["fPesquisaNPS"].merge(cli[["id_cliente", "segmento", "cidade", "tipo_pessoa"]], on="id_cliente", how="left")

    ent = t["fEntregas"].copy()
    dev = t["fDevolucoes"].merge(prod[["id_produto", "categoria", "departamento"]], on="id_produto", how="left")

    return {
        "itens": it, "vendas": v, "estoque": est, "metas": metas, "despesas": desp,
        "receber": cr, "pagar": cp, "orcamentos": orc, "nps": nps, "entregas": ent,
        "devolucoes": dev, "compras": t["fCompras"], "produtos": prod, "clientes": cli,
        "vendedores": vend, "lojas": lojas, "fornecedores": t["dFornecedores"],
        "categorias": t["dCategorias"], "canais": can, "pagamentos": pag,
    }
