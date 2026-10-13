"""Estilo das figuras do artigo: fonte Latin Modern (a do LaTeX) e mapa base cartográfico
(água, mangues, ruas e limites de bairro do OpenStreetMap), com barra de escala e seta de norte.

As geometrias ficam no sistema local em km de geocodificar.para_km; o mapa base é
desenhado com geopandas e guardado em cache em dados/mapa_base.pkl.
"""
import json
import pickle
from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import numpy as np
from matplotlib import font_manager
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize, unary_union

from geocodificar import DADOS, carregar_municipio, para_km

TEXMF_LM = Path("/opt/homebrew/Cellar/texlive/20260301/share/texmf-dist/fonts/opentype/public/lm")

# cores do mapa base: discretas, para não competir com os dados
TERRA = "#f3f2ee"
AGUA = "#c9dcea"
MANGUE = "#dfe8d8"
RUA = "#d6d3cc"
RUA_PRINCIPAL = "#c3bfb6"
LIMITE_BAIRRO = "#8f8d86"
LIMITE_MUNICIPIO = "#3f3e3b"
TINTA = "#1d1d1b"
TINTA2 = "#55534e"


def configurar_fontes():
    """Latin Modern Roman em todo o texto e Computer Modern nas fórmulas, como no LaTeX."""
    pasta = TEXMF_LM
    if not pasta.exists():
        import subprocess
        alvo = subprocess.run(["kpsewhich", "lmroman10-regular.otf"], capture_output=True, text=True).stdout.strip()
        pasta = Path(alvo).parent if alvo else pasta
    for f in ("lmroman10-regular.otf", "lmroman10-bold.otf", "lmroman10-italic.otf", "lmroman10-bolditalic.otf"):
        if (pasta / f).exists():
            font_manager.fontManager.addfont(str(pasta / f))
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Latin Modern Roman", "CMU Serif", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "axes.unicode_minus": False,
        "font.size": 9.5,
        "axes.titlesize": 9.5,
        "axes.titleweight": "normal",
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.5,
        "figure.titlesize": 10,
        "pdf.fonttype": 42,
    })


# ----------------------------------------------------------------------------- mapa base

def _km(coords):
    xs, ys = para_km([p["lon"] for p in coords], [p["lat"] for p in coords])
    return list(zip(xs, ys))


def _poligonos_relacao(el):
    linhas = [LineString(_km(m["geometry"])) for m in el.get("members", [])
              if m.get("role") in ("outer", "") and len(m.get("geometry", [])) > 1]
    return list(polygonize(unary_union(linhas))) if linhas else []


def carregar_mapa_base() -> dict:
    cache = DADOS / "mapa_base.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    municipio = carregar_municipio()
    agua, mangue, rios = [], [], []
    for el in json.loads((DADOS / "osm_agua.json").read_text())["elements"]:
        t = el.get("tags", {})
        alagado = t.get("natural") == "wetland" or t.get("water") in ("marsh", "reedbed")
        if el["type"] == "relation":
            polys = _poligonos_relacao(el)
        elif len(el.get("geometry", [])) > 3 and el["geometry"][0] == el["geometry"][-1]:
            polys = [Polygon(_km(el["geometry"]))]
        else:
            polys = []
            if t.get("waterway") in ("river", "canal", "stream") and len(el.get("geometry", [])) > 1:
                rios.append((LineString(_km(el["geometry"])), t["waterway"]))
        for p in polys:
            if p.is_valid and p.area > 0:
                (mangue if alagado else agua).append(p)
    principais = {"motorway", "trunk", "primary", "secondary", "tertiary", "motorway_link", "trunk_link", "primary_link"}
    ruas, ruas_p = [], []
    for el in json.loads((DADOS / "osm_ruas.json").read_text())["elements"]:
        if len(el.get("geometry", [])) < 2:
            continue
        (ruas_p if el["tags"].get("highway") in principais else ruas).append(LineString(_km(el["geometry"])))
    base = {
        "municipio": municipio,
        "agua": gpd.GeoSeries(agua).buffer(0),
        "mangue": gpd.GeoSeries(mangue).buffer(0),
        "rios": gpd.GeoSeries([g for g, k in rios if k in ("river", "canal")]),
        "riachos": gpd.GeoSeries([g for g, k in rios if k == "stream"]),
        "ruas": gpd.GeoSeries(ruas),
        "ruas_principais": gpd.GeoSeries(ruas_p),
    }
    cache.write_bytes(pickle.dumps(base))
    return base


