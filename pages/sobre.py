import streamlit as st
import base64
from pathlib import Path
from i18n import t

# ============================================================
# DADOS DA PUBLICAÇÃO
# ============================================================
BIBTEX = r"""@inproceedings{Silva:DengueSphere:2026,
  title = {A Decision Support System Applied to Dengue Epidemiological Surveillance: {{The DengueSphere}} Platform},
  booktitle = {Proceedings of the 2026 International Conference on Decision Support System Technology ({{ICDSST}} 2026)},
  author = {Silva, Eduardo and Economou, Theo and Silva, Ma{\'i}sa Mendon{\c c}a},
  year = {2026},
  volume = {1},
  pages = {154--160},
  publisher = {University of Plymouth},
  address = {Plymouth, United Kingdom},
  urldate = {2026-06-24},
  isbn = {978-1-84102-474-5}
}
"""

PUB_TITLE = "A Decision Support System Applied to Dengue Epidemiological Surveillance: The DengueSphere Platform"
PUB_AUTHORS = "Eduardo Silva · Theo Economou · Maísa Mendonça Silva"
PUB_VENUE = "International Conference on Decision Support System Technology (ICDSST 2026)"
PUB_PUBLISHER = "University of Plymouth · Plymouth, United Kingdom"
PUB_ISBN = "ISBN 978-1-84102-474-5"
PUB_CITATION = (
    "Silva, E., Economou, T., &amp; Silva, M. M. (2026). "
    f"{PUB_TITLE}. In <em>Proceedings of the 2026 International Conference on Decision "
    "Support System Technology (ICDSST 2026)</em> (Vol. 1, pp. 154–160). "
    "University of Plymouth."
)

STACK = ["Python", "Streamlit", "DBSCAN", "OpenStreetMap", "Folium"]


def html(markup: str):
    """Renderiza HTML sem indentação (o Markdown trataria linhas indentadas como código)."""
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


