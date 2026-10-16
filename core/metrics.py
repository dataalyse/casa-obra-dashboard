"""
Medidas do escopo (seção 5). Todas recebem tabelas já filtradas.
Vendas canceladas já foram removidas de `itens` em core.data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.data import HOJE
from core.filters import Ctx, by_loja, itens


def div(a, b):
    try:
        if b is None or b == 0 or pd.isna(b) or pd.isna(a):
            return None
        return a / b
    except TypeError:
        return None


def var(atual, anterior):
    if anterior is None or atual is None or pd.isna(anterior) or anterior == 0:
        return None
    return (atual - anterior) / abs(anterior)


def resumo(it: pd.DataFrame) -> dict:
    fat = float(it["valor_liquido"].sum())
    bruto = float(it["valor_bruto"].sum())
    desc = float(it["valor_desconto"].sum())
    cmv = float(it["custo_total"].sum())
    lucro = float(it["lucro_bruto"].sum())
    n = int(it["id_venda"].nunique())
    linhas = int(len(it))
    return {
        "fat": fat, "bruto": bruto, "desc": desc, "cmv": cmv, "lucro": lucro, "n": n, "linhas": linhas,
        "margem": div(lucro, fat), "ticket": div(fat, n), "desc_pct": div(desc, bruto),
        "itens_venda": div(linhas, n),
    }


def mensal(it: pd.DataFrame, meses: pd.DatetimeIndex | None = None) -> pd.DataFrame:
    g = it.groupby("ano_mes").agg(fat=("valor_liquido", "sum"), lucro=("lucro_bruto", "sum"),
                                  cmv=("custo_total", "sum"), n=("id_venda", "nunique"))
    if meses is not None:
        g = g.reindex(meses, fill_value=0)
    g["margem"] = g["lucro"] / g["fat"].replace(0, np.nan)
    g["ticket"] = g["fat"] / g["n"].replace(0, np.nan)
    return g


def meses_ate(fim: pd.Timestamp, n: int = 12) -> pd.DatetimeIndex:
    ult = fim.to_period("M").to_timestamp()
    return pd.date_range(end=ult, periods=n, freq="MS")


def meses_periodo(ctx: Ctx) -> pd.DatetimeIndex:
    return pd.date_range(ctx.ini.to_period("M").to_timestamp(), ctx.mes_ref, freq="MS")


def spark12(D: dict, ctx: Ctx, col: str = "fat") -> pd.Series:
    """Série mensal dos 12 meses que terminam no fim do período (para os sparklines)."""
    ms = meses_ate(ctx.fim)
    it = itens(D, ctx, ini=ms[0], fim=ctx.fim)
    return mensal(it, ms)[col]


def metas(D: dict, ctx: Ctx, ini=None, fim=None) -> float:
    ini = ctx.ini if ini is None else ini
    fim = ctx.fim if fim is None else fim
    mt = by_loja(D["metas"], ctx)
    m0 = ini.to_period("M").to_timestamp()
    m1 = fim.to_period("M").to_timestamp()
    mt = mt[(mt["mes"] >= m0) & (mt["mes"] <= m1)]
    if ctx.vends:
        ids = D["vendedores"].loc[D["vendedores"]["vendedor"].isin(ctx.vends), "id_vendedor"]
        return float(mt.loc[(mt["nivel_meta"] == "Vendedor") & mt["id_vendedor"].isin(ids), "meta_faturamento"].sum())
    return float(mt.loc[mt["nivel_meta"] == "Loja", "meta_faturamento"].sum())


def metas_mensal(D: dict, ctx: Ctx) -> pd.Series:
    mt = by_loja(D["metas"], ctx)
    mt = mt[(mt["mes"] >= ctx.ini.to_period("M").to_timestamp()) & (mt["mes"] <= ctx.mes_ref)]
    return mt[mt["nivel_meta"] == "Loja"].groupby("mes")["meta_faturamento"].sum()


def despesas(D: dict, ctx: Ctx, ini=None, fim=None) -> pd.DataFrame:
    ini = ctx.ini if ini is None else ini
    fim = ctx.fim if fim is None else fim
    d = by_loja(D["despesas"], ctx)
    return d[(d["mes"] >= ini.to_period("M").to_timestamp()) & (d["mes"] <= fim.to_period("M").to_timestamp())]


def nps(df: pd.DataFrame) -> float | None:
    if df.empty:
        return None
    n = df["nota_0a10"]
    return float(((n >= 9).mean() - (n <= 6).mean()) * 100)


def nps_f(D: dict, ctx: Ctx, ini=None, fim=None) -> pd.DataFrame:
    ini = ctx.ini if ini is None else ini
    fim = ctx.fim if fim is None else fim
    n = by_loja(D["nps"], ctx)
    n = n[(n["data_resposta"] >= ini) & (n["data_resposta"] <= fim)]
    if ctx.segs:
        n = n[n["segmento"].isin(ctx.segs)]
    return n


def abc(it: pd.DataFrame) -> pd.DataFrame:
    """Curva ABC por produto (faturamento decrescente; ≤80% A, ≤95% B, resto C)."""
    p = it.groupby("produto", observed=True).agg(
        fat=("valor_liquido", "sum"), lucro=("lucro_bruto", "sum"), cmv=("custo_total", "sum"),
        qtd=("quantidade", "sum"), categoria=("categoria", "first"), departamento=("departamento", "first"),
    ).sort_values("fat", ascending=False)
    p = p[p["fat"] > 0]
    tot = p["fat"].sum()
    p["acum"] = p["fat"].cumsum() / tot if tot else 0
    p["classe"] = np.where(p["acum"] <= 0.80, "A", np.where(p["acum"] <= 0.95, "B", "C"))
    # o produto que cruza 80% ainda é A (convenção usual)
    return p.reset_index()


def ultima_venda(D: dict, ate: pd.Timestamp) -> pd.DataFrame:
    """Última data de venda por loja+produto até a data de referência."""
    it = D["itens"]
    it = it[it["data"] <= ate]
    return it.groupby(["id_loja", "id_produto"], observed=True)["data"].max().rename("ultima_venda").reset_index()


def estoque_ref(D: dict, ctx: Ctx, mes: pd.Timestamp | None = None) -> pd.DataFrame:
    """Foto do estoque no último mês do período, com filtros de loja/depto/categoria."""
    mes = ctx.mes_ref if mes is None else mes
    e = by_loja(D["estoque"], ctx)
    e = e[e["mes"] == mes]
    if ctx.deptos:
        e = e[e["departamento"].isin(ctx.deptos)]
    if ctx.cats:
        e = e[e["categoria"].isin(ctx.cats)]
    return e


def estoque_enriquecido(D: dict, ctx: Ctx) -> pd.DataFrame:
    """Foto do mês + dias sem venda, venda média diária (3 meses) e sugestão de reposição."""
    e = estoque_ref(D, ctx).copy()
    ref = ctx.data_ref
    uv = ultima_venda(D, ref)
    e = e.merge(uv, on=["id_loja", "id_produto"], how="left")
    e["dias_sem_venda"] = (ref - e["ultima_venda"]).dt.days
    e["dias_sem_venda"] = e["dias_sem_venda"].fillna(999)

    tres = pd.date_range(end=ctx.mes_ref, periods=3, freq="MS")
    s3 = D["estoque"][D["estoque"]["mes"].isin(tres)].groupby(["id_loja", "id_produto"])["saidas_vendas"].sum()
    e = e.merge(s3.rename("saidas_3m").reset_index(), on=["id_loja", "id_produto"], how="left")
    e["saidas_3m"] = e["saidas_3m"].fillna(0)
    e["venda_dia"] = e["saidas_3m"] / 90
    e["sugestao"] = np.maximum(
        0, e["venda_dia"] * (e["lead_time_dias"] + 15) + e["estoque_minimo"] - e["estoque_final"]
    )
    e["sugestao"] = np.ceil(e["sugestao"])
    e["valor_sugestao"] = e["sugestao"] * e["custo_unitario"]
    e["risco_ruptura"] = (e["cobertura_dias"] < e["lead_time_dias"]) & (e["venda_dia"] > 0)
    e["parado"] = (e["dias_sem_venda"] > 90) | (e["situacao_estoque"] == "Excesso")
    return e


def giro(D: dict, ctx: Ctx, loja_ids: list[str] | None = None) -> float | None:
    """CMV dos 12 meses até o fim do período ÷ valor médio do estoque nesses 12 meses."""
    ms = meses_ate(ctx.fim)
    it = itens(D, ctx, ini=ms[0], fim=ctx.fim, cross=False)
    e = D["estoque"]
    e = e[e["mes"].isin(ms)]
    if loja_ids is not None:
        it = it[it["id_loja"].isin(loja_ids)]
        e = e[e["id_loja"].isin(loja_ids)]
    elif ctx.loja_ids:
        e = e[e["id_loja"].isin(ctx.loja_ids)]
    if ctx.deptos:
        e = e[e["departamento"].isin(ctx.deptos)]
    if ctx.cats:
        e = e[e["categoria"].isin(ctx.cats)]
    medio = e.groupby("mes")["valor_estoque_final"].sum().mean()
    meses_c = max(1, it["ano_mes"].nunique())
    cmv_anual = it["custo_total"].sum() * 12 / meses_c
    return div(cmv_anual, medio)


def receber(D: dict, ctx: Ctx) -> pd.DataFrame:
    return by_loja(D["receber"], ctx)


def pagar(D: dict, ctx: Ctx) -> pd.DataFrame:
    return by_loja(D["pagar"], ctx)


def hoje() -> pd.Timestamp:
    return HOJE
