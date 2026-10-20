import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path
from i18n import t
from ui import inject_styles, html, footer

# ======================================
# CONFIGURAÇÃO DE ESTILO (paleta da página Sobre)
# ======================================
inject_styles()

st.markdown("""
<style>
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 30px;
        margin-bottom: 18px;
    }

    .logo-container img {
        max-width: 260px;
        height: auto;
        pointer-events: none;
    }

    .ds-home-title {
        margin: 24px 0 4px 0;
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.15;
        background: linear-gradient(90deg, #0a2a66 0%, #0d47a1 45%, #00838f 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .ds-home-subtitle {
        color: #00838f;
        font-style: italic;
        font-size: 1.1rem;
    }

    .ds-divider {
        height: 3px;
        margin: 22px 0 8px 0;
        border-radius: 3px;
        background: linear-gradient(90deg, #0d47a1, #00acc1 55%, transparent);
    }

    [data-testid="stHeading"] h2 { color: #0a2a66; }
    [data-testid="stMarkdownContainer"] strong { color: #0d47a1; }
    [data-testid="stMarkdownContainer"] li::marker { color: #00838f; }

    [data-testid="stMarkdownContainer"] blockquote {
        margin: 18px 0;
        padding: 14px 18px;
        border-left: 4px solid #00838f;
        border-radius: 0 12px 12px 0;
        background: #e0f7fa;
        color: #004d55;
    }
    [data-testid="stMarkdownContainer"] blockquote strong { color: #006064; }
</style>
""", unsafe_allow_html=True)

col_logo, col_texto = st.columns([1, 2], gap="large")

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

    # Animação: casos se agrupando em clusters (DBSCAN)
    animacao = (
        Path("assets/cluster_animation.html").read_text(encoding="utf-8")
        .replace("__CAPTION__", t("home_anim_caption"))
        .replace("__CLUSTER__", t("home_anim_cluster"))
        .replace("__NOISE__", t("home_anim_noise"))
    )
    components.html(animacao, height=300)

with col_texto:
    html(f"""
    <div class="ds-home-title">{t("home_title")}</div>
    <div class="ds-home-subtitle">{t("home_subtitle")}</div>
    <div class="ds-divider"></div>
    """)

    st.header(t("home_welcome_header"))

    st.markdown(t("home_main_text"))

footer(t("home_footer"))
