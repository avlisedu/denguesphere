from anyio import Path
import streamlit as st

# ======================================
# CONFIGURAÇÃO GERAL DO SISTEMA
# ======================================
st.set_page_config(
    page_title="DengueSphere v1.0",
    page_icon=str(Path("img/barra.png")),   # ícone da aba
    layout="wide",
)

# ======================================
# ESTILO VISUAL (gradiente azul pastel)
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

# st.markdown("""
# <style>
#     .stAppHeader {
#         background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%);
#     }
#     div[data-testid="stHorizontalBlock"] button {
#         background-color: #e3f2fd;
#         color: #0d47a1;
#         border-radius: 6px;
#         border: none;
#         font-weight: 600;
#     }
#     div[data-testid="stHorizontalBlock"] button:hover {
#         background-color: #64b5f6;
#         color: white;
#     }
#     .version-tag {
#         font-size: 13px;
#         color: gray;
#         text-align: right;
#         margin-top: -10px;
#     }
#     .footer-box {
#         background-color: #e3f2fd;
#         border-radius: 6px;
#         padding: 8px 14px;
#         margin-top: 30px;
#         font-size: 13px;
#         color: #0d47a1;
#     }
# </style>
# """, unsafe_allow_html=True)

# ======================================
# DEFINIÇÃO DA NAVEGAÇÃO SUPERIOR
# ======================================
pg = st.navigation(
    [
        st.Page("pages/home.py", title="Início"),  # ← a logo fica só aqui
        st.Page("pages/coordenadas.py", title="Gerar Coordenadas por CEP"),
        st.Page("pages/clusterizador.py", title="Clusterizador"),
        st.Page("pages/sobre.py", title="Sobre o Projeto"),
   ],
    position="top"
)

pg.run()
