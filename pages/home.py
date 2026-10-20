import streamlit as st
import base64
from pathlib import Path
from i18n import t

# ======================================
# CONFIGURAÇÃO DE ESTILO
# ======================================
st.markdown("""
<style>
    /* Fundo branco fixo */
    .stApp {
        background-color: #ffffff !important;
    }

    /* Logo à esquerda, centralizada na sua coluna */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 30px;
        margin-bottom: 10px;
    }

    .logo-container img {
        max-width: 280px;
        height: auto;
        border-radius: 0;
        box-shadow: none;
        pointer-events: none;
    }

    /* Título e subtítulo alinhados à esquerda, ao lado da logo */
    .content {
        text-align: left;
    }

    .content h2 {
        color: #0d47a1;
        margin-top: 15px;
    }

    .content em {
        color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

col_logo, col_texto = st.columns([1, 2], gap="large", vertical_alignment="center")

with col_logo:
    logo_path = Path("img/logo.png")
    if logo_path.exists():
        st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(t("coords_logo_warning"))

with col_texto:
    st.markdown(f"""
    <div class="content">
        <h2><strong>{t("home_title_h2")}</strong></h2>
        <p><em>{t("home_subtitle")}</em></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.header(t("home_welcome_header"))

    st.markdown(t("home_main_text"))

st.info(t("home_footer_info"))