def desenhar_base(ax, base, bairros=None, ruas=True, detalhe=False, terra=True):
    """Terra, mangues, água, ruas e limites. detalhe=True engrossa as ruas (recortes ampliados)."""
    mun = gpd.GeoSeries([base["municipio"]])
    if terra:
        mun.plot(ax=ax, color=TERRA, linewidth=0, zorder=0)
    base["mangue"].plot(ax=ax, color=MANGUE, linewidth=0, zorder=1)
    base["agua"].plot(ax=ax, color=AGUA, linewidth=0, zorder=1)
    base["rios"].plot(ax=ax, color=AGUA, linewidth=1.6 if detalhe else 0.9, zorder=1)
    base["riachos"].plot(ax=ax, color=AGUA, linewidth=0.6 if detalhe else 0.3, zorder=1)
    if ruas:
        base["ruas"].plot(ax=ax, color=RUA, linewidth=0.5 if detalhe else 0.15, zorder=2)
        base["ruas_principais"].plot(ax=ax, color=RUA_PRINCIPAL, linewidth=1.0 if detalhe else 0.35, zorder=2)
    if bairros is not None:
        gpd.GeoSeries([b["geom"] for b in bairros.values()]).boundary.plot(
            ax=ax, color=LIMITE_BAIRRO, linewidth=0.6 if detalhe else 0.25, zorder=4)
    mun.boundary.plot(ax=ax, color=LIMITE_MUNICIPIO, linewidth=0.7, zorder=5)
    # mapa base rasterizado no PDF (milhares de ruas); textos e dados continuam vetoriais
    for col in ax.collections:
        if col.get_zorder() <= 2:
            col.set_rasterized(True)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(False)


def enquadrar_municipio(ax, base, margem=0.4):
    x0, y0, x1, y1 = base["municipio"].bounds
    ax.set_xlim(x0 - margem, x1 + margem)
    ax.set_ylim(y0 - margem, y1 + margem)
    ax.set_xlabel("")
    ax.set_ylabel("")


def barra_escala(ax, km=2, pos=(0.62, 0.05), altura=0.012):
    """Barra de escala alternada preto/branco, no estilo de cartas topográficas."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    bx = x0 + pos[0] * (x1 - x0)
    by = y0 + pos[1] * (y1 - y0)
    h = altura * (y1 - y0)
    meio = km / 2
    ax.add_patch(mpl.patches.Rectangle((bx, by), meio, h, facecolor=TINTA, edgecolor=TINTA, linewidth=0.5, zorder=10))
    ax.add_patch(mpl.patches.Rectangle((bx + meio, by), meio, h, facecolor="white", edgecolor=TINTA, linewidth=0.5, zorder=10))
    for v, rot in [(0, "0"), (km, f"{km:g} km".replace(".", ","))]:
        ax.text(bx + v, by + 1.8 * h, rot, ha="center", va="bottom", fontsize=7, color=TINTA, zorder=10)


def seta_norte(ax, pos=(0.1, 0.88), tam=0.07):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    x = x0 + pos[0] * (x1 - x0)
    y = y0 + pos[1] * (y1 - y0)
    d = tam * (y1 - y0)
    ax.annotate("", xy=(x, y + d), xytext=(x, y), arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.6",
                                                                   color=TINTA, linewidth=0.8), zorder=10)
    ax.text(x, y + d * 1.15, "N", ha="center", va="bottom", fontsize=8, color=TINTA, zorder=10)
