from __future__ import annotations

CLIENTES_REQUIRED = [
    "codigo_cliente",
    "razao",
    "regiao",
    "pauta_atual",
    "codigo_vendedor_atual",
    "lat",
    "lon",
]

VENDEDORES_REQUIRED = [
    "codigo_vendedor",
    "nome",
    "regiao",
    "pauta",
    "lat",
    "lon",
]

PAUTAS_VALIDAS = {"D", "M", "PC"}

PAUTA_CORES = {
    "D": "#1F6FEB",
    "M": "#2EA44F",
    "PC": "#E6B800",
    "A_DEFINIR": "#D73A49",
}

PAUTA_LABELS = {
    "D": "Pauta D",
    "M": "Pauta M",
    "PC": "Conveniência (PC)",
    "A_DEFINIR": "A definir",
}

VENDEDOR_A_DEFINIR = "A definir"
