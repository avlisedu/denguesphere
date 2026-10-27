import streamlit as st
import base64
from pathlib import Path
from i18n import t
from ui import inject_styles, html, section, DATASET_URL

# ======================================
# CONFIGURAÇÃO DE ESTILO (paleta da página Sobre)
# ======================================
inject_styles()

st.markdown("""
<style>
    html, body { background: #ffffff; }
    html body .stApp,
    html body [data-testid="stAppViewContainer"],
    html body [data-testid="stMain"] { background: transparent !important; }

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

    .ds-dataset .ds-pub-icon { color: #0d47a1; background: #e3f2fd; }
    .ds-dataset p { margin: 0 0 12px 0; font-size: 0.94rem; line-height: 1.55; color: #37474f; }
    .ds-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-top: 16px;
        padding: 9px 16px;
        border-radius: 10px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #ffffff !important;
        text-decoration: none !important;
        background: linear-gradient(135deg, #0d47a1, #00838f);
        transition: filter 0.15s ease;
    }
    .ds-btn:hover { filter: brightness(1.12); }
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


with col_texto:
    html(f"""
    <div class="ds-home-title">{t("home_title")}</div>
    <div class="ds-home-subtitle">{t("home_subtitle")}</div>
    <div class="ds-divider"></div>
    """)

    st.header(t("home_welcome_header"))

    st.markdown(t("home_main_text"))

# ======================================
# BASE DE DADOS DE EXEMPLO
# ======================================
html(f"""
{section("fi-rr-database", t("home_dataset_header"))}
<div class="ds-pub ds-dataset">
    <div class="ds-pub-icon"><i class="fi fi-rr-file-csv"></i></div>
    <div>
        <div class="ds-badges"><span class="ds-badge teal">{t("home_dataset_badge")}</span></div>
        <h3>{t("home_dataset_title")}</h3>
        <p>{t("home_dataset_text")}</p>
        <div class="ds-pub-meta">
            <span><i class="fi fi-rr-calendar"></i>{t("home_dataset_years")}</span>
            <span><i class="fi fi-rr-building"></i>{t("home_dataset_publisher")}</span>
            <span><i class="fi fi-rr-license"></i>{t("home_dataset_license")}</span>
            <span><i class="fi fi-rr-refresh"></i>{t("home_dataset_update")}</span>
        </div>
        <a class="ds-btn" href="{DATASET_URL}" target="_blank" rel="noopener">{t("home_dataset_button")}<i class="fi fi-rr-arrow-up-right-from-square"></i></a>
    </div>
</div>
""")

# ======================================
# FUNDO ANIMADO (casos formando clusters)
# ======================================
st.html(
    f"<script>{Path('assets/cluster_background.js').read_text(encoding='utf-8')}</script>",
    unsafe_allow_javascript=True,
)
