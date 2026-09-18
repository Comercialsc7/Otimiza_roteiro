from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.loader import SchemaError, load_clientes, load_vendedores
from src.data.session import (
    KEY_CLIENTES,
    KEY_VENDEDORES,
    bases_carregadas,
    init_session,
    set_bases,
)

st.set_page_config(page_title="Carregar Bases", layout="wide")
init_session()

st.sidebar.page_link("Home.py", label="Home")
st.sidebar.page_link("pages/1_Carregar_Bases.py", label="Carregar Bases")
st.sidebar.page_link("pages/2_Otimizacao_Roteiros.py", label="Otimização de Roteiros")

st.title("Carregar Bases")
st.caption("Envie os CSVs de clientes e vendedores. Os dados ficam na sessão do app.")

amostra_dir = ROOT / "assets" / "amostras"
usar_amostra = st.checkbox("Usar CSVs de exemplo (assets/amostras)", value=False)

col_a, col_b = st.columns(2)
with col_a:
    file_clientes = st.file_uploader("CSV clientes", type=["csv"], key="up_clientes")
with col_b:
    file_vendedores = st.file_uploader("CSV vendedores", type=["csv"], key="up_vendedores")

carregar = st.button("Carregar na sessão", type="primary")

if carregar:
    try:
        if usar_amostra:
            path_c = amostra_dir / "clientes.csv"
            path_v = amostra_dir / "vendedores.csv"
            if not path_c.exists() or not path_v.exists():
                st.error("Arquivos de exemplo não encontrados em assets/amostras.")
            else:
                clientes = load_clientes(path_c)
                vendedores = load_vendedores(path_v)
                set_bases(clientes, vendedores)
                st.success(
                    f"Amostra carregada: {len(clientes)} clientes, {len(vendedores)} vendedores."
                )
        else:
            if file_clientes is None or file_vendedores is None:
                st.warning("Envie os dois arquivos CSV ou marque a amostra.")
            else:
                clientes = load_clientes(file_clientes)
                vendedores = load_vendedores(file_vendedores)
                set_bases(clientes, vendedores)
                st.success(
                    f"Bases carregadas: {len(clientes)} clientes, {len(vendedores)} vendedores."
                )
    except SchemaError as err:
        st.error(str(err))
    except Exception as err:
        st.error(f"Falha ao carregar: {err}")

if bases_carregadas():
    st.subheader("Preview clientes")
    st.dataframe(st.session_state[KEY_CLIENTES].head(50), use_container_width=True)
    st.subheader("Preview vendedores")
    st.dataframe(st.session_state[KEY_VENDEDORES].head(50), use_container_width=True)

st.markdown(
    """
#### Colunas esperadas

**clientes.csv**  
`codigo_cliente, razao, regiao, pauta_atual, codigo_vendedor_atual, lat, lon`

**vendedores.csv**  
`codigo_vendedor, nome, regiao, pauta, lat, lon`

Pautas válidas: `D`, `M`, `PC`.
"""
)
