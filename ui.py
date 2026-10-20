import base64
from pathlib import Path

import streamlit as st

# ============================================================
# ESTILO VISUAL COMPARTILHADO (paleta, hero, cards, seções, rodapé)
# ============================================================
STYLES = """
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
.ds-hero-sub { color: #b2ebf2; font-size: 1.15rem; font-weight: 600; margin: -4px 0 10px 0; }
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
.ds-grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }

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

/* ---------- Passos (Home) ---------- */
.ds-step { position: relative; }
.ds-step-num {
    position: absolute;
    top: 18px;
    right: 20px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #dbe7f7;
}
.ds-step-tag {
    display: inline-block;
    margin-top: 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 6px;
    background: #e0f7fa;
    color: #006064;
}

/* ---------- Dica ---------- */
.ds-tip {
    display: flex;
    gap: 16px;
    align-items: flex-start;
    margin-top: 24px;
    padding: 18px 22px;
    border-radius: 14px;
    background: #e0f7fa;
    border: 1px solid #b2ebf2;
    color: #004d55;
    font-size: 0.94rem;
    line-height: 1.55;
}
.ds-tip .fi { font-size: 22px; color: #00838f; padding-top: 2px; }
.ds-tip strong { color: #006064; }

/* ---------- Atalhos (st.page_link) ---------- */
[data-testid="stPageLink"] a {
    border: 1px solid #dbe7f7;
    border-radius: 12px;
    background: #f7faff;
    padding: 10px 14px;
    transition: border-color 0.15s ease, background 0.15s ease;
}
[data-testid="stPageLink"] a:hover { border-color: #90caf9; background: #e3f2fd; }
[data-testid="stPageLink"] p { color: #0d47a1; font-weight: 600; }

/* ---------- Notas de versão ---------- */
.ds-release {
    background: #ffffff;
    border: 1px solid #dbe7f7;
    border-radius: 14px;
    padding: 20px 22px;
}
.ds-release.future { background: #f7fdfe; border: 1px dashed #4dd0e1; }
.ds-release-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.ds-release-version {
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #0a2a66;
}
.ds-release ul { list-style: none; margin: 0; padding: 0; }
.ds-release li {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin: 0 0 8px 0;
    font-size: 0.92rem;
    line-height: 1.5;
    color: #37474f;
}
.ds-release li .fi { color: #2e7d32; padding-top: 3px; }
.ds-release.future li .fi { color: #00838f; }

@media (max-width: 1100px) {
    .ds-grid-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
    .ds-hero { flex-direction: column; align-items: flex-start; padding: 28px 22px; }
    .ds-grid-4, .ds-grid-3, .ds-grid-2 { grid-template-columns: 1fr; }
    .ds-pub { flex-direction: column; }
}
</style>
"""


def inject_styles():
    st.markdown(STYLES, unsafe_allow_html=True)


def html(markup: str):
    """Renderiza HTML sem indentação (o Markdown trataria linhas indentadas como código)."""
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def logo_html() -> str:
    logo_path = Path("img/logo.png")
    if not logo_path.exists():
        return ""
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    return f'<div class="ds-hero-logo"><img src="data:image/png;base64,{logo_b64}"></div>'


def chips(items) -> str:
    return "".join(f'<span class="ds-chip">{item}</span>' for item in items)


def section(icon: str, title: str) -> str:
    return f'<div class="ds-section"><i class="fi {icon}"></i>{title}</div>'


def footer(text: str):
    html(f'<div class="ds-footer">{text}</div>')