# ============================================================
# ESTILO VISUAL
# ============================================================
st.markdown("""
<style>
@import url('https://cdn-uicons.flaticon.com/2.6.0/uicons-regular-rounded/css/uicons-regular-rounded.css');

.stApp { background-color: #ffffff !important; }
.block-container { padding-top: 3rem !important; padding-bottom: 2rem !important; }

.fi { display: inline-flex; line-height: 1; }

/* ---------- Hero ---------- */
.ds-hero {
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 36px;
    padding: 40px 44px;
    border-radius: 20px;
    color: #ffffff;
    background:
        radial-gradient(circle at 85% 20%, rgba(77, 208, 225, 0.35), transparent 45%),
        linear-gradient(135deg, #0a2a66 0%, #0d47a1 50%, #00838f 100%);
}
.ds-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
}
.ds-hero-logo {
    flex: 0 0 auto;
    background: #ffffff;
    border-radius: 18px;
    padding: 14px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    position: relative;
    z-index: 1;
}
.ds-hero-logo img { width: 150px; height: auto; display: block; pointer-events: none; }
.ds-hero-body { position: relative; z-index: 1; }
.ds-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #b2ebf2;
}
.ds-hero h1 {
    color: #ffffff !important;
    font-size: 2.4rem;
    margin: 6px 0 10px 0;
    padding: 0;
}
.ds-hero p { color: #e3f2fd; font-size: 1.02rem; line-height: 1.6; margin: 0 0 18px 0; max-width: 760px; }
.ds-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.ds-chip {
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 12px;
    padding: 5px 11px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.28);
    color: #ffffff;
}

/* ---------- Seções ---------- */
.ds-section {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 44px 0 16px 0;
    font-size: 1.35rem;
    font-weight: 700;
    color: #0d47a1;
}
.ds-section .fi { color: #00838f; font-size: 1.2rem; }

.ds-grid { display: grid; gap: 16px; }
.ds-grid-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.ds-grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }

.ds-card {
    background: #f7faff;
    border: 1px solid #dbe7f7;
    border-radius: 14px;
    padding: 20px;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.ds-card:hover {
    transform: translateY(-3px);
    border-color: #90caf9;
    box-shadow: 0 10px 24px rgba(13, 71, 161, 0.10);
}
.ds-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: #ffffff;
    background: linear-gradient(135deg, #0d47a1, #00acc1);
    margin-bottom: 14px;
}
.ds-card h4 { margin: 0 0 6px 0; padding: 0; font-size: 1.02rem; color: #0a2a66; }
.ds-card p { margin: 0; font-size: 0.92rem; line-height: 1.5; color: #455a64; }

/* ---------- Objetivos ---------- */
.ds-objective { display: flex; align-items: flex-start; gap: 14px; }
.ds-objective .ds-icon { margin-bottom: 0; flex: 0 0 auto; }
.ds-objective p { color: #263238; font-size: 0.95rem; padding-top: 2px; }

/* ---------- Publicação ---------- */
.ds-pub {
    display: flex;
    gap: 22px;
    padding: 26px;
    border-radius: 16px;
    background: #ffffff;
    border: 1px solid #dbe7f7;
    border-left: 5px solid #00838f;
    box-shadow: 0 6px 20px rgba(13, 71, 161, 0.06);
}
.ds-pub-icon {
    flex: 0 0 auto;
    width: 56px;
    height: 56px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    color: #00838f;
    background: #e0f7fa;
}
.ds-badges { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.ds-badge {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 6px;
    background: #e3f2fd;
    color: #0d47a1;
}
.ds-badge.teal { background: #e0f7fa; color: #006064; }
.ds-pub h3 { margin: 0 0 8px 0 !important; padding: 0 !important; font-size: 1.15rem; line-height: 1.4; color: #0a2a66 !important; }
.ds-pub-authors { font-weight: 600; color: #263238; margin-bottom: 10px; }
.ds-pub-meta { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 0.88rem; color: #546e7a; }
.ds-pub-meta span { display: inline-flex; align-items: center; gap: 6px; }
.ds-pub-cite {
    margin-top: 16px;
    padding: 12px 14px;
    border-radius: 10px;
    background: #f7faff;
    font-size: 0.88rem;
    line-height: 1.55;
    color: #37474f;
}
.ds-pub-cite small { display: block; color: #78909c; margin-bottom: 4px; }

/* ---------- Equipe ---------- */
.ds-person { display: flex; gap: 14px; align-items: flex-start; }
.ds-person .ds-icon { margin-bottom: 0; flex: 0 0 auto; border-radius: 50%; }
.ds-person a { font-size: 0.88rem; color: #0d47a1; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; margin-top: 8px; }

/* ---------- Rodapé ---------- */
.ds-footer {
    margin-top: 44px;
    padding: 16px;
    border-radius: 12px;
    background: #0a2a66;
    color: #bbdefb;
    font-size: 13px;
    text-align: center;
}

@media (max-width: 1100px) {
    .ds-grid-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
    .ds-hero { flex-direction: column; align-items: flex-start; padding: 28px 22px; }
    .ds-grid-4, .ds-grid-3 { grid-template-columns: 1fr; }
    .ds-pub { flex-direction: column; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
logo_path = Path("img/logo.png")
logo_html = ""
if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    logo_html = f'<div class="ds-hero-logo"><img src="data:image/png;base64,{logo_b64}"></div>'

chips = "".join(f'<span class="ds-chip">{name}</span>' for name in STACK)

html(f"""
<div class="ds-hero">
    {logo_html}
    <div class="ds-hero-body">
        <span class="ds-eyebrow"><i class="fi fi-rr-microscope"></i>{t("about_eyebrow")}</span>
        <h1>{t("about_title")}</h1>
        <p>{t("about_lead")}</p>
        <div class="ds-chips">{chips}</div>
    </div>
</div>
""")

# ============================================================
# MÓDULOS
# ============================================================
modules = [
    ("fi-rr-map-location-track", "about_mod_geo_title", "about_mod_geo_text"),
    ("fi-rr-chart-network", "about_mod_cluster_title", "about_mod_cluster_text"),
    ("fi-rr-globe", "about_mod_map_title", "about_mod_map_text"),
    ("fi-rr-chart-histogram", "about_mod_stats_title", "about_mod_stats_text"),
]
module_cards = "".join(
    f"""
    <div class="ds-card">
        <div class="ds-icon"><i class="fi {icon}"></i></div>
        <h4>{t(title)}</h4>
        <p>{t(text)}</p>
    </div>
    """
    for icon, title, text in modules
)

html(f"""
<div class="ds-section"><i class="fi fi-rr-diagram-project"></i>{t("about_modules_header")}</div>
<div class="ds-grid ds-grid-4">{module_cards}</div>
""")

# ============================================================
# OBJETIVOS
# ============================================================
objectives = [
    ("fi-rr-database", "about_obj_1"),
    ("fi-rr-marker-time", "about_obj_2"),
    ("fi-rr-bullseye-arrow", "about_obj_3"),
]
objective_cards = "".join(
    f"""
    <div class="ds-card ds-objective">
        <div class="ds-icon"><i class="fi {icon}"></i></div>
        <p>{t(text)}</p>
    </div>
    """
    for icon, text in objectives
)

html(f"""
<div class="ds-section"><i class="fi fi-rr-bullseye-arrow"></i>{t("about_objectives_header")}</div>
<div class="ds-grid ds-grid-3">{objective_cards}</div>
""")

# ============================================================
# PUBLICAÇÃO
# ============================================================
html(f"""
<div class="ds-section"><i class="fi fi-rr-book-open-cover"></i>{t("about_pub_header")}</div>
<div class="ds-pub">
    <div class="ds-pub-icon"><i class="fi fi-rr-document"></i></div>
    <div>
        <div class="ds-badges">
            <span class="ds-badge">ICDSST 2026</span>
            <span class="ds-badge teal">{t("about_pub_badge")}</span>
        </div>
        <h3>{PUB_TITLE}</h3>
        <div class="ds-pub-authors">{PUB_AUTHORS}</div>
        <div class="ds-pub-meta">
            <span><i class="fi fi-rr-calendar"></i>{t("about_pub_published")} {PUB_VENUE}</span>
            <span><i class="fi fi-rr-books"></i>{t("about_pub_pages")}</span>
            <span><i class="fi fi-rr-building"></i>{PUB_PUBLISHER}</span>
            <span><i class="fi fi-rr-hastag"></i>{PUB_ISBN}</span>
        </div>
        <div class="ds-pub-cite">
            <small><i class="fi fi-rr-quote-right"></i> {t("about_pub_cite_hint")}</small>
            {PUB_CITATION}
        </div>
    </div>
</div>
""")

st.write("")
col_bib, col_download = st.columns([4, 1], vertical_alignment="top")
with col_bib:
    with st.expander(t("about_pub_bibtex")):
        st.code(BIBTEX, language="latex")
with col_download:
    st.download_button(
        t("about_pub_download"),
        data=BIBTEX,
        file_name="Silva_DengueSphere_2026.bib",
        mime="application/x-bibtex",
        icon=":material/download:",
        width="stretch",
    )

# ============================================================
# EQUIPE
# ============================================================
team = [
    ("fi-rr-graduation-cap", "Eduardo da Silva", t("about_team_eduardo_role"), "eduardo.es@ufpe.br"),
    ("fi-rr-chalkboard-user", t("about_team_maisa_name"), t("about_team_maisa_role"), None),
    ("fi-rr-users", t("about_team_gpsid_name"), t("about_team_gpsid_role"), None),
]
team_cards = "".join(
    f"""
    <div class="ds-card ds-person">
        <div class="ds-icon"><i class="fi {icon}"></i></div>
        <div>
            <h4>{name}</h4>
            <p>{role}</p>
            {f'<a href="mailto:{email}"><i class="fi fi-rr-envelope"></i>{email}</a>' if email else ""}
        </div>
    </div>
    """
    for icon, name, role, email in team
)

html(f"""
<div class="ds-section"><i class="fi fi-rr-users"></i>{t("about_team_header")}</div>
<div class="ds-grid ds-grid-3">{team_cards}</div>
""")

# ============================================================
# RODAPÉ
# ============================================================
html(f'<div class="ds-footer">{t("about_footer")}</div>')
