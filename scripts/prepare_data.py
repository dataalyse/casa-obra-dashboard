"""
Casa&Obra — pré-processamento da base.

Lê `data/Base_CASA_E_OBRA.xlsx` (21 abas, modelo estrela) e grava uma cópia
compacta de cada aba em `data/parquet/<aba>.parquet`. O app carrega os
parquets (muito mais rápido que abrir o Excel a cada inicialização) e faz as
agregações em memória.

Uso:
    pip install -r requirements.txt
    python scripts/prepare_data.py
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "Base_CASA_E_OBRA.xlsx"
OUT = ROOT / "data" / "parquet"


def _hora(v) -> str | None:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, dt.time):
        return v.strftime("%H:%M")
    return str(v)[:5]


def prepare(xlsx: Path = XLSX, out: Path = OUT) -> None:
    out.mkdir(parents=True, exist_ok=True)
    abas = pd.read_excel(xlsx, sheet_name=None)
    for nome, df in abas.items():
        if nome.upper().startswith("LEIA"):
            continue
        df = df.copy()
        if "hora" in df.columns:
            df["hora"] = df["hora"].map(_hora)
        if "ano_mes" in df.columns:
            df["ano_mes"] = df["ano_mes"].astype(str).str[:7]
        if "faixa_atraso" in df.columns:
            df["faixa_atraso"] = df["faixa_atraso"].where(df["faixa_atraso"].astype(str).str.contains("dias"))
        # colunas de texto com nulos ficam como string para o parquet
        for c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].astype("string")
        df.to_parquet(out / f"{nome}.parquet", index=False)
        print(f"{nome:<16} {len(df):>7} linhas")


if __name__ == "__main__":
    prepare()
