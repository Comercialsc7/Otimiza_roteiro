from __future__ import annotations

import folium
import pandas as pd
from folium.plugins import MarkerCluster

from src.data.schema import PAUTA_CORES, PAUTA_LABELS

SC_CENTER = [-27.2423, -50.2189]


def _cor_pauta(pauta: str) -> str:
    return PAUTA_CORES.get(str(pauta).upper(), "#6A737D")


def construir_mapa(
    clientes: pd.DataFrame,
    vendedores: pd.DataFrame,
    resultado: pd.DataFrame | None = None,
) -> folium.Map:
    if resultado is not None and not resultado.empty:
        base_cli = resultado
        lat_col_points = base_cli["lat"].tolist() + vendedores["lat"].tolist()
        lon_col_points = base_cli["lon"].tolist() + vendedores["lon"].tolist()
    elif not clientes.empty:
        base_cli = clientes
        lat_col_points = base_cli["lat"].tolist() + vendedores["lat"].tolist()
        lon_col_points = base_cli["lon"].tolist() + vendedores["lon"].tolist()
    elif not vendedores.empty:
        base_cli = clientes
        lat_col_points = vendedores["lat"].tolist()
        lon_col_points = vendedores["lon"].tolist()
    else:
        return folium.Map(location=SC_CENTER, zoom_start=7, tiles="OpenStreetMap")

    center_lat = float(sum(lat_col_points) / len(lat_col_points))
    center_lon = float(sum(lon_col_points) / len(lon_col_points))
    mapa = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles="OpenStreetMap")

    for _, v in vendedores.iterrows():
        cor = _cor_pauta(v["pauta"])
        folium.Marker(
            location=[float(v["lat"]), float(v["lon"])],
            popup=(
                f"<b>Vendedor</b><br>"
                f"{v['codigo_vendedor']} — {v['nome']}<br>"
                f"Pauta: {PAUTA_LABELS.get(v['pauta'], v['pauta'])}<br>"
                f"Região: {v['regiao']}"
            ),
            tooltip=f"Vendedor {v['codigo_vendedor']} ({v['pauta']})",
            icon=folium.Icon(color="black", icon="user", prefix="fa", icon_color=cor),
        ).add_to(mapa)

    cluster = MarkerCluster(name="Clientes").add_to(mapa)
    pontos = resultado if resultado is not None else clientes
    if pontos is not None and not pontos.empty:
        for _, c in pontos.iterrows():
            pauta = c["pauta_sugerida"] if "pauta_sugerida" in c.index else c.get(
                "pauta_atual", "D"
            )
            cor = _cor_pauta(pauta)
            vendedor_txt = (
                c["vendedor_sugerido"]
                if "vendedor_sugerido" in c.index
                else c.get("codigo_vendedor_atual", "-")
            )
            folium.CircleMarker(
                location=[float(c["lat"]), float(c["lon"])],
                radius=6,
                color=cor,
                fill=True,
                fill_color=cor,
                fill_opacity=0.85,
                popup=(
                    f"<b>Cliente</b><br>"
                    f"{c['codigo_cliente']} — {c['razao']}<br>"
                    f"Pauta: {PAUTA_LABELS.get(str(pauta), pauta)}<br>"
                    f"Vendedor: {vendedor_txt}"
                ),
                tooltip=f"{c['codigo_cliente']} | {PAUTA_LABELS.get(str(pauta), pauta)}",
            ).add_to(cluster)

    legenda = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:9999;
                background:white;padding:10px 12px;border:1px solid #ccc;
                border-radius:4px;font-size:13px;line-height:1.5;">
      <b>Legenda</b><br>
      <span style="color:#1F6FEB;">●</span> Pauta D<br>
      <span style="color:#2EA44F;">●</span> Pauta M<br>
      <span style="color:#E6B800;">●</span> PC<br>
      <span style="color:#D73A49;">●</span> A definir<br>
      <b>pin</b> Vendedor (ancora)
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(legenda))
    return mapa
