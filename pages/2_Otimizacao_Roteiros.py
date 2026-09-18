from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.loader import listar_regioes
from src.data.schema import PAUTA_LABELS
from src.data.session import (
    KEY_CLIENTES,
    KEY_PARAMS,
    KEY_RESULTADO,
    KEY_VENDEDORES,
    bases_carregadas,
    clear_resultado,
    init_session,
)
from src.models.optimizer import otimizar_regiao
from src.viz.maps import construir_mapa

st.set_page_config(page_title="Otimização de Roteiros", layout="wide")
init_session()

st.sidebar.page_link("Home.py", label="Home")
st.sidebar.page_link("pages/1_Carregar_Bases.py", label="Carregar Bases")
st.sidebar.page_link("pages/2_Otimizacao_Roteiros.py", label="Otimização de Roteiros")

st.title("Otimização de Roteiros")

if not bases_carregadas():
    st.warning("Carregue as bases em **Carregar Bases** antes de otimizar.")
    st.stop()

clientes = st.session_state[KEY_CLIENTES]
vendedores = st.session_state[KEY_VENDEDORES]
regioes = listar_regioes(clientes, vendedores)

st.sidebar.header("Filtros")
regiao = st.sidebar.selectbox("Região", regioes)
n_pautas = st.sidebar.radio("Número de pautas", options=[2, 3], index=0, horizontal=True)
limiar_km = st.sidebar.slider("Limiar km (A definir)", min_value=5.0, max_value=120.0, value=40.0, step=1.0)
tolerancia_pct = st.sidebar.slider(
    "Tolerância da média (%)",
    min_value=0.0,
    max_value=50.0,
    value=5.0,
    step=1.0,
)

cli_reg = clientes[clientes["regiao"] == regiao]
ven_reg = vendedores[vendedores["regiao"] == regiao]
if n_pautas == 2:
    ven_ativas = ven_reg[ven_reg["pauta"].isin(["D", "M"])]
else:
    ven_ativas = ven_reg[ven_reg["pauta"].isin(["D", "M", "PC"])]

st.sidebar.caption(f"Clientes na região: {len(cli_reg)}")
st.sidebar.caption(f"Âncoras ativas: {len(ven_ativas)}")
if len(ven_ativas) > 0 and len(cli_reg) > 0:
    st.sidebar.caption(f"Média alvo: {len(cli_reg) / len(ven_ativas):.1f} clientes/vendedor")

rodar = st.sidebar.button("Otimizar", type="primary")
if st.sidebar.button("Limpar resultado"):
    clear_resultado()
    st.rerun()

if rodar:
    try:
        resultado, meta = otimizar_regiao(
            clientes=clientes,
            vendedores=vendedores,
            regiao=regiao,
            n_pautas=n_pautas,
            limiar_km=limiar_km,
            tolerancia_pct=tolerancia_pct,
        )
        st.session_state[KEY_RESULTADO] = resultado
        st.session_state[KEY_PARAMS] = meta
    except Exception as err:
        st.error(str(err))

resultado = st.session_state.get(KEY_RESULTADO)
meta = st.session_state.get(KEY_PARAMS)

m1, m2, m3, m4 = st.columns(4)
if meta and meta.get("regiao") == regiao:
    m1.metric("Clientes", meta["n_clientes"])
    m2.metric("Âncoras", meta["n_ancoras"])
    m3.metric("Média alvo", meta["media_alvo"])
    m4.metric("A definir", meta["n_a_definir"])
else:
    m1.metric("Clientes", len(cli_reg))
    m2.metric("Âncoras", len(ven_ativas))
    media = round(len(cli_reg) / len(ven_ativas), 2) if len(ven_ativas) else 0
    m3.metric("Média alvo", media)
    m4.metric("A definir", "-")

st.subheader("Mapa")
mapa = construir_mapa(
    clientes=cli_reg,
    vendedores=ven_reg if n_pautas == 3 else ven_ativas,
    resultado=resultado if resultado is not None and meta and meta.get("regiao") == regiao else None,
)
st_folium(mapa, width=None, height=560, returned_objects=[])

if resultado is not None and meta and meta.get("regiao") == regiao:
    st.subheader("Resumo por vendedor")
    resumo = meta["resumo_vendedor"].copy()
    resumo["pauta_sugerida"] = resumo["pauta_sugerida"].map(
        lambda x: PAUTA_LABELS.get(x, x)
    )
    st.dataframe(resumo, use_container_width=True)

    st.subheader("Atribuição")
    tabela = resultado[
        [
            "codigo_cliente",
            "razao",
            "regiao",
            "codigo_vendedor_atual",
            "pauta_atual",
            "vendedor_sugerido",
            "nome_vendedor_sugerido",
            "pauta_sugerida",
            "distancia_km",
            "status",
        ]
    ].copy()
    tabela["pauta_atual"] = tabela["pauta_atual"].map(lambda x: PAUTA_LABELS.get(x, x))
    tabela["pauta_sugerida"] = tabela["pauta_sugerida"].map(
        lambda x: PAUTA_LABELS.get(x, x)
    )
    st.dataframe(tabela, use_container_width=True, height=360)

    csv_bytes = tabela.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar atribuição CSV",
        data=csv_bytes,
        file_name=f"atribuicao_{regiao.lower()}.csv",
        mime="text/csv",
    )
else:
    st.info("Ajuste os filtros e clique em **Otimizar** para gerar a atribuição.")
