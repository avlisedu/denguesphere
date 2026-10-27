import streamlit as st
from i18n import t
from ui import inject_styles, html, logo_html, chips, section, footer

# ============================================================
# DADOS DA PUBLICAÇÃO
# ============================================================
BIBTEX = r"""@inproceedings{Silva:DengueSphere:2026,
  title = {A Decision Support System Applied to Dengue Epidemiological Surveillance: {{The DengueSphere}} Platform},
  booktitle = {Proceedings of the 2026 International Conference on Decision Support System Technology ({{ICDSST}} 2026)},
  author = {Silva, Eduardo and Economou, Theo and Silva, Maisa Mendon{\c c}a},
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
PUB_AUTHORS = "Eduardo Silva, Theo Economou, Maisa Mendonça Silva"
PUB_VENUE = "International Conference on Decision Support System Technology (ICDSST 2026)"
PUB_PUBLISHER = "University of Plymouth, Plymouth, United Kingdom"
PUB_ISBN = "ISBN 978-1-84102-474-5"
PUB_CITATION = (
    "Silva, E., Economou, T., &amp; Silva, M. M. (2026). "
    f"{PUB_TITLE}. In <em>Proceedings of the 2026 International Conference on Decision "
    "Support System Technology (ICDSST 2026)</em> (Vol. 1, pp. 154–160). "
    "University of Plymouth."
)

STACK = ["Python", "Streamlit", "DBSCAN", "OpenStreetMap", "Folium"]


# ============================================================
# ESTILO VISUAL
# ============================================================
inject_styles()

# ============================================================
# HERO
# ============================================================
html(f"""
<div class="ds-hero">
    {logo_html()}
    <div class="ds-hero-body">
        <span class="ds-eyebrow"><i class="fi fi-rr-microscope"></i>{t("about_eyebrow")}</span>
        <h1>{t("about_title")}</h1>
        <p>{t("about_lead")}</p>
        <div class="ds-chips">{chips(STACK)}</div>
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
{section("fi-rr-diagram-project", t("about_modules_header"))}
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
{section("fi-rr-bullseye-arrow", t("about_objectives_header"))}
<div class="ds-grid ds-grid-3">{objective_cards}</div>
""")

# ============================================================
# PUBLICAÇÃO
# ============================================================
html(f"""
{section("fi-rr-book-open-cover", t("about_pub_header"))}
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
with st.expander(t("about_pub_bibtex")):
    st.code(BIBTEX, language="latex")

# ============================================================
# NOTAS DE VERSÃO
# ============================================================
def release_items(key, icon):
    items = t(key)
    if not isinstance(items, list):  # chave ausente: t() devolve o próprio nome da chave
        return ""
    return "".join(f'<li><i class="fi {icon}"></i><span>{item}</span></li>' for item in items)


html(f"""
{section("fi-rr-code-commit", t("about_releases_header"))}
<div class="ds-grid ds-grid-2">
    <div class="ds-release">
        <div class="ds-release-head">
            <span class="ds-release-version">v1.1</span>
            <span class="ds-badge">{t("about_release_current")}</span>
        </div>
        <ul>{release_items("about_release_11_items", "fi-rr-check-circle")}</ul>
    </div>
    <div class="ds-release future">
        <div class="ds-release-head">
            <span class="ds-release-version">{t("about_release_future_title")}</span>
            <span class="ds-badge teal">{t("about_release_future")}</span>
        </div>
        <ul>{release_items("about_release_future_items", "fi-rr-time-forward")}</ul>
    </div>
    <div class="ds-release">
        <div class="ds-release-head">
            <span class="ds-release-version">v1.0</span>
            <span class="ds-badge">{t("about_release_previous")}</span>
        </div>
        <ul>{release_items("about_release_10_items", "fi-rr-check-circle")}</ul>
    </div>
</div>
""")

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
{section("fi-rr-users", t("about_team_header"))}
<div class="ds-grid ds-grid-3">{team_cards}</div>
""")

# ============================================================
# RODAPÉ
# ============================================================
footer(t("about_footer"))
