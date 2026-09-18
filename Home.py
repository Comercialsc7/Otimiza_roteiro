from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.session import KEY_CLIENTES, KEY_VENDEDORES, bases_carregadas, init_session

st.set_page_config(
    page_title="Otimização de Roteiros",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

st.title("Otimização de Roteiros")
st.caption("Santa Catarina — distribuição de carteira por região e pauta")

st.markdown(
    """
Aplicação para redistribuir clientes entre vendedores de uma região
com base na proximidade das âncoras (endereço/base do vendedor) e
no equilíbrio de quantidade de clientes por vendedor.

**Fluxo**
1. Carregue os CSVs de clientes e vendedores
2. Abra **Otimização de Roteiros**
3. Filtre a região, escolha 2 ou 3 pautas e execute
4. Veja o mapa Folium e a tabela de atribuição
"""
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Clientes carregados", len(st.session_state[KEY_CLIENTES]) if bases_carregadas() else 0)
with col2:
    st.metric("Vendedores carregados", len(st.session_state[KEY_VENDEDORES]) if bases_carregadas() else 0)
with col3:
    status = "Prontas" if bases_carregadas() else "Pendentes"
    st.metric("Bases", status)

if bases_carregadas():
    st.success("Bases na sessão. Vá para **Otimização de Roteiros** na barra lateral.")
else:
    st.info("Nenhuma base na sessão. Comece por **Carregar Bases**.")

st.sidebar.page_link("Home.py", label="Home")
st.sidebar.page_link("pages/1_Carregar_Bases.py", label="Carregar Bases")
st.sidebar.page_link("pages/2_Otimizacao_Roteiros.py", label="Otimização de Roteiros")
