from anyio import Path
import importlib
import streamlit as st
import i18n
import ui

# O Streamlit mantém em memória os módulos já importados; recarregá-los a cada
# execução garante que mudanças em textos (i18n) e estilos (ui) apareçam sem reiniciar o servidor.
importlib.reload(i18n)
importlib.reload(ui)
from i18n import t, lang_selector

# ======================================
# CONFIGURAÇÃO GERAL DO SISTEMA
# ======================================
st.set_page_config(
    page_title="DengueSphere",
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
        st.Page("pages/home.py", title=t("nav_home"), icon=":material/home:"),
        st.Page("pages/coordenadas.py", title=t("nav_coords"), icon=":material/my_location:"),
        st.Page("pages/clusterizador.py", title=t("nav_cluster"), icon=":material/hub:"),
        st.Page("pages/sobre.py", title=t("nav_about"), icon=":material/info:"),
    ],
    position="top"
)

pg.run()
