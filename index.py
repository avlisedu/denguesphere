from anyio import Path
import streamlit as st
from i18n import t, lang_selector

# ======================================
# CONFIGURAÇÃO GERAL DO SISTEMA
# ======================================
st.set_page_config(
    page_title="DengueSphere - Web App",
    page_icon=str(Path("img/barra.png")),
    layout="wide",
)

# ======================================
# ESTILO VISUAL
# ======================================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================================
# SELETOR DE IDIOMA
# ======================================
lang_area = st.empty()
with lang_area:
    lang_selector()

# ======================================
# MENU SUPERIOR COM TRADUÇÕES
# ======================================
pg = st.navigation(
    [
        st.Page("pages/home.py", title=t("nav_home")),
        st.Page("pages/coordenadas.py", title=t("nav_coords")),
        st.Page("pages/clusterizador.py", title=t("nav_cluster")),
        st.Page("pages/sobre.py", title=t("nav_about")),
    ],
    position="top"
)

pg.run()
