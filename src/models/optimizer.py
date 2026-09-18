from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.schema import VENDEDOR_A_DEFINIR


def haversine_km(
    lat1: np.ndarray | float,
    lon1: np.ndarray | float,
    lat2: np.ndarray | float,
    lon2: np.ndarray | float,
) -> np.ndarray | float:
    r = 6371.0
    lat1_r = np.radians(lat1)
    lon1_r = np.radians(lon1)
    lat2_r = np.radians(lat2)
    lon2_r = np.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(lat1_r) * np.cos(lat2_r) * np.sin(dlon / 2.0) ** 2
    )
    return 2.0 * r * np.arcsin(np.sqrt(a))


def _filtrar_ancoras(vendedores: pd.DataFrame, n_pautas: int) -> pd.DataFrame:
    df = vendedores.copy()
    if n_pautas == 2:
        df = df[df["pauta"].isin(["D", "M"])]
    elif n_pautas == 3:
        df = df[df["pauta"].isin(["D", "M", "PC"])]
    else:
        raise ValueError("n_pautas deve ser 2 ou 3")
    if df.empty:
        raise ValueError(
            "Nenhuma âncora disponível para o modo escolhido nesta região"
        )
    return df.reset_index(drop=True)


def _matriz_distancias(clientes: pd.DataFrame, ancoras: pd.DataFrame) -> np.ndarray:
    n_c = len(clientes)
    n_a = len(ancoras)
    dist = np.zeros((n_c, n_a), dtype=float)
    c_lat = clientes["lat"].to_numpy(dtype=float)
    c_lon = clientes["lon"].to_numpy(dtype=float)
    a_lat = ancoras["lat"].to_numpy(dtype=float)
    a_lon = ancoras["lon"].to_numpy(dtype=float)
    for j in range(n_a):
        dist[:, j] = haversine_km(c_lat, c_lon, a_lat[j], a_lon[j])
    return dist


def _atribuir_nearest(dist: np.ndarray) -> np.ndarray:
    return dist.argmin(axis=1)


def _balancear(
    dist: np.ndarray,
    assign: np.ndarray,
    n_ancoras: int,
    tolerancia_pct: float,
    max_iter: int = 500,
) -> np.ndarray:
    assign = assign.copy()
    n_clientes = len(assign)
    if n_clientes == 0 or n_ancoras == 0:
        return assign

    media = n_clientes / n_ancoras
    limite = max(0.0, media * (tolerancia_pct / 100.0))

    for _ in range(max_iter):
        counts = np.bincount(assign, minlength=n_ancoras).astype(float)
        acima = counts.max() > media + limite
        abaixo = counts.min() < media - limite
        if not acima and not abaixo:
            break

        s = int(counts.argmax())
        f = int(counts.argmin())
        if s == f or counts[s] - counts[f] <= 1:
            break

        candidatos = np.where(assign == s)[0]
        if len(candidatos) == 0:
            break

        arrependimento = dist[candidatos, f] - dist[candidatos, s]
        i = int(candidatos[np.argmin(arrependimento)])
        assign[i] = f

    return assign


def otimizar_regiao(
    clientes: pd.DataFrame,
    vendedores: pd.DataFrame,
    regiao: str,
    n_pautas: int = 2,
    limiar_km: float = 40.0,
    tolerancia_pct: float = 15.0,
) -> tuple[pd.DataFrame, dict]:
    regiao = regiao.strip().upper()
    cli = clientes[clientes["regiao"] == regiao].copy().reset_index(drop=True)
    ven = vendedores[vendedores["regiao"] == regiao].copy().reset_index(drop=True)

    if cli.empty:
        raise ValueError(f"Nenhum cliente na região {regiao}")
    if ven.empty:
        raise ValueError(f"Nenhum vendedor na região {regiao}")

    ancoras = _filtrar_ancoras(ven, n_pautas)
    dist = _matriz_distancias(cli, ancoras)
    assign = _atribuir_nearest(dist)
    dist_nearest = dist[np.arange(len(cli)), assign]
    dentro = dist_nearest <= limiar_km

    if dentro.any():
        idx = np.where(dentro)[0]
        assign_dentro = _balancear(
            dist[idx][:, :],
            assign[idx].copy(),
            len(ancoras),
            tolerancia_pct,
        )
        assign[idx] = assign_dentro

    dist_atribuida = dist[np.arange(len(cli)), assign]
    fora = ~dentro

    pauta_sugerida = ancoras.loc[assign, "pauta"].to_numpy()
    codigo_sugerido = ancoras.loc[assign, "codigo_vendedor"].to_numpy()
    nome_sugerido = ancoras.loc[assign, "nome"].to_numpy()

    pauta_sugerida = np.where(fora, "A_DEFINIR", pauta_sugerida)
    codigo_sugerido = np.where(fora, VENDEDOR_A_DEFINIR, codigo_sugerido)
    nome_sugerido = np.where(fora, VENDEDOR_A_DEFINIR, nome_sugerido)
    status = np.where(fora, "a_definir", "atribuido")

    resultado = cli.copy()
    resultado["vendedor_sugerido"] = codigo_sugerido
    resultado["nome_vendedor_sugerido"] = nome_sugerido
    resultado["pauta_sugerida"] = pauta_sugerida
    resultado["distancia_km"] = np.round(dist_atribuida, 2)
    resultado["status"] = status

    n_atribuidos = int((~fora).sum())
    media_alvo = n_atribuidos / len(ancoras) if len(ancoras) else 0.0
    resumo_pauta = (
        resultado.groupby("pauta_sugerida", dropna=False)
        .size()
        .rename("qtd")
        .reset_index()
    )
    resumo_vendedor = (
        resultado.groupby(
            ["vendedor_sugerido", "nome_vendedor_sugerido", "pauta_sugerida"],
            dropna=False,
        )
        .size()
        .rename("qtd")
        .reset_index()
    )

    meta = {
        "regiao": regiao,
        "n_pautas": n_pautas,
        "limiar_km": limiar_km,
        "tolerancia_pct": tolerancia_pct,
        "n_clientes": int(len(cli)),
        "n_ancoras": int(len(ancoras)),
        "media_alvo": round(float(media_alvo), 2),
        "n_a_definir": int(fora.sum()),
        "distancia_media_km": round(float(dist_atribuida.mean()), 2),
        "ancoras": ancoras,
        "resumo_pauta": resumo_pauta,
        "resumo_vendedor": resumo_vendedor,
    }
    return resultado, meta
