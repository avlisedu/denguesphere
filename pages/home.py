import streamlit as st
from i18n import t
from ui import inject_styles, html, logo_html, chips, section, footer

STACK = ["DBSCAN", "OpenStreetMap", "Python", "Streamlit"]

inject_styles()

# ============================================================
# HERO
# ============================================================
html(f"""
<div class="ds-hero">
    {logo_html()}
    <div class="ds-hero-body">
        <span class="ds-eyebrow"><i class="fi fi-rr-microscope"></i>{t("home_eyebrow")}</span>
        <h1>{t("home_title")}</h1>
        <div class="ds-hero-sub">{t("home_subtitle")}</div>
        <p>{t("home_lead")}</p>
        <div class="ds-chips">{chips(STACK)}</div>
    </div>
</div>
""")

# ============================================================
# ATALHOS
# ============================================================
html(section("fi-rr-rocket-lunch", t("home_start_header")))

col_coords, col_cluster, col_about = st.columns(3)
with col_coords:
    st.page_link("pages/coordenadas.py", label=t("home_link_coords"), icon=":material/my_location:", width="stretch")
with col_cluster:
    st.page_link("pages/clusterizador.py", label=t("home_link_cluster"), icon=":material/hub:", width="stretch")
with col_about:
    st.page_link("pages/sobre.py", label=t("home_link_about"), icon=":material/info:", width="stretch")

# ============================================================
# COMO FUNCIONA
# ============================================================
steps = [
    ("fi-rr-file-upload", "home_step1_title", "home_step1_text", None),
    ("fi-rr-map-location-track", "home_step2_title", "home_step2_text", "home_step2_tag"),
    ("fi-rr-settings-sliders", "home_step3_title", "home_step3_text", None),
    ("fi-rr-chart-network", "home_step4_title", "home_step4_text", None),
]
step_cards = "".join(
    f"""
    <div class="ds-card ds-step">
        <span class="ds-step-num">0{number}</span>
        <div class="ds-icon"><i class="fi {icon}"></i></div>
        <h4>{t(title)}</h4>
        <p>{t(text)}</p>
        {f'<span class="ds-step-tag">{t(tag)}</span>' if tag else ""}
    </div>
    """
    for number, (icon, title, text, tag) in enumerate(steps, start=1)
)

html(f"""
{section("fi-rr-route", t("home_steps_header"))}
<div class="ds-grid ds-grid-4">{step_cards}</div>
<div class="ds-tip"><i class="fi fi-rr-bulb"></i><div>{t("home_tip")}</div></div>
""")

# ============================================================
# RODAPÉ
# ============================================================
footer(t("home_footer"))
