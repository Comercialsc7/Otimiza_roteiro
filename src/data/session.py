from __future__ import annotations

import streamlit as st


KEY_CLIENTES = "clientes"
KEY_VENDEDORES = "vendedores"
KEY_RESULTADO = "resultado_otimizacao"
KEY_PARAMS = "params_otimizacao"


def init_session() -> None:
    defaults = {
        KEY_CLIENTES: None,
        KEY_VENDEDORES: None,
        KEY_RESULTADO: None,
        KEY_PARAMS: None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def bases_carregadas() -> bool:
    return (
        st.session_state.get(KEY_CLIENTES) is not None
        and st.session_state.get(KEY_VENDEDORES) is not None
    )


def set_bases(clientes, vendedores) -> None:
    st.session_state[KEY_CLIENTES] = clientes
    st.session_state[KEY_VENDEDORES] = vendedores
    st.session_state[KEY_RESULTADO] = None
    st.session_state[KEY_PARAMS] = None


def clear_resultado() -> None:
    st.session_state[KEY_RESULTADO] = None
    st.session_state[KEY_PARAMS] = None
