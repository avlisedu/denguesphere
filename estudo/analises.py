"""Estudo numérico retrospectivo do DengueSphere com casos de dengue do Recife (2013–2025).

Usa diretamente o módulo de clusterização do software (ml-service/app/services/clustering.py).
Saídas em estudo/resultados/ (tabelas .csv) e estudo/figuras/ (.png e .pdf).

  python analises.py            # tudo
  python analises.py prospectiva  # só uma etapa
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
from sklearn.metrics import adjusted_rand_score, silhouette_score

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ.parent / "ml-service"))
from app.services.clustering import executar_clusterizacao, stability_analysis  # noqa: E402

from carregar import carregar_todos  # noqa: E402
from geocodificar import DADOS, GeocodificadorLocal, carregar_municipio, para_km  # noqa: E402

RES = RAIZ / "resultados"
FIG = RAIZ / "figuras"
NIVEL_RUA = ["rua_bairro", "rua_vizinha", "rua_cidade"]
TREINO = range(2013, 2020)  # escolha de parâmetros; 2020–2025 = teste
CELULA_KM = 0.1
JANELA = 4      # semanas de dados usadas pelo DBSCAN
HORIZONTE = 4   # semanas futuras avaliadas
MIN_CASOS = 30
RNG = np.random.default_rng(42)
POP_MIN_BAIRRO = 1000   # evita taxas explosivas em bairros quase sem moradores (ex.: Bairro do Recife)
IBGE_SETORES = DADOS / "ibge" / "PE_setores_CD2022.gpkg"
POP_RECIFE_2022 = 1_488_924  # soma de v0001 nos setores do Recife (Censo 2022)

GRADE_EPS = [0.1, 0.2, 0.3, 0.5, 0.75, 1.0]
GRADE_MINPTS = [3, 5, 10, 15, 20]
GRADE_PROSP = [(e, m) for e in (0.2, 0.3, 0.5, 0.75) for m in (3, 5, 10)]
NIVEIS = [(0, 100, "baixa (<100 casos/4 sem)"), (100, 400, "média (100–400)"), (400, np.inf, "alta (>400)")]
ALERTA_MIN = 0.8  # fração mínima de janelas em que a configuração sinaliza ao menos um cluster

AZUL, LARANJA, AGUA = "#2a78d6", "#eb6834", "#1baf7a"
CINZA, TINTA, TINTA2 = "#d6d5d0", "#0b0b0b", "#52514e"


# ----------------------------------------------------------------------------- dados

def carregar_geo(apenas_confirmados=True, nivel_rua=True) -> pd.DataFrame:
    g = pd.read_csv(DADOS / "casos_geocodificados.csv.gz", parse_dates=["data"], low_memory=False)
    if apenas_confirmados:
        g = g[g["confirmado"]]
    if nivel_rua:
        g = g[g["tipo_match"].isin(NIVEL_RUA)]
    g = g.dropna(subset=["latitude", "longitude"]).copy()
    g["x"], g["y"] = para_km(g["longitude"].to_numpy(), g["latitude"].to_numpy())
    g["semana"] = (g["data"] - pd.to_timedelta(g["data"].dt.weekday, unit="D")).dt.normalize()
    return g.reset_index(drop=True)


def janelas(g: pd.DataFrame, passo: int):
    """Gera (semana_final, casos_passados, casos_futuros) com JANELA semanas de dados."""
    semanas = pd.date_range(g["semana"].min(), g["semana"].max(), freq="7D")
    for i in range(JANELA - 1, len(semanas) - HORIZONTE, passo):
        ini, fim = semanas[i - JANELA + 1], semanas[i]
        passado = g[(g["semana"] >= ini) & (g["semana"] <= fim)]
        futuro = g[(g["semana"] > fim) & (g["semana"] <= semanas[i + HORIZONTE])]
        yield fim, passado, futuro


def nivel(n: int) -> str:
    return next(r for a, b, r in NIVEIS if a <= n < b)


def silhueta(df: pd.DataFrame) -> float:
    c = df[df["cluster"] != -1]
    if c["cluster"].nunique() < 2 or len(c) < 3:
        return np.nan
    n = min(len(c), 2000)
    return silhouette_score(np.radians(c[["latitude", "longitude"]]), c["cluster"], metric="haversine",
                            sample_size=n, random_state=0)


def salvar(fig, nome):
    """Só PDF (o formato incluído no LaTeX); camadas rasterizadas saem a 300 dpi."""
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{nome}.pdf", bbox_inches="tight", dpi=300)


def br(v) -> str:
    """Rótulo com vírgula decimal (figuras em português)."""
    return str(v).replace(".", ",")


def estilo():
    import locale
    import matplotlib.pyplot as plt
    for loc in ("pt_BR.UTF-8", "pt_BR"):
        try:
            locale.setlocale(locale.LC_NUMERIC, loc)
            break
        except locale.Error:
            pass
    from cartografia import configurar_fontes
    configurar_fontes()
    plt.rcParams.update({
        "axes.formatter.use_locale": True,
        "axes.edgecolor": CINZA, "axes.labelcolor": TINTA2, "xtick.color": TINTA2,
        "ytick.color": TINTA2, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#ecebe7", "grid.linewidth": 0.6, "axes.axisbelow": True,
        "axes.titlecolor": TINTA, "legend.frameon": False,
    })
    return plt


# ----------------------------------------------------------------------------- 1. descritiva

def descritiva():
    plt = estilo()
    todos = carregar_todos()
    todos = todos[todos["recife"] & todos["data"].notna() & todos["ano_epi"].between(2013, 2025)]
    rotulo = {1: "1 Dengue clássico", 2: "2 Dengue c/ complicações", 3: "3 FHD", 4: "4 SCD", 5: "5 Descartado",
              8: "8 Inconclusivo", 10: "10 Dengue", 11: "11 Dengue c/ sinais de alarme", 12: "12 Dengue grave"}
    classif = (todos.assign(classe=todos["tp_classificacao_final"].map(rotulo).fillna("Sem classificação"))
               .pivot_table(index="ano_epi", columns="classe", values="recife", aggfunc="size", fill_value=0))
    classif.to_csv(RES / "tab_classificacao_por_ano.csv")

    geo = pd.read_csv(DADOS / "casos_geocodificados.csv.gz", parse_dates=["data"], low_memory=False)
    conf = geo[geo["confirmado"] & geo["ano_epi"].between(2013, 2025)].copy()
    conf["semana"] = (conf["data"] - pd.to_timedelta(conf["data"].dt.weekday, unit="D")).dt.normalize()
    semanal = conf.groupby("semana").size()
    semanal = semanal.reindex(pd.date_range(semanal.index.min(), semanal.index.max(), freq="7D"), fill_value=0).astype(float)
    # sequências de 8+ semanas sem nenhum caso = período sem dados (o arquivo de 2014 termina em julho)
    zero = semanal.eq(0)
    run = zero.groupby((~zero).cumsum()).transform("sum")
    semanal[zero & (run >= 8)] = np.nan
    tipo = conf.groupby("ano_epi")["tipo_match"].value_counts(normalize=True).unstack(fill_value=0) * 100
    pico = conf.groupby(["ano_epi", "semana_epi"]).size()
    anual = pd.DataFrame({
        "notificados": todos.groupby("ano_epi").size(),
        "confirmados": conf.groupby("ano_epi").size(),
        "pct_nivel_rua": tipo[NIVEL_RUA].sum(axis=1),
        "pct_centroide_bairro": tipo["bairro"],
        "pct_nao_encontrado": tipo.get("nao_encontrado", 0),
        "incidencia_100mil": conf.groupby("ano_epi").size() / POP_RECIFE_2022 * 1e5,
        "pico_semanal": pico.groupby("ano_epi").max(),
        "se_pico": pico.groupby("ano_epi").idxmax().map(lambda t: t[1]),
    }).round(1)
    anual.loc["Total"] = [anual["notificados"].sum(), anual["confirmados"].sum(),
                          (conf["tipo_match"].isin(NIVEL_RUA).mean() * 100).round(1),
                          ((conf["tipo_match"] == "bairro").mean() * 100).round(1),
                          ((conf["tipo_match"] == "nao_encontrado").mean() * 100).round(1),
                          round(len(conf) / POP_RECIFE_2022 * 1e5 / conf["ano_epi"].nunique(), 1), np.nan, np.nan]
    anual.to_csv(RES / "tab1_casos_por_ano.csv")
    print(anual.to_string())

    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.fill_between(semanal.index, semanal.values, color=AZUL, alpha=0.15, linewidth=0)
    ax.plot(semanal.index, semanal.values, color=AZUL, linewidth=1.2)
    ax.set_ylabel("Casos confirmados por semana")
    ax.set_xlim(semanal.index.min(), semanal.index.max())
    lacuna = semanal.index[semanal.isna()]
    if len(lacuna):
        ax.axvspan(lacuna.min(), lacuna.max(), color="#f2f1ed", zorder=0)
        ax.text(lacuna.min() + (lacuna.max() - lacuna.min()) / 2, ax.get_ylim()[1] * 0.92, "sem\ndados",
                ha="center", va="top", fontsize=7, color=TINTA2)
    ax.set_ylim(0)
    salvar(fig, "fig1_curva_epidemica")
    plt.close(fig)

    # qualidade da geocodificação por ano
    cats = {"Rua no bairro informado": ["rua_bairro"], "Rua em bairro vizinho / cidade": ["rua_vizinha", "rua_cidade"],
            "Centroide do bairro / não encontrado": ["bairro", "nao_encontrado"]}
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    base = np.zeros(len(tipo))
    for (nome, cols), cor in zip(cats.items(), (AZUL, LARANJA, AGUA)):
        v = tipo.reindex(columns=cols, fill_value=0).sum(axis=1).to_numpy()
        ax.bar(tipo.index, v, bottom=base, color=cor, width=0.75, label=nome, edgecolor="white", linewidth=1)
        base += v
    ax.set_ylabel("% dos casos confirmados")
    ax.set_ylim(0, 100)
    ax.set_xticks(tipo.index)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=8)
    salvar(fig, "fig2_geocodificacao")
    plt.close(fig)


# ----------------------------------------------------------------------------- 2. sensibilidade

def sensibilidade():
    plt = estilo()
    g = carregar_geo()
    linhas = []
    for fim, passado, _ in janelas(g, passo=JANELA):
        if len(passado) < MIN_CASOS:
            continue
        for eps in GRADE_EPS:
            for m in GRADE_MINPTS:
                d = executar_clusterizacao(passado, eps, m)
                rot = d["cluster"]
                n_cl = int(rot.max() + 1)
                tam = rot[rot >= 0].value_counts()
                linhas.append({
                    "semana_final": fim, "ano": fim.isocalendar().year, "n": len(d), "nivel": nivel(len(d)),
                    "eps_km": eps, "min_samples": m,
                    "n_clusters": n_cl, "pct_ruido": (rot == -1).mean() * 100,
                    "pct_maior_cluster": tam.max() / len(d) * 100 if n_cl else 0,
                    "silhueta": silhueta(d) if n_cl >= 2 else np.nan,
                })
    df = pd.DataFrame(linhas)
    df.to_csv(RES / "sensibilidade_janelas.csv", index=False)

    def q(s):
        return f"{s.median():.2f} [{s.quantile(.25):.2f}–{s.quantile(.75):.2f}]"
    tab = df.groupby(["eps_km", "min_samples"]).agg(
        janelas=("n", "size"), n_clusters=("n_clusters", q), pct_ruido=("pct_ruido", q),
        pct_maior_cluster=("pct_maior_cluster", q), silhueta=("silhueta", q))
    tab.to_csv(RES / "tab2_sensibilidade_parametros.csv")
    tab_n = df.groupby(["nivel", "eps_km", "min_samples"]).agg(
        janelas=("n", "size"), n_clusters=("n_clusters", q), pct_ruido=("pct_ruido", q),
        pct_maior_cluster=("pct_maior_cluster", q), silhueta=("silhueta", q),
        pct_janelas_com_cluster=("n_clusters", lambda s: (s > 0).mean() * 100))
    tab_n.to_csv(RES / "tab2b_sensibilidade_por_nivel.csv")
    print(tab_n.to_string())

    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6))
    for ax, (_, _, rot) in zip(axs, NIVEIS):
        sub = df[df["nivel"] == rot]
        m = sub.groupby(["min_samples", "eps_km"])["n_clusters"].median().unstack("eps_km")
        curto = rot.split(" (")[0].capitalize() + " (" + rot.split(" (")[1].replace(" casos/4 sem", "")
        titulo, fmt = f"{curto}\n{sub['semana_final'].nunique()} janelas", "{:.0f}"
        ax.imshow(m.values, cmap="Blues", aspect="auto", origin="lower")
        ax.grid(False)
        ax.set_xticks(range(len(m.columns)), [br(f"{e:g}") for e in m.columns])
        ax.set_yticks(range(len(m.index)), m.index)
        ax.set_xlabel("$\\varepsilon$ (km)")
        ax.set_title(titulo, loc="left", fontsize=9)
        vmin, vmax = np.nanmin(m.values), np.nanmax(m.values)
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                v = m.values[i, j]
                if np.isfinite(v):
                    claro = (v - vmin) / max(vmax - vmin, 1e-9) < 0.55
                    ax.text(j, i, br(fmt.format(v)), ha="center", va="center", fontsize=6.5, color=TINTA if claro else "white")
    axs[0].set_ylabel("min_samples")
    fig.tight_layout()
    salvar(fig, "fig3_sensibilidade")
    plt.close(fig)


# ----------------------------------------------------------------------------- 3. estabilidade

def estabilidade(n_boot=10):
    g = carregar_geo()
    linhas = []
    for fim, passado, _ in janelas(g, passo=JANELA):
        if len(passado) < MIN_CASOS:
            continue
        for eps, m in GRADE_PROSP:
            base = passado.reset_index(drop=True)
            ref = executar_clusterizacao(base, eps, m)["cluster"].to_numpy()
            if ref.max() < 0:
                continue  # sem clusters: ARI seria 1 trivialmente (tudo ruído)
            info = {"semana_final": fim, "nivel": nivel(len(base)), "eps_km": eps, "min_samples": m}
            for r in stability_analysis(base, eps, m):
                linhas.append({**info, "perturbacao": f"{r['parametro']} {r['variacao']}", "ari": r["ari"]})
            for _ in range(n_boot):
                idx = np.sort(RNG.choice(len(base), size=int(0.9 * len(base)), replace=False))
                lab = executar_clusterizacao(base.iloc[idx], eps, m)["cluster"].to_numpy()
                linhas.append({**info, "perturbacao": "subamostra 90%", "ari": adjusted_rand_score(ref[idx], lab)})
    df = pd.DataFrame(linhas)
    df.to_csv(RES / "estabilidade_janelas.csv", index=False)
    tab = (df.groupby(["eps_km", "min_samples", "perturbacao"])["ari"]
           .agg(mediana="median", p25=lambda s: s.quantile(.25), p75=lambda s: s.quantile(.75), media="mean")
           .round(3).unstack("perturbacao"))
    tab.to_csv(RES / "tab3_estabilidade_ari.csv")
    print(tab.xs("mediana", axis=1, level=0).to_string())
    tab_n = df.groupby(["nivel", "perturbacao"])["ari"].median().round(3).unstack("perturbacao")
    tab_n.to_csv(RES / "tab3b_estabilidade_por_nivel.csv")
    print(tab_n.to_string())


# ----------------------------------------------------------------------------- 4. validação prospectiva

def populacao_grade(grade) -> np.ndarray:
    """População do Censo 2022 por célula da grade, por ponderação areal dos setores censitários
    (cada setor reparte sua população entre as células na proporção da área de interseção)."""
    cache = DADOS / f"pop_grade_{grade.nx}x{grade.ny}.npy"
    if cache.exists():
        return np.load(cache)
    import geopandas as gpd
    import shapely
    from shapely.geometry import box
    setores = gpd.read_file(IBGE_SETORES, where="CD_MUN='2611606'")
    setores["pop"] = pd.to_numeric(setores["v0001"], errors="coerce").fillna(0)
    celulas = shapely.box(grade.cx.ravel() - CELULA_KM / 2, grade.cy.ravel() - CELULA_KM / 2,
                          grade.cx.ravel() + CELULA_KM / 2, grade.cy.ravel() + CELULA_KM / 2)
    arvore = shapely.STRtree(celulas)
    pop = np.zeros(grade.cx.size)
    for geom, p in zip(setores.geometry, setores["pop"]):
        if p <= 0 or geom is None:
            continue
        geom = shapely.transform(geom, lambda c: np.c_[para_km(c[:, 0], c[:, 1])])
        idx = arvore.query(geom, predicate="intersects")
        frac = shapely.area(shapely.intersection(celulas[idx], geom)) / geom.area
        pop[idx] += p * frac
    np.save(cache, pop)
    return pop


class Grade:
    """Grade regular de CELULA_KM sobre o município, para medir áreas e capturas."""

    def __init__(self):
        geo = GeocodificadorLocal()
        self.bairros = geo.bairros
        municipio = carregar_municipio()
        self.municipio = municipio
        self.area_cidade = municipio.area
        x0, y0, x1, y1 = municipio.bounds
        self.x0, self.y0 = x0, y0
        self.nx, self.ny = int(np.ceil((x1 - x0) / CELULA_KM)), int(np.ceil((y1 - y0) / CELULA_KM))
        cx = x0 + (np.arange(self.nx) + 0.5) * CELULA_KM
        cy = y0 + (np.arange(self.ny) + 0.5) * CELULA_KM
        self.cx, self.cy = np.meshgrid(cx, cy, indexing="ij")
        self.arvore = cKDTree(np.c_[self.cx.ravel(), self.cy.ravel()])
        from shapely import contains_xy
        self.bairro_celula = np.full(self.cx.size, -1)
        self.nomes_bairros = list(self.bairros)
        for k, b in enumerate(self.nomes_bairros):
            dentro = contains_xy(self.bairros[b]["geom"], self.cx.ravel(), self.cy.ravel())
            self.bairro_celula[dentro] = k
        self.dentro = self.bairro_celula >= 0
        self.pop = populacao_grade(self)
        self.pop_bairro = np.bincount(self.bairro_celula[self.dentro], weights=self.pop[self.dentro],
                                      minlength=len(self.nomes_bairros))
        self.pop_total = self.pop.sum()

    def pop_topk(self, k):
        """Referência sem casos: as k células mais populosas."""
        p = np.where(self.dentro, self.pop, -1)
        mask = np.zeros(self.cx.size, bool)
        mask[np.argsort(-p, kind="stable")[:k]] = True
        return mask

    def celulas(self, x, y):
        i = np.clip(((np.asarray(x) - self.x0) / CELULA_KM).astype(int), 0, self.nx - 1)
        j = np.clip(((np.asarray(y) - self.y0) / CELULA_KM).astype(int), 0, self.ny - 1)
        return i * self.ny + j

    def buffer(self, x, y, raio):
        mask = np.zeros(self.cx.size, bool)
        if len(x):
            pts = np.unique(np.c_[x, y].round(4), axis=0)
            for viz in self.arvore.query_ball_point(pts, r=raio):
                mask[viz] = True
        return mask & self.dentro

    def contagem(self, x, y):
        return np.bincount(self.celulas(x, y), minlength=self.cx.size).astype(float)

    def kde_topk(self, x, y, sigma_km, k):
        dens = gaussian_filter(self.contagem(x, y).reshape(self.nx, self.ny), sigma=sigma_km / CELULA_KM).ravel()
        dens[~self.dentro] = -1
        mask = np.zeros(self.cx.size, bool)
        mask[np.argsort(-dens)[:k]] = True
        return mask

    def bairros_topk(self, x, y, k):
        """Bairros inteiros, em ordem decrescente de incidência (casos/habitante) na janela."""
        cont = np.bincount(self.bairro_celula[self.celulas(x, y)] + 1, minlength=len(self.nomes_bairros) + 1)[1:]
        ordem = np.argsort(-(cont / np.maximum(self.pop_bairro, POP_MIN_BAIRRO)))
        mask = np.zeros(self.cx.size, bool)
        for b in ordem:
            if mask.sum() >= k or cont[b] == 0:
                break
            mask |= self.bairro_celula == b
        return mask


def avaliar(grade, mask, futuro_cel):
    """Captura, % da área, PAI (área), % da população e PAI populacional (captura ÷ % da população)."""
    area = mask.sum() * CELULA_KM ** 2
    if area == 0 or len(futuro_cel) == 0:
        return {"captura_pct": np.nan, "area_pct": 0.0, "pai": np.nan, "pop_pct": 0.0, "pai_pop": np.nan}
    captura = mask[futuro_cel].mean()
    frac_area = area / grade.area_cidade
    frac_pop = grade.pop[mask].sum() / grade.pop_total
    return {"captura_pct": captura * 100, "area_pct": frac_area * 100, "pai": captura / frac_area,
            "pop_pct": frac_pop * 100, "pai_pop": captura / frac_pop if frac_pop > 0 else np.nan}


def prospectiva_variante(grade, g, nome, configs):
    linhas = []
    for fim, passado, futuro in janelas(g, passo=1):
        if len(passado) < MIN_CASOS or len(futuro) < MIN_CASOS:
            continue
        fut = grade.celulas(futuro["x"], futuro["y"])
        for eps, m in configs:
            d = executar_clusterizacao(passado, eps, m)
            cl = d[d["cluster"] != -1]
            hot = grade.buffer(cl["x"], cl["y"], eps)
            k = int(hot.sum())
            info = {"variante": nome, "semana_final": fim, "ano": fim.isocalendar().year,
                    "conjunto": "treino" if fim.isocalendar().year in TREINO else "teste",
                    "nivel": nivel(len(passado)), "eps_km": eps, "min_samples": m, "n_passado": len(passado),
                    "n_futuro": len(futuro), "n_clusters": int(d["cluster"].max() + 1), "sinalizou": k > 0}
            if k == 0:
                linhas.append({**info, "metodo": "DBSCAN (DengueSphere)", "captura_pct": 0.0, "area_pct": 0.0, "pai": np.nan,
                               "pop_pct": 0.0, "pai_pop": np.nan})
                continue
            metodos = {
                "DBSCAN (DengueSphere)": hot,
                "KDE (mesma área)": grade.kde_topk(passado["x"], passado["y"], eps, k),
                "Ranking de bairros": grade.bairros_topk(passado["x"], passado["y"], k),
                "População (mesma área)": grade.pop_topk(k),
                "Todos os casos (sem clusterizar)": grade.buffer(passado["x"], passado["y"], eps),
            }
            for metodo, mask in metodos.items():
                linhas.append({**info, "metodo": metodo, **avaliar(grade, mask, fut)})
    return pd.DataFrame(linhas)


def prospectiva():
    plt = estilo()
    grade = Grade()
    print(f"área do município (polígonos OSM): {grade.area_cidade:.1f} km²")
    principal = prospectiva_variante(grade, carregar_geo(), "confirmados, nível de rua", GRADE_PROSP)
    principal.to_csv(RES / "prospectiva_janelas.csv", index=False)

    # escolha do parâmetro no treino (2013–2019): maior PAI mediano do DBSCAN entre as configurações
    # que sinalizam algum cluster em >= ALERTA_MIN das janelas (evita premiar quem quase nunca alerta)
    db = principal[principal["metodo"].str.startswith("DBSCAN")]

    def escolher(sub):
        r = sub.groupby(["eps_km", "min_samples"]).agg(alerta=("sinalizou", "mean"), pai=("pai", "median"))
        ok = r[r["alerta"] >= ALERTA_MIN]
        return (ok if len(ok) else r.sort_values("alerta", ascending=False).head(1))["pai"].idxmax()

    escolha = escolher(db[db["conjunto"] == "treino"])
    print("parâmetros escolhidos no treino:", escolha)

    # guia de parâmetros por nível de incidência: escolhido no treino, avaliado no teste
    guia = []
    for _, _, rot in NIVEIS:
        tr = db[(db["conjunto"] == "treino") & (db["nivel"] == rot)]
        if tr.empty:
            continue
        e, m = escolher(tr)
        for conj in ("treino", "teste"):
            sub = principal[(principal["conjunto"] == conj) & (principal["nivel"] == rot) &
                            (principal["eps_km"] == e) & (principal["min_samples"] == m)]
            for metodo, s2 in sub.groupby("metodo"):
                guia.append({"nivel": rot, "eps_km": e, "min_samples": m, "conjunto": conj, "metodo": metodo,
                             "janelas": s2["semana_final"].nunique(),
                             "pct_janelas_com_alerta": s2["sinalizou"].mean() * 100 if metodo.startswith("DBSCAN") else np.nan,
                             "captura_med": s2["captura_pct"].median(), "area_med": s2["area_pct"].median(),
                             "pai_med": s2["pai"].median(), "pop_med": s2["pop_pct"].median(),
                             "pai_pop_med": s2["pai_pop"].median()})
    guia = pd.DataFrame(guia).round(2)
    guia.to_csv(RES / "tab4b_guia_parametros_por_nivel.csv", index=False)
    print(guia.to_string())

    def resumo(df):
        return df.groupby(["conjunto", "metodo"]).agg(
            janelas=("pai", "size"), pct_alerta=("sinalizou", lambda s: s.mean() * 100), captura_med=("captura_pct", "median"), area_med=("area_pct", "median"),
            pai_med=("pai", "median"), pai_p25=("pai", lambda s: s.quantile(.25)), pai_p75=("pai", lambda s: s.quantile(.75)),
            pop_med=("pop_pct", "median"), pai_pop_med=("pai_pop", "median"),
            pai_pop_p25=("pai_pop", lambda s: s.quantile(.25)), pai_pop_p75=("pai_pop", lambda s: s.quantile(.75))
        ).round(2)

    grade_tab = db.groupby(["conjunto", "eps_km", "min_samples"]).agg(
        pct_janelas_com_alerta=("sinalizou", lambda s: s.mean() * 100), captura_med=("captura_pct", "median"),
        area_med=("area_pct", "median"), pai_med=("pai", "median"), pop_med=("pop_pct", "median"),
        pai_pop_med=("pai_pop", "median")).round(2)
    grade_tab.to_csv(RES / "tab4a_prospectiva_grade_dbscan.csv")

    sel = principal[(principal["eps_km"] == escolha[0]) & (principal["min_samples"] == escolha[1])]
    tab = resumo(sel)
    tab.to_csv(RES / "tab4_prospectiva_comparacao.csv")
    print(tab.to_string())

    # vitória pareada do DBSCAN sobre cada referência, por janela (teste)
    from scipy.stats import wilcoxon
    pares = []
    for metrica in ("pai", "pai_pop"):
        piv = sel[sel["conjunto"] == "teste"].pivot_table(index="semana_final", columns="metodo", values=metrica)
        for ref in [c for c in piv.columns if not c.startswith("DBSCAN")]:
            a, b = piv["DBSCAN (DengueSphere)"], piv[ref]
            ok = a.notna() & b.notna()
            stat = wilcoxon(a[ok], b[ok])
            pares.append({"metrica": metrica, "referencia": ref, "janelas": int(ok.sum()),
                          "pct_janelas_dbscan_melhor": (a[ok] > b[ok]).mean() * 100,
                          "dif_mediana": (a[ok] - b[ok]).median(), "wilcoxon_p": stat.pvalue})
    pares = pd.DataFrame(pares).round(4)
    pares.to_csv(RES / "tab5_prospectiva_pareada_teste.csv", index=False)
    print(pares.to_string())

    # sensibilidade: casos não descartados (o que se tem em tempo real) e inclusão de centroides de bairro
    variantes = [
        prospectiva_variante(grade, carregar_geo(apenas_confirmados=False), "não descartados, nível de rua", [escolha]),
        prospectiva_variante(grade, carregar_geo(nivel_rua=False), "confirmados, incl. centroide de bairro", [escolha]),
    ]
    sens = pd.concat([sel] + variantes)
    sens.to_csv(RES / "prospectiva_variantes_janelas.csv", index=False)
    tab_s = sens.groupby(["variante", "metodo"]).agg(
        janelas=("pai", "size"), pct_alerta=("sinalizou", lambda s: s.mean() * 100),
        captura_med=("captura_pct", "median"), area_med=("area_pct", "median"), pai_med=("pai", "median"),
        pai_pop_med=("pai_pop", "median")).round(2)
    tab_s.to_csv(RES / "tab6_prospectiva_sensibilidade.csv")
    print(tab_s.to_string())

    # figura: PAI por método (teste)
    ordem = ["DBSCAN (DengueSphere)", "KDE (mesma área)", "Ranking de bairros", "População (mesma área)",
             "Todos os casos (sem clusterizar)"]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, (metrica, rotulo) in zip(axs, [("pai", "PAI por área"), ("pai_pop", "PAI por população")]):
        dados = [sel[(sel["conjunto"] == "teste") & (sel["metodo"] == mt)][metrica].dropna() for mt in ordem]
        bp = ax.boxplot(dados, orientation="horizontal", widths=0.55, patch_artist=True, showfliers=False,
                        medianprops={"color": TINTA, "linewidth": 1.2}, whiskerprops={"color": TINTA2},
                        capprops={"color": TINTA2})
        for patch, mt in zip(bp["boxes"], ordem):
            patch.set_facecolor(AZUL if mt.startswith("DBSCAN") else CINZA)
            patch.set_edgecolor("white")
        ax.axvline(1, color=TINTA2, linewidth=0.8, linestyle=":")
        ax.set_title("(a) por área" if metrica == "pai" else "(b) por população", loc="left")
        ax.set_xlabel(rotulo)
    axs[0].set_yticks(range(1, len(ordem) + 1), [m.replace("Ranking de bairros", "Ranking de bairros (incidência)") for m in ordem])
    axs[0].invert_yaxis()
    fig.tight_layout()
    salvar(fig, "fig4_pai_metodos")
    plt.close(fig)

    # figura: série temporal de captura
    s = sel.pivot_table(index="semana_final", columns="metodo", values="captura_pct").asfreq("7D")  # lacunas viram NaN
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    for mt, cor in [("DBSCAN (DengueSphere)", AZUL), ("KDE (mesma área)", LARANJA), ("Ranking de bairros", AGUA)]:
        ax.plot(s.index, s[mt].rolling(4, min_periods=3).mean(), color=cor, linewidth=1.2,
                label=mt.replace("Ranking de bairros", "Ranking de bairros (incidência)"))
    ax.set_ylabel("% dos casos futuros capturados")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=8)
    ax.set_ylim(0)
    salvar(fig, "fig5_captura_temporal")
    plt.close(fig)

    alta = guia[guia["nivel"].str.startswith("alta")]
    mapa_exemplo(grade, (float(alta["eps_km"].iloc[0]), int(alta["min_samples"].iloc[0])) if len(alta) else escolha)
    return escolha


def mapa_exemplo(grade, escolha):
    plt = estilo()
    import geopandas as gpd
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from shapely.ops import unary_union
    from cartografia import barra_escala, carregar_mapa_base, desenhar_base, enquadrar_municipio, seta_norte
    base = carregar_mapa_base()
    g = carregar_geo()
    eps, m = escolha
    # janela com mais casos em 2015 (maior epidemia)
    fim, passado, futuro = max((j for j in janelas(g, passo=1) if j[0].year == 2015), key=lambda j: len(j[1]))
    d = executar_clusterizacao(passado, eps, m)
    ruido, cl = d[d["cluster"] == -1], d[d["cluster"] != -1]
    hot = grade.buffer(cl["x"], cl["y"], eps)
    fut = grade.celulas(futuro["x"], futuro["y"])
    dentro = hot[fut]
    area = hot.sum() * CELULA_KM ** 2 / grade.area_cidade * 100
    pts = np.unique(np.c_[cl["x"], cl["y"]].round(4), axis=0)
    zona = unary_union(gpd.points_from_xy(pts[:, 0], pts[:, 1]).buffer(eps, resolution=12)).intersection(grade.municipio)

    fig, axs = plt.subplots(1, 2, figsize=(7.2, 5.0))
    for ax in axs:
        desenhar_base(ax, base, grade.bairros)
        enquadrar_municipio(ax, base, margem=0.2)
    axs[0].scatter(ruido["x"], ruido["y"], s=1.5, color="#8f8d86", linewidths=0, zorder=6)
    axs[0].scatter(cl["x"], cl["y"], s=2.5, color=AZUL, linewidths=0, zorder=7)
    gpd.GeoSeries([zona]).plot(ax=axs[1], color=AZUL, alpha=0.22, linewidth=0, zorder=5)
    gpd.GeoSeries([zona]).boundary.plot(ax=axs[1], color=AZUL, linewidth=0.6, zorder=6)
    axs[1].scatter(futuro["x"][~dentro], futuro["y"][~dentro], s=1.5, color="#8f8d86", linewidths=0, zorder=7)
    axs[1].scatter(futuro["x"][dentro], futuro["y"][dentro], s=2.5, color=LARANJA, linewidths=0, zorder=8)
    for ax in axs:
        barra_escala(ax, km=4, pos=(0.08, 0.04))
    seta_norte(axs[0], pos=(0.9, 0.86))
    ponto = lambda cor, rot: Line2D([], [], marker="o", linestyle="", markersize=4, markerfacecolor=cor,
                                    markeredgewidth=0, label=rot)
    axs[0].legend(handles=[ponto(AZUL, f"caso em cluster ({cl['cluster'].nunique()} clusters)"), ponto("#8f8d86", "ruído")],
                  loc="upper left", bbox_to_anchor=(0.0, 0.99), fontsize=7.5, handletextpad=0.2, frameon=True,
                  facecolor="white", edgecolor="#d6d3cc", framealpha=0.95)
    axs[1].legend(handles=[Patch(facecolor=AZUL, alpha=0.3, edgecolor=AZUL, label="área sinalizada"),
                           ponto(LARANJA, "caso seguinte, dentro"), ponto("#8f8d86", "caso seguinte, fora")],
                  loc="upper left", bbox_to_anchor=(0.0, 0.99), fontsize=7.5, handletextpad=0.4, frameon=True,
                  facecolor="white", edgecolor="#d6d3cc", framealpha=0.95)
    axs[0].set_title(f"(a) {fim - pd.Timedelta(days=21):%d/%m} a {fim + pd.Timedelta(days=6):%d/%m/%Y}: "
                     f"{len(d):,} casos".replace(",", "."), loc="left")
    axs[1].set_title(f"(b) 4 semanas seguintes: {br(f'{area:.1f}')}% da área, {dentro.mean() * 100:.0f}% dos casos",
                     loc="left")
    for ax in axs:
        ax.set_xlabel("")
        ax.set_ylabel("")
    fig.tight_layout(w_pad=0.5)
    salvar(fig, "fig6_mapa_exemplo_2015")
    plt.close(fig)


# ----------------------------------------------------------------------------- 5. persistência entre anos

def persistencia():
    plt = estilo()
    g = carregar_geo()
    tam = 0.5
    g["cel"] = list(zip((g["x"] // tam).astype(int), (g["y"] // tam).astype(int)))
    cont = g.pivot_table(index="cel", columns="ano_epi", values="x", aggfunc="size", fill_value=0)
    cont = cont[[a for a in cont.columns if 2013 <= a <= 2025]]
    linhas = []
    anos = list(cont.columns)
    for a, b in zip(anos[:-1], anos[1:]):
        rho = spearmanr(cont[a], cont[b]).statistic
        top_a = cont[a] >= cont[a].quantile(0.9)
        top_b = cont[b] >= cont[b].quantile(0.9)
        linhas.append({"ano": a, "ano_seguinte": b, "spearman_celulas_500m": rho,
                       "jaccard_top10pct": (top_a & top_b).sum() / (top_a | top_b).sum(),
                       "pct_casos_seguinte_no_top10_anterior": cont.loc[top_a, b].sum() / cont[b].sum() * 100,
                       "pct_area_top10": top_a.mean() * 100})
    # mesma pergunta em escala de bairro, com incidência (casos/habitante)
    grade = Grade()
    gb = carregar_geo(nivel_rua=False)
    gb["b"] = grade.bairro_celula[grade.celulas(gb["x"], gb["y"])]
    gb = gb[gb["b"] >= 0]
    inc = gb.pivot_table(index="b", columns="ano_epi", values="x", aggfunc="size", fill_value=0)
    inc = inc.reindex(range(len(grade.nomes_bairros)), fill_value=0)[anos]
    ok = grade.pop_bairro >= POP_MIN_BAIRRO
    inc = inc[ok].div(grade.pop_bairro[ok], axis=0) * 1e5
    for l, (a, b) in zip(linhas, zip(anos[:-1], anos[1:])):
        l["spearman_incidencia_bairro"] = spearmanr(inc[a], inc[b]).statistic
    tab = pd.DataFrame(linhas).round(3)
    tab.to_csv(RES / "tab7_persistencia_interanual.csv", index=False)
    print(tab.to_string())

    corr = cont.corr(method="spearman")
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    im = ax.imshow(corr.values, cmap="Blues", vmin=0, vmax=1)
    ax.grid(False)
    ax.set_xticks(range(len(anos)), [str(a)[2:] for a in anos])
    ax.set_yticks(range(len(anos)), anos)
    fig.colorbar(im, ax=ax, shrink=0.8)
    salvar(fig, "fig7_persistencia")
    plt.close(fig)


# ----------------------------------------------------------------------------- 6. desempenho

def desempenho():
    g = carregar_geo()
    linhas = []
    for n in [1000, 2500, 5000, 10000, 20000, 40000]:
        amostra = g.sample(n=n, random_state=1)
        for eps, m in [(0.3, 10), (0.5, 10)]:
            tempos = []
            for _ in range(3):
                t = time.perf_counter()
                executar_clusterizacao(amostra, eps, m)
                tempos.append(time.perf_counter() - t)
            linhas.append({"n_casos": n, "eps_km": eps, "min_samples": m, "tempo_s_mediana": np.median(tempos)})
    tab = pd.DataFrame(linhas).round(3)
    tab.to_csv(RES / "tab8_desempenho.csv", index=False)
    print(tab.to_string())


# ----------------------------------------------------------------------------- 7. mapas de calor

def _contornos(ax, grade, municipio=True):
    for b in grade.bairros.values():
        for p in getattr(b["geom"], "geoms", [b["geom"]]):
            ax.plot(*p.exterior.xy, color="white", linewidth=0.3, alpha=0.8)
    if municipio:
        for p in getattr(grade.municipio, "geoms", [grade.municipio]):
            ax.plot(*p.exterior.xy, color=TINTA2, linewidth=0.6)
    ax.set_aspect("equal")
    ax.axis("off")


def mapas_calor():
    _mapas_calor([2015, 2016, 2019, 2021, 2024, 2025], "")  # os 6 anos com mais casos
    _mapas_calor(list(range(2013, 2026)), "_todos_anos")


def _mapas_calor(anos, sufixo):
    plt = estilo()
    from matplotlib.colors import LinearSegmentedColormap
    azul = LinearSegmentedColormap.from_list("azul", ["#f4f8fd", "#9ec5f4", "#3987e5", "#1c5cab", "#0d366b"])
    grade = Grade()
    g = carregar_geo()

    # (a) densidade de casos por ano em hexágonos sobre o mapa base, 5 classes por percentil do ano
    import geopandas as gpd
    from matplotlib.colors import BoundaryNorm, ListedColormap
    from matplotlib.patches import Patch
    from cartografia import barra_escala, carregar_mapa_base, desenhar_base, enquadrar_municipio, seta_norte
    base = carregar_mapa_base()
    seq = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
    rotulos_q = ["50% menores", "50–80%", "80–95%", "95–99%", "1% maiores"]
    x0, y0, x1, y1 = grade.municipio.bounds
    tam_hex = int(round((x1 - x0) / 0.35))  # hexágonos de ~350 m
    nc = 3 if len(anos) <= 6 else 5
    nl = int(np.ceil(len(anos) / nc))
    fig, axs = plt.subplots(nl, nc, figsize=(7.2, 3.5 * nl if nc == 3 else 2.3 * nl))
    for ax in axs.ravel()[len(anos):]:
        ax.axis("off")
    for k, (ax, ano) in enumerate(zip(axs.ravel(), anos)):
        sub = g[g["ano_epi"] == ano]
        desenhar_base(ax, base, ruas=True)
        hb = ax.hexbin(sub["x"], sub["y"], gridsize=tam_hex, extent=(x0, x1, y0, y1), mincnt=1, linewidths=0, zorder=3)
        v = hb.get_array()
        lim = np.r_[0, np.quantile(v, [0.5, 0.8, 0.95, 0.99]), v.max() + 1]
        hb.set_cmap(ListedColormap(seq))
        hb.set_norm(BoundaryNorm(lim, 5))
        hb.set_alpha(0.92)
        enquadrar_municipio(ax, base, margem=0.2)
        ax.set_title(f"{ano} ({len(sub):,} casos)".replace(",", "."), loc="left")
        if k == 0:
            seta_norte(ax, pos=(0.88, 0.84))
            barra_escala(ax, km=4, pos=(0.05, 0.04))
    alca = [Patch(facecolor=c, label=r) for c, r in zip(seq, rotulos_q)]
    titulo_leg = "Hexágonos ($\\approx$350 m) por número\nde casos, em percentis do ano"
    if len(anos) < nl * nc:
        fig.tight_layout(h_pad=0.6, w_pad=0.3)
        axs.ravel()[-1].legend(handles=alca, loc="center", frameon=False, title=titulo_leg, fontsize=8, title_fontsize=8)
    else:
        fig.legend(handles=alca, loc="lower center", ncol=5, frameon=False, title=titulo_leg.replace("\n", " "),
                   fontsize=8, title_fontsize=8.5, bbox_to_anchor=(0.5, -0.01))
        fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=0.6, w_pad=0.3)
    salvar(fig, "fig8_mapas_calor_anuais" + sufixo)
    plt.close(fig)

    if sufixo:
        _rr_bairros(grade, base, anos, sufixo, plt, nl, nc)
        return
    # (b) PAI e taxa de alerta do DBSCAN na grade de parâmetros (período de teste)
    pj = pd.read_csv(RES / "prospectiva_janelas.csv", parse_dates=["semana_final"])
    db = pj[pj["metodo"].str.startswith("DBSCAN") & (pj["conjunto"] == "teste")]
    paineis = [("pai", "PAI mediano (teste)", "{:.1f}"), ("captura_pct", "Captura mediana, % (teste)", "{:.1f}"),
               ("sinalizou", "% de janelas com alerta (teste)", "{:.0f}")]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.5))
    for ax, (col, titulo, fmt) in zip(axs, paineis):
        agg = db.groupby(["min_samples", "eps_km"])[col]
        m = (agg.mean() * 100 if col == "sinalizou" else agg.median()).unstack("eps_km")
        ax.imshow(m.values, cmap=azul, aspect="auto", origin="lower")
        ax.grid(False)
        ax.set_xticks(range(len(m.columns)), [br(f"{e:g}") for e in m.columns])
        ax.set_yticks(range(len(m.index)), m.index)
        ax.set_xlabel("$\\varepsilon$ (km)")
        ax.set_title(titulo, loc="left", fontsize=9)
        vmin, vmax = np.nanmin(m.values), np.nanmax(m.values)
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                v = m.values[i, j]
                claro = (v - vmin) / max(vmax - vmin, 1e-9) < 0.55
                ax.text(j, i, br(fmt.format(v)), ha="center", va="center", fontsize=7, color=TINTA if claro else "white")
    axs[0].set_ylabel("min_samples")
    fig.tight_layout()
    salvar(fig, "fig9_pai_grade_parametros")
    plt.close(fig)

    # (c) bairro x ano: participação de cada bairro nos casos do ano (25 bairros com mais casos)
    geo = pd.read_csv(DADOS / "casos_geocodificados.csv.gz", low_memory=False)
    geo = geo[geo["confirmado"] & geo["ano_epi"].between(2013, 2025) & geo["bairro_osm"].notna()]
    nomes = {k: v["nome"] for k, v in grade.bairros.items()}
    tab = geo.pivot_table(index="bairro_osm", columns="ano_epi", values="latitude", aggfunc="size", fill_value=0)
    popb = pd.Series(grade.pop_bairro, index=grade.nomes_bairros)
    popb = popb[popb >= 5000]  # bairros muito pequenos têm taxas instáveis
    taxa = tab.reindex(popb.index, fill_value=0).div(popb, axis=0) * 1e5
    resumo = pd.DataFrame({"bairro": [nomes[b] for b in taxa.index], "populacao_2022": popb.round(0),
                           "casos_2013_2025": tab.reindex(popb.index, fill_value=0).sum(axis=1),
                           "incidencia_media_anual_100mil": taxa.mean(axis=1)}).sort_values(
                               "incidencia_media_anual_100mil", ascending=False)
    resumo.round(1).to_csv(RES / "tab_incidencia_bairros.csv", index=False)
    top = resumo.index[:25]
    pct = taxa.loc[top]
    pct.index = [nomes.get(b, b) for b in pct.index]
    pct.round(1).to_csv(RES / "tab_bairro_ano_incidencia.csv")
    from matplotlib.colors import LogNorm
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    im = ax.imshow(pct.values.clip(1), cmap=azul, aspect="auto", norm=LogNorm(vmin=10, vmax=pct.values.max()))
    ax.grid(False)
    ax.set_xticks(range(pct.shape[1]), pct.columns)
    ax.set_yticks(range(pct.shape[0]), pct.index, fontsize=7.5)
    lim = np.exp(np.log(10) + 0.55 * (np.log(pct.values.max()) - np.log(10)))
    for i in range(pct.shape[0]):
        for j in range(pct.shape[1]):
            v = pct.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=5.5, color=TINTA if v < lim else "white")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02).set_label("Casos confirmados por 100 mil habitantes (escala log)")
    salvar(fig, "fig10_bairro_ano")
    plt.close(fig)

    _rr_bairros(grade, base, anos, sufixo, plt, nl, nc)


def _rr_bairros(grade, base, anos, sufixo, plt, nl, nc):
    import geopandas as gpd
    from matplotlib.patches import Patch
    from cartografia import barra_escala, desenhar_base, enquadrar_municipio, seta_norte
    # (d) risco relativo por bairro: incidência do bairro ÷ incidência do Recife no ano (coropleto, 5 classes)
    gb = carregar_geo(nivel_rua=False)
    gb["b"] = grade.bairro_celula[grade.celulas(gb["x"], gb["y"])]
    gb = gb[gb["b"] >= 0]
    div = ["#184f95", "#86b6ef", "#e9e8e4", "#ee8a87", "#a8282a"]
    limites = [0, 0.5, 0.8, 1.25, 2, np.inf]
    rotulos_rr = ["< 0,5", "0,5–0,8", "0,8–1,25", "1,25–2", "$\\geq$ 2"]
    geoms = gpd.GeoSeries([grade.bairros[b]["geom"] for b in grade.nomes_bairros])
    pequeno = grade.pop_bairro < POP_MIN_BAIRRO
    fig, axs = plt.subplots(nl, nc, figsize=(7.2, 3.5 * nl if nc == 3 else 2.3 * nl))
    for ax in axs.ravel()[len(anos):]:
        ax.axis("off")
    for k, (ax, ano) in enumerate(zip(axs.ravel(), anos)):
        sub = gb[gb["ano_epi"] == ano]
        casos = np.bincount(sub["b"], minlength=len(grade.nomes_bairros))
        rr = (casos / np.maximum(grade.pop_bairro, 1)) / (casos.sum() / grade.pop_bairro.sum())
        classe = np.digitize(rr, limites[1:-1])
        desenhar_base(ax, base, ruas=False)
        geoms[~pequeno].plot(ax=ax, color=[div[c] for c in classe[~pequeno]], edgecolor="white", linewidth=0.3, zorder=3)
        geoms[pequeno].plot(ax=ax, facecolor="white", edgecolor="#8f8d86", hatch="////", linewidth=0.3, zorder=3)
        base["agua"].plot(ax=ax, color="#c9dcea", linewidth=0, zorder=4, rasterized=True)
        base["rios"].plot(ax=ax, color="#c9dcea", linewidth=0.9, zorder=4, rasterized=True)
        enquadrar_municipio(ax, base, margem=0.2)
        ax.set_title(str(ano), loc="left")
        if k == 0:
            seta_norte(ax, pos=(0.88, 0.84))
            barra_escala(ax, km=4, pos=(0.05, 0.04))
    alca = [Patch(facecolor=c, edgecolor="white", label=r) for c, r in zip(div, rotulos_rr)]
    alca.append(Patch(facecolor="white", edgecolor="#8f8d86", hatch="////", label="< 1.000 hab."))
    titulo_leg = "Risco relativo do bairro\n(incidência do bairro ÷\nincidência do Recife no ano)"
    if len(anos) < nl * nc:
        fig.tight_layout(h_pad=0.6, w_pad=0.3)
        axs.ravel()[-1].legend(handles=alca, loc="center", frameon=False, title=titulo_leg, fontsize=8, title_fontsize=8)
    else:
        fig.legend(handles=alca, loc="lower center", ncol=6, frameon=False, fontsize=8, title_fontsize=8.5,
                   title=titulo_leg.replace("\n", " "), bbox_to_anchor=(0.5, -0.01))
        fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=0.6, w_pad=0.3)
    salvar(fig, "fig11_risco_relativo_bairros" + sufixo)
    plt.close(fig)


# ----------------------------------------------------------------------------- 8. figura de métodos: ponderação areal

def figura_populacao(centro_bairro="CAMPINA BARRETO", lado_km=1.6):
    plt = estilo()
    import geopandas as gpd
    import shapely
    from matplotlib.colors import LinearSegmentedColormap, LogNorm
    from matplotlib.patches import Rectangle
    azul = LinearSegmentedColormap.from_list("azul", ["#f4f8fd", "#9ec5f4", "#3987e5", "#1c5cab", "#0d366b"])
    grade = Grade()
    setores = gpd.read_file(IBGE_SETORES, where="CD_MUN='2611606'")
    setores["pop"] = pd.to_numeric(setores["v0001"], errors="coerce").fillna(0)
    setores["geom_km"] = [shapely.transform(g, lambda c: np.c_[para_km(c[:, 0], c[:, 1])]) for g in setores.geometry]
    setores["dens"] = setores["pop"] / shapely.area(setores["geom_km"].to_numpy())

    c = grade.bairros[centro_bairro]["geom"].centroid
    x0, x1, y0, y1 = c.x - lado_km / 2, c.x + lado_km / 2, c.y - lado_km / 2, c.y + lado_km / 2
    janela = shapely.box(x0, y0, x1, y1)
    rec = setores[shapely.intersects(setores["geom_km"].to_numpy(), janela)]
    dens_cel = (grade.pop / CELULA_KM ** 2).reshape(grade.nx, grade.ny)
    norma = LogNorm(vmin=1000, vmax=max(np.nanpercentile(dens_cel[dens_cel > 0], 99.5), rec["dens"].max()))

    def poligonos(ax, geom, **kw):
        for p in getattr(geom, "geoms", [geom]):
            ax.fill(*p.exterior.xy, **kw)

    def moldura(ax, titulo, lim=None):
        lx0, lx1, ly0, ly1 = lim or (x0, x1, y0, y1)
        ax.set_xlim(lx0, lx1)
        ax.set_ylim(ly0, ly1)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for sp in ax.spines.values():
            sp.set_visible(True)
            sp.set_color(CINZA)
        ax.set_title(titulo, loc="left", fontsize=9)

    fig, axs = plt.subplots(2, 2, figsize=(7.2, 7.4))
    (a, b), (cc, d) = axs

    # (a) cidade inteira
    a.pcolormesh(grade.cx, grade.cy, np.where(dens_cel > 0, dens_cel, np.nan), cmap=azul, norm=norma, shading="auto",
                 rasterized=True)
    for p in getattr(grade.municipio, "geoms", [grade.municipio]):
        a.plot(*p.exterior.xy, color=TINTA2, linewidth=0.6)
    from cartografia import carregar_mapa_base
    base = carregar_mapa_base()
    base["agua"].plot(ax=a, color="#c9dcea", linewidth=0, zorder=3)
    base["rios"].plot(ax=a, color="#c9dcea", linewidth=0.8, zorder=3)
    a.add_patch(Rectangle((x0, y0), lado_km, lado_km, fill=False, edgecolor=LARANJA, linewidth=1.4, zorder=5))
    a.set_aspect("equal")
    a.axis("off")
    a.set_title("(a) Recife, população na grade\n(quadrado: recorte de (b) e (d))", loc="left", fontsize=9)

    # (b) setores censitários originais
    for g, dn in zip(rec["geom_km"], rec["dens"]):
        poligonos(b, g, facecolor=azul(norma(max(dn, 1000))) if dn > 0 else "#ffffff", edgecolor="white", linewidth=0.8)
    moldura(b, f"(b) {len(rec)} setores censitários (Censo 2022)\n(quadrado: área ampliada em (c))")

    # (c) grade sobre os setores, um setor em destaque
    alvo = rec.assign(a=shapely.area(rec["geom_km"].to_numpy())).query("pop > 0")
    alvo = alvo.iloc[(alvo["a"] - alvo["a"].median()).abs().argsort().iloc[0]]
    bx0, by0, bx1, by1 = alvo["geom_km"].bounds
    m = 0.12
    lado = max(bx1 - bx0, by1 - by0) + 2 * m
    zx, zy = (bx0 + bx1) / 2, (by0 + by1) / 2
    zoom = (zx - lado / 2, zx + lado / 2, zy - lado / 2, zy + lado / 2)
    b.add_patch(Rectangle((zoom[0], zoom[2]), lado, lado, fill=False, edgecolor=LARANJA, linewidth=1.4))
    for g in rec["geom_km"]:
        poligonos(cc, g, facecolor="none", edgecolor=TINTA2, linewidth=0.8)
    ix = np.where((grade.cx.ravel() > x0 - CELULA_KM) & (grade.cx.ravel() < x1 + CELULA_KM) &
                  (grade.cy.ravel() > y0 - CELULA_KM) & (grade.cy.ravel() < y1 + CELULA_KM))[0]
    caixas = shapely.box(grade.cx.ravel()[ix] - CELULA_KM / 2, grade.cy.ravel()[ix] - CELULA_KM / 2,
                         grade.cx.ravel()[ix] + CELULA_KM / 2, grade.cy.ravel()[ix] + CELULA_KM / 2)
    for cx_ in np.unique(grade.cx.ravel()[ix]):
        cc.axvline(cx_ - CELULA_KM / 2, color=CINZA, linewidth=0.6)
    for cy_ in np.unique(grade.cy.ravel()[ix]):
        cc.axhline(cy_ - CELULA_KM / 2, color=CINZA, linewidth=0.6)
    inter = shapely.area(shapely.intersection(caixas, alvo["geom_km"]))
    frac = inter / alvo["geom_km"].area
    for p_ in getattr(alvo["geom_km"], "geoms", [alvo["geom_km"]]):
        cc.plot(*p_.exterior.xy, color=LARANJA, linewidth=2, zorder=5)
    for k in np.where(frac > 0.004)[0]:
        bx = caixas[k]
        cc.fill(*bx.exterior.xy, facecolor=LARANJA, alpha=0.15 + 0.6 * frac[k] / frac.max(), edgecolor="none")
        cc.text(bx.centroid.x, bx.centroid.y, f"{alvo['pop'] * frac[k]:.0f}", ha="center", va="center", fontsize=8,
                color=TINTA, zorder=6)
    moldura(cc, f"(c) Setor de {alvo['pop']:.0f} hab. repartido\npela área de interseção", zoom)
    for sp in cc.spines.values():
        sp.set_color(LARANJA)
        sp.set_linewidth(1.4)

    # (d) resultado
    d.pcolormesh(grade.cx, grade.cy, np.where(dens_cel > 0, dens_cel, np.nan), cmap=azul, norm=norma, shading="auto",
                 rasterized=True)
    for g in rec["geom_km"]:
        poligonos(d, g, facecolor="none", edgecolor="white", linewidth=0.5)
    moldura(d, "(d) Resultado no recorte:\npopulação por célula de 100 m")

    sm = plt.cm.ScalarMappable(cmap=azul, norm=norma)
    cb = fig.colorbar(sm, ax=axs, orientation="horizontal", fraction=0.03, pad=0.03, aspect=50)
    from matplotlib.ticker import FixedLocator, NullLocator
    marcas = [1000, 2000, 5000, 10000, 20000, 50000]
    cb.ax.xaxis.set_major_locator(FixedLocator([v for v in marcas if v <= norma.vmax]))
    cb.ax.xaxis.set_minor_locator(NullLocator())
    cb.ax.set_xticklabels([f"{v:,}".replace(",", ".") for v in marcas if v <= norma.vmax])
    cb.set_label("Densidade populacional (hab./km², escala log)")
    salvar(fig, "fig12_ponderacao_areal")
    plt.close(fig)
    print("setor em destaque:", alvo["CD_SETOR"], alvo["pop"], "células:", int((frac > 0.004).sum()),
          "soma:", round(float((alvo["pop"] * frac).sum()), 1))


ETAPAS = {"descritiva": descritiva, "sensibilidade": sensibilidade, "estabilidade": estabilidade,
          "prospectiva": prospectiva, "persistencia": persistencia, "desempenho": desempenho, "mapas_calor": mapas_calor, "populacao": figura_populacao}

if __name__ == "__main__":
    RES.mkdir(exist_ok=True)
    for nome in sys.argv[1:] or ETAPAS:
        print(f"\n===== {nome}")
        t = time.perf_counter()
        ETAPAS[nome]()
        print(f"({time.perf_counter() - t:.0f} s)")
