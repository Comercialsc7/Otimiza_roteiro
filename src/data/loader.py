from __future__ import annotations

import pandas as pd

from src.data.schema import (
    CLIENTES_REQUIRED,
    PAUTAS_VALIDAS,
    VENDEDORES_REQUIRED,
)


class SchemaError(ValueError):
    pass


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = (
        out.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return out


def _require_columns(df: pd.DataFrame, required: list[str], label: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SchemaError(
            f"{label}: colunas obrigatórias ausentes: {', '.join(missing)}"
        )


def _to_float(series: pd.Series, col: str, label: str) -> pd.Series:
    converted = pd.to_numeric(series, errors="coerce")
    if converted.isna().any():
        bad = series[converted.isna()].head(5).tolist()
        raise SchemaError(
            f"{label}: valores inválidos em '{col}'. Exemplos: {bad}"
        )
    return converted


def load_clientes(source) -> pd.DataFrame:
    df = pd.read_csv(source)
    df = _normalize_columns(df)
    _require_columns(df, CLIENTES_REQUIRED, "clientes")
    out = df[CLIENTES_REQUIRED].copy()
    out["codigo_cliente"] = out["codigo_cliente"].astype(str).str.strip()
    out["razao"] = out["razao"].astype(str).str.strip()
    out["regiao"] = out["regiao"].astype(str).str.strip().str.upper()
    out["pauta_atual"] = out["pauta_atual"].astype(str).str.strip().str.upper()
    out["codigo_vendedor_atual"] = (
        out["codigo_vendedor_atual"].astype(str).str.strip()
    )
    out["lat"] = _to_float(out["lat"], "lat", "clientes")
    out["lon"] = _to_float(out["lon"], "lon", "clientes")
    invalid = set(out["pauta_atual"].unique()) - PAUTAS_VALIDAS
    if invalid:
        raise SchemaError(
            f"clientes: pauta_atual inválida: {', '.join(sorted(invalid))}. "
            f"Use: {', '.join(sorted(PAUTAS_VALIDAS))}"
        )
    if out["codigo_cliente"].duplicated().any():
        raise SchemaError("clientes: codigo_cliente duplicado")
    return out.reset_index(drop=True)


def load_vendedores(source) -> pd.DataFrame:
    df = pd.read_csv(source)
    df = _normalize_columns(df)
    _require_columns(df, VENDEDORES_REQUIRED, "vendedores")
    out = df[VENDEDORES_REQUIRED].copy()
    out["codigo_vendedor"] = out["codigo_vendedor"].astype(str).str.strip()
    out["nome"] = out["nome"].astype(str).str.strip()
    out["regiao"] = out["regiao"].astype(str).str.strip().str.upper()
    out["pauta"] = out["pauta"].astype(str).str.strip().str.upper()
    out["lat"] = _to_float(out["lat"], "lat", "vendedores")
    out["lon"] = _to_float(out["lon"], "lon", "vendedores")
    invalid = set(out["pauta"].unique()) - PAUTAS_VALIDAS
    if invalid:
        raise SchemaError(
            f"vendedores: pauta inválida: {', '.join(sorted(invalid))}. "
            f"Use: {', '.join(sorted(PAUTAS_VALIDAS))}"
        )
    if out["codigo_vendedor"].duplicated().any():
        raise SchemaError("vendedores: codigo_vendedor duplicado")
    return out.reset_index(drop=True)


def listar_regioes(clientes: pd.DataFrame, vendedores: pd.DataFrame) -> list[str]:
    regs = set(clientes["regiao"].unique()) | set(vendedores["regiao"].unique())
    return sorted(regs)
