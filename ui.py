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
    position: relative;
    z-index: 1;
}
.ds-hero-logo { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.ds-hero-logo img { width: 170px; height: auto; display: block; pointer-events: none; filter: drop-shadow(0 8px 20px rgba(0, 0, 0, 0.25)); }
.ds-hero-logo span { color: #ffffff; font-size: 1.35rem; font-weight: 700; letter-spacing: 0.01em; }
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
/* Cada versão abre e fecha; só a atual começa aberta */
.ds-release-list { display: flex; flex-direction: column; gap: 12px; }
.ds-release summary { list-style: none; cursor: pointer; margin-bottom: 0; }
.ds-release summary::-webkit-details-marker { display: none; }
.ds-release[open] summary { margin-bottom: 12px; }
.ds-release-toggle { margin-left: auto; color: #0d47a1; transition: transform 0.2s; }
.ds-release[open] .ds-release-toggle { transform: rotate(180deg); }

/* ---------- Cabeçalho compacto (páginas de ferramenta) ---------- */
.ds-page-head {
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 26px 30px;
    border-radius: 18px;
    color: #ffffff;
    background:
        radial-gradient(circle at 90% 10%, rgba(77, 208, 225, 0.35), transparent 45%),
        linear-gradient(135deg, #0a2a66 0%, #0d47a1 55%, #00838f 100%);
}
.ds-page-head::after {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
}
.ds-page-head-icon {
    position: relative;
    z-index: 1;
    flex: 0 0 auto;
    width: 58px;
    height: 58px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.3);
}
.ds-page-head-body { position: relative; z-index: 1; }
.ds-page-head h1 { color: #ffffff !important; font-size: 1.9rem; margin: 0 0 4px 0; padding: 0; }
.ds-page-head p { color: #e3f2fd; margin: 0; font-size: 0.98rem; line-height: 1.55; max-width: 820px; }

/* ---------- Passo numerado ---------- */
.ds-step-badge {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    font-weight: 700;
    color: #ffffff;
    background: linear-gradient(135deg, #0d47a1, #00acc1);
}

/* ---------- Cards compactos ---------- */
.ds-mini { display: flex; gap: 12px; align-items: center; padding: 14px 16px; }
.ds-mini .ds-icon { width: 38px; height: 38px; font-size: 17px; margin: 0; flex: 0 0 auto; }
.ds-mini p { color: #263238; }

/* ---------- Componentes do Streamlit na paleta ---------- */
[data-testid="stMetric"] {
    background: #f7faff;
    border: 1px solid #dbe7f7;
    border-radius: 14px;
    padding: 14px 16px;
}
[data-testid="stMetricLabel"] p { color: #546e7a; font-weight: 600; }
[data-testid="stMetricValue"] { color: #0a2a66; }
[data-testid="stFileUploaderDropzone"] {
    min-height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 14px;
    padding: 28px 24px;
    background:
        radial-gradient(circle at 50% 0%, rgba(0, 172, 193, 0.10), transparent 60%),
        #f7faff;
    border: 2px dashed #90caf9;
    border-radius: 18px;
    transition: border-color 0.15s ease, background-color 0.15s ease;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: #00acc1; background-color: #eefbfd; }
/* Ícone desenhado pelo próprio app (o do Streamlit muda de lugar entre versões) */
[data-testid="stFileUploaderDropzone"]::before {
    content: "\\e42b";
    font-family: "uicons-regular-rounded";
    font-size: 28px;
    line-height: 1;
    flex: 0 0 auto;
    width: 64px;
    height: 64px;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    background: linear-gradient(135deg, #0d47a1, #00acc1);
    box-shadow: 0 8px 20px rgba(13, 71, 161, 0.2);
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 4px;
    margin: 0;
}
[data-testid="stFileUploaderDropzoneInstructions"] svg { display: none; }
/* Mesma ordem em qualquer versão: ícone, texto e depois o botão */
[data-testid="stFileUploaderDropzoneInstructions"] { order: 1; }
[data-testid="stFileUploaderDropzone"] > :not([data-testid="stFileUploaderDropzoneInstructions"]) { order: 2; }
[data-testid="stFileUploaderDropzoneInstructions"] span { font-size: 1.02rem; font-weight: 600; color: #0a2a66; }
[data-testid="stFileUploaderDropzoneInstructions"] small { color: #78909c; }
[data-testid="stFileUploaderDropzone"] button {
    border-radius: 10px;
    border-color: #90caf9;
    color: #0d47a1;
    font-weight: 600;
}

/* Depois que um arquivo é carregado, a área vira uma linha compacta (até a 1.55 o arquivo fica abaixo; a partir da 1.66, dentro, em stFileChips) */
[data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) [data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"]:has([data-testid="stFileChips"]) {
    min-height: 0;
    flex-direction: row;
    justify-content: flex-start;
    padding: 10px 16px;
}
[data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) [data-testid="stFileUploaderDropzone"]::before,
[data-testid="stFileUploaderDropzone"]:has([data-testid="stFileChips"])::before {
    width: 36px;
    height: 36px;
    font-size: 17px;
    border-radius: 10px;
    box-shadow: none;
}
[data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) [data-testid="stFileUploaderDropzoneInstructions"] {
    flex: 1 1 auto;
    align-items: flex-start;
    text-align: left;
}
[data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) [data-testid="stFileUploaderDropzoneInstructions"] span { font-size: 0.92rem; }
.ds-mini p small { color: #78909c; font-weight: 600; font-size: 0.78rem; }
.ds-mini p b { color: #0a2a66; }

/* ---------- Dica com link ---------- */
.ds-tip a { color: #006064; font-weight: 600; }
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #0d47a1, #00838f);
    border: none;
}
[data-testid="stBaseButton-primary"]:hover { filter: brightness(1.1); border: none; }
[data-testid="stProgress"] [role="progressbar"] > div > div > div { background: linear-gradient(90deg, #0d47a1, #00acc1); }

/* ---------- Cronômetro (mesma altura de um botão do Streamlit) ---------- */
.ds-timer {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    height: 2.5rem;
    box-sizing: border-box;
    padding: 0 14px 0 6px;
    border-radius: 0.5rem;
    background: #f7faff;
    border: 1px solid #dbe7f7;
    white-space: nowrap;
}
.ds-timer .fi {
    width: 28px; height: 28px;
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; color: #ffffff;
    background: linear-gradient(135deg, #0d47a1, #00acc1);
}
.ds-timer span { display: inline-flex; align-items: baseline; gap: 8px; }
.ds-timer small { font-size: 0.85rem; color: #546e7a; }
.ds-timer b {
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 1.05rem;
    color: #0a2a66;
    font-variant-numeric: tabular-nums;
}
.ds-timer.live .fi { animation: ds-tick 1s steps(2, start) infinite; }
@keyframes ds-tick { 50% { filter: brightness(1.25); } }

@media (max-width: 1100px) {
    .ds-grid-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
    .ds-hero { flex-direction: column; align-items: flex-start; padding: 28px 22px; }
    .ds-grid-4, .ds-grid-3, .ds-grid-2 { grid-template-columns: 1fr; }
    .ds-pub { flex-direction: column; }
    .ds-page-head { flex-direction: column; align-items: flex-start; padding: 22px; }
}
</style>
"""


def inject_styles():
    st.markdown(STYLES, unsafe_allow_html=True)


def html(markup: str):
    """Renderiza HTML sem indentação (o Markdown trataria linhas indentadas como código)."""
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def logo_html() -> str:
    """Logo para fundos escuros (hero): só o globo, com o nome em texto branco abaixo."""
    logo_path = Path("img/logo_dark.png")
    if not logo_path.exists():
        return ""
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    return f'<div class="ds-hero-logo"><img src="data:image/png;base64,{logo_b64}" alt=""><span>DengueSphere</span></div>'


def chips(items) -> str:
    return "".join(f'<span class="ds-chip">{item}</span>' for item in items)


def section(icon: str, title: str) -> str:
    return f'<div class="ds-section"><i class="fi {icon}"></i>{title}</div>'


def footer(text: str):
    html(f'<div class="ds-footer">{text}</div>')


def page_header(icon: str, title: str, lead: str):
    html(f"""
    <div class="ds-page-head">
        <div class="ds-page-head-icon"><i class="fi {icon}"></i></div>
        <div class="ds-page-head-body"><h1>{title}</h1><p>{lead}</p></div>
    </div>
    """)


def step(number: int, title: str) -> str:
    return f'<div class="ds-section"><span class="ds-step-badge">{number}</span>{title}</div>'


def mini_cards(items) -> str:
    """items: lista de (ícone, texto)."""
    cards = "".join(
        f'<div class="ds-card ds-mini"><div class="ds-icon"><i class="fi {icon}"></i></div><p>{text}</p></div>'
        for icon, text in items
    )
    return f'<div class="ds-grid ds-grid-{min(len(items), 4)}">{cards}</div>'


DATASET_URL = "https://dados.recife.pe.gov.br/sv/dataset/casos-de-dengue-zika-e-chikungunya"


def tip(text: str, icon: str = "fi-rr-bulb"):
    html(f'<div class="ds-tip"><i class="fi {icon}"></i><div>{text}</div></div>')
