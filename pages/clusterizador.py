import streamlit as st
import pandas as pd
import numpy as np
import io
import json
import re
import sqlite3
import unicodedata
from html import escape
from pathlib import Path
from rapidfuzz import fuzz, process
from shapely import wkb
from shapely.geometry import mapping
from shapely.ops import unary_union
from sklearn.cluster import DBSCAN
import folium
from branca.element import MacroElement, Template
from folium import Circle
from folium.elements import JSCSSMixin
from streamlit_folium import st_folium
import plotly.express as px
from i18n import t
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.metrics import adjusted_rand_score
from ui import inject_styles, html, page_header, section, mini_cards

# Escala de cor dos gráficos, na paleta do app
ESCALA = ["#b2ebf2", "#00acc1", "#0d47a1"]

inject_styles()
page_header("fi-rr-chart-network", t("cluster_title"), t("cluster_lead"))


# ------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------------------------------------
def normalizar_nome(nome):
    nome = unicodedata.normalize("NFD", str(nome).strip().lower())
    nome = "".join(c for c in nome if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", nome).strip("_")


def detectar_coluna(colunas, aliases):
    """Encontra a coluna pelo nome, ignorando maiúsculas, acentos e espaços."""
    nomes = {normalizar_nome(c): c for c in colunas}
    for alias in aliases:
        if alias in nomes:
            return nomes[alias]
    return None


def milhar(n):
    """Separador de milhar conforme o idioma (1.219 em português, 1,219 em inglês)."""
    texto = f"{n:,}"
    return texto.replace(",", ".") if st.session_state.get("lang", "pt") == "pt" else texto


def para_numero(serie):
    """Converte coordenadas, aceitando vírgula decimal ("-8,05")."""
    if not pd.api.types.is_numeric_dtype(serie):  # texto (object no pandas 2, str no pandas 3)
        serie = serie.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(serie, errors="coerce")


def semanas_epidemiologicas(datas):
    """Retorna (semana_epi 'S01'–'S53', ano_epi) a partir de datas já convertidas."""
    iso = datas.dt.isocalendar()
    semana = iso["week"].map(lambda w: f"S{int(w):02d}" if pd.notna(w) else None)
    ano = iso["year"].map(lambda a: int(a) if pd.notna(a) else None)
    return semana.astype(object), ano.astype(object)


def executar_clusterizacao(df, eps, min_samples):
    """Executa clusterização DBSCAN com métrica Haversine"""
    coords = np.radians(df[["latitude", "longitude"]])
    db = DBSCAN(
        eps=eps,  # já convertido para radianos
        min_samples=min_samples,
        algorithm="ball_tree",
        metric="haversine"
    )
    df["cluster"] = db.fit_predict(coords)
    return df


def desenhar_clusters(mapa, df, cores, eps_km):
    """Desenha clusters e ruídos no mapa folium"""
    for cluster_id in sorted(df["cluster"].unique()):
        cluster_df = df[df["cluster"] == cluster_id]

        # Cor diferenciada para ruídos
        if cluster_id == -1:
            cor = "#9E9E9E"  # cinza
        else:
            cor = cores[cluster_id % len(cores)]

        lat_mean = cluster_df["latitude"].mean()
        lon_mean = cluster_df["longitude"].mean()

        # Círculo do cluster (não desenha para ruídos)
        if cluster_id != -1:
            Circle(
                location=[lat_mean, lon_mean],
                radius=eps_km * 1000,  # metros
                color=cor,
                fill=False,
                weight=2,
                opacity=0.5,
            ).add_to(mapa)

        # Pontos individuais
        for _, row in cluster_df.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=6,
                color=cor,
                fill=True,
                fill_color=cor,
                fill_opacity=0.9 if cluster_id != -1 else 0.6,
                popup=f"Cluster {cluster_id}" if cluster_id != -1 else "Ruído (isolado)",
            ).add_to(mapa)


def estilizar(fig):
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color="#37474f",
        title_font_color="#0a2a66",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(gridcolor="#eef3fa")
    fig.update_yaxes(gridcolor="#eef3fa")
    return fig


@st.cache_data(show_spinner=False)
def ler_base(dados: bytes, nome: str) -> pd.DataFrame:
    if nome.lower().endswith(".csv"):
        for encoding in ("utf-8", "latin-1"):
            try:
                return pd.read_csv(io.BytesIO(dados), sep=None, engine="python", encoding=encoding)
            except UnicodeDecodeError:
                continue
    return pd.read_excel(io.BytesIO(dados))


def avaliar_estabilidade_ari(df_base, eps_base, min_samples_base, eps_fatores=(0.9, 1.1), delta_minpts=(-1, +1)):
    """
    Compara a clusterização base com pequenas variações de eps e min_samples usando ARI.
    Importante: df_base precisa ter a mesma ordem de linhas em todas as execuções.
    """
    # garante ordem estável
    df_base = df_base.sort_index()

    df_ref = executar_clusterizacao(df_base.copy(), eps_base, min_samples_base).sort_index()
    labels_ref = df_ref["cluster"].to_numpy()

    resultados = []

    # variações em eps
    for f in eps_fatores:
        eps_var = eps_base * f
        df_var = executar_clusterizacao(df_base.copy(), eps_var, min_samples_base).sort_index()
        ari = adjusted_rand_score(labels_ref, df_var["cluster"].to_numpy())
        resultados.append(("eps", f"{f:.2f}×", ari))

    # variações em min_samples
    for d in delta_minpts:
        m_var = min_samples_base + d
        if m_var >= 2:
            df_var = executar_clusterizacao(df_base.copy(), eps_base, m_var).sort_index()
            ari = adjusted_rand_score(labels_ref, df_var["cluster"].to_numpy())
            resultados.append(("min_samples", f"{m_var}", ari))

    return resultados


# ------------------------------------------------------------
# CAMADAS DE REFERÊNCIA (pontos fixos e distritos sanitários)
# ------------------------------------------------------------
MALHA_BAIRROS = Path("estudo/dados/ibge/PE_bairros_CD2022.gpkg")
SEDES_DISTRITOS = Path("referencias/recife/sedes_distritos.csv")
UNIDADES_SAUDE = Path("referencias/recife/unidades_saude.csv")
BAIRROS_DISTRITOS = Path("referencias/recife/bairros_distritos.csv")

MODELO_PONTOS = (
    "tipo,nome,latitude,longitude\n"
    "unidade de saude,USF Exemplo,-8.0476,-34.8770\n"
    "armadilha,Ovitrampa 001,-8.0631,-34.8711\n"
    "imovel abandonado,Rua Exemplo 100,-8.0539,-34.8811\n"
)
MODELO_DISTRITOS = (
    "bairro,distrito\n"
    "Boa Vista,DS I\n"
    "Santo Amaro,DS I\n"
    "Encruzilhada,DS II\n"
    "Casa Amarela,DS III\n"
)

# Desenhos dos ícones em SVG (Font Awesome Free). SVG embutido aparece também na imagem baixada do mapa,
# o que não acontece com a fonte de ícones carregada de outro domínio
ICONES_SVG = json.loads(Path("assets/icones_mapa.json").read_text(encoding="utf-8"))


def svg_icone(nome, tamanho, cor="white"):
    icone = ICONES_SVG[nome]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{icone["viewBox"]}" width="{tamanho}" '
            f'height="{tamanho}" fill="{cor}"><path d="{icone["d"]}"/></svg>')


# Ícone e cor do marcador conforme palavras do tipo
ICONES_TIPO = [
    (("sede", "distrito"), "building-flag", "#0D47A1"),
    (("zoonose",), "shield-virus", "#2E7D32"),
    (("hospital", "maternidade"), "hospital", "#880E4F"),
    (("pronto_atendimento", "upa"), "truck-medical", "#B71C1C"),
    (("saude", "ubs", "usf", "posto", "policlinica", "clinica"), "house-medical", "#E53935"),
    (("armadilha", "ovitrampa", "larvitrampa", "trampa"), "mosquito", "#EF6C00"),
    (("abandonad", "baldio", "terreno", "desocupad", "imovel"), "house-crack", "#37474F"),
    (("estrategico", "borracharia", "ferro_velho", "cemiterio", "reciclagem", "deposito"),
     "triangle-exclamation", "#6A1B9A"),
]

CORES_DISTRITOS = [
    "#4E79A7", "#F28E2B", "#59A14F", "#B07AA1", "#EDC948",
    "#76B7B2", "#FF9DA7", "#9C755F", "#E15759", "#BAB0AC",
]
ROMANOS = {"i": 1, "v": 5, "x": 10}


def icone_do_tipo(tipo):
    chave = normalizar_nome(tipo)
    for palavras, icone, cor in ICONES_TIPO:
        if any(palavra in chave for palavra in palavras):
            return icone, cor
    return "location-dot", "#00838F"


def numero_distrito(nome):
    """Número do distrito em 'DS II', 'VIII' ou '3' (None se não houver)."""
    fim = normalizar_nome(nome).split("_")[-1]
    if fim.isdigit():
        return int(fim)
    if fim and re.fullmatch(r"x{0,3}(ix|iv|v?i{0,3})", fim):
        valores = [ROMANOS[c] for c in fim]
        return sum(-v if i + 1 < len(valores) and v < valores[i + 1] else v for i, v in enumerate(valores))
    return None


def nome_distrito(valor):
    """'II' vira 'DS II'; nomes completos ('Distrito Norte', 'DS II') ficam como estão."""
    texto = str(valor).strip()
    sozinho = "_" not in normalizar_nome(texto)
    return f"DS {texto}" if sozinho and numero_distrito(texto) is not None else texto


def preparar_pontos(df, nome_arquivo):
    """Pontos fixos com _tipo, _nome, _lat, _lon e o HTML do popup (demais colunas do arquivo)."""
    col_lat = detectar_coluna(df.columns, ALIASES["lat"])
    col_lon = detectar_coluna(df.columns, ALIASES["lon"])
    if col_lat is None or col_lon is None:
        return pd.DataFrame()
    lat, lon = para_numero(df[col_lat]), para_numero(df[col_lon])
    ok = lat.between(-90, 90) & lon.between(-180, 180)
    pontos = df[ok].copy()
    pontos["_lat"], pontos["_lon"] = lat[ok], lon[ok]

    # Sem coluna de tipo (ou com tipo vazio), o nome do arquivo identifica a camada
    col_tipo = detectar_coluna(df.columns, ["tipo", "categoria", "classe", "type", "category"])
    padrao = Path(nome_arquivo).stem.replace("_", " ")
    tipos = pontos[col_tipo].fillna("").astype(str).str.strip() if col_tipo else pd.Series("", index=pontos.index)
    pontos["_tipo"] = tipos.mask(tipos == "", padrao)

    col_nome = detectar_coluna(df.columns, ["nome", "name", "estabelecimento", "unidade", "descricao",
                                            "identificacao", "codigo", "id"])
    pontos["_nome"] = pontos[col_nome].fillna("").astype(str) if col_nome else ""

    extras = [c for c in df.columns if c not in (col_lat, col_lon, col_tipo, col_nome)]
    pontos["_popup"] = [
        f"<b>{escape(row['_nome'] or row['_tipo'])}</b><br><small>{escape(row['_tipo'])}</small>"
        + "".join(f"<br>{escape(str(c))}: {escape(str(row[c]))}" for c in extras if pd.notna(row[c]))
        for _, row in pontos.iterrows()
    ]
    return pontos[["_tipo", "_nome", "_lat", "_lon", "_popup"]]


@st.cache_data(show_spinner=False)
def carregar_bairros():
    """Bairros de Pernambuco (malha do IBGE, Censo 2022) com polígonos simplificados."""
    con = sqlite3.connect(MALHA_BAIRROS)
    try:
        linhas = con.execute("SELECT NM_MUN, NM_BAIRRO, geom FROM PE_bairros_CD2022").fetchall()
    finally:
        con.close()
    bairros = []
    for municipio, nome, blob in linhas:
        # Geometria GeoPackage: cabeçalho de 8 bytes e envelope (0, 32, 48 ou 64 bytes) antes do WKB
        envelope = (0, 32, 48, 48, 64)[(blob[3] >> 1) & 7]
        geom = wkb.loads(bytes(blob[8 + envelope:])).simplify(0.00003)
        bairros.append({"municipio": municipio, "bairro": nome, "geom": geom})
    return pd.DataFrame(bairros)


def associar_distritos(tabela, bairros):
    """
    Liga cada bairro do arquivo ao polígono do IBGE, no município com mais bairros em comum.
    Retorna (bairros do município com 'distrito' e colunas extras, município, nomes sem par, colunas extras)
    ou None se faltarem as colunas de bairro e distrito.
    """
    col_bairro = detectar_coluna(tabela.columns, ["bairro", "nm_bairro", "bairros", "neighborhood"])
    col_ds = detectar_coluna(tabela.columns, ["ds", "distrito", "distrito_sanitario", "nm_distrito", "district"])
    if col_bairro is None or col_ds is None:
        return None

    tabela = tabela.dropna(subset=[col_bairro]).copy()
    tabela["_chave"] = tabela[col_bairro].map(normalizar_nome)
    bairros = bairros.assign(_chave=bairros["bairro"].map(normalizar_nome))
    comuns = bairros[bairros["_chave"].isin(tabela["_chave"])]
    if comuns.empty:
        return pd.DataFrame(), None, [], []
    municipio = comuns["municipio"].value_counts().idxmax()
    bairros = bairros[bairros["municipio"] == municipio].copy()

    # Nomes que não batem exatamente ("AFOGAGOS", "SITIO DOS PINTOS") usam o bairro mais parecido
    chaves_ibge = list(bairros["_chave"])
    nao_encontrados = []
    for i, chave in tabela["_chave"].items():
        if chave not in chaves_ibge:
            par = process.extractOne(chave, chaves_ibge, scorer=fuzz.WRatio, score_cutoff=85)
            if par:
                tabela.at[i, "_chave"] = par[0]
            else:
                nao_encontrados.append(str(tabela.at[i, col_bairro]))

    extras = [c for c in tabela.columns if c not in (col_bairro, col_ds, "_chave")]
    tabela["distrito"] = tabela[col_ds].map(lambda v: nome_distrito(v) if pd.notna(v) else None)
    tabela = tabela.drop_duplicates("_chave")[["_chave", "distrito"] + extras]
    return bairros.merge(tabela, on="_chave", how="left"), municipio, nao_encontrados, extras


def desenhar_distritos(mapa, bairros_ds, extras):
    """Bairros coloridos pelo distrito, contorno de cada distrito e o nome no centro."""
    grupo = folium.FeatureGroup(name=t("layers_districts_title"))
    distritos = sorted(bairros_ds["distrito"].dropna().unique(),
                       key=lambda d: (numero_distrito(d) is None, numero_distrito(d) or 0, d))
    cor_de = {d: CORES_DISTRITOS[i % len(CORES_DISTRITOS)] for i, d in enumerate(distritos)}

    rotulo_bairro, rotulo_ds = t("layers_tooltip_bairro"), t("layers_tooltip_distrito")
    feicoes = []
    for _, row in bairros_ds.iterrows():
        props = {rotulo_bairro: row["bairro"], rotulo_ds: row["distrito"] or t("layers_no_district"),
                 "_cor": cor_de.get(row["distrito"])}
        props.update({str(c): (str(row[c]) if pd.notna(row[c]) else "–") for c in extras})
        feicoes.append({"type": "Feature", "geometry": mapping(row["geom"]), "properties": props})

    folium.GeoJson(
        {"type": "FeatureCollection", "features": feicoes},
        style_function=lambda f: {
            "color": f["properties"]["_cor"] or "#9E9E9E",
            "weight": 1,
            "fillColor": f["properties"]["_cor"] or "#9E9E9E",
            "fillOpacity": 0.18 if f["properties"]["_cor"] else 0.04,
            "dashArray": None if f["properties"]["_cor"] else "4 4",
        },
        highlight_function=lambda f: {"weight": 3, "fillOpacity": 0.35},
        tooltip=folium.GeoJsonTooltip(fields=[rotulo_bairro, rotulo_ds] + [str(c) for c in extras]),
    ).add_to(grupo)

    for distrito in distritos:
        area = unary_union(list(bairros_ds.loc[bairros_ds["distrito"] == distrito, "geom"]))
        folium.GeoJson(
            mapping(area),
            style_function=lambda f, cor=cor_de[distrito]: {"color": cor, "weight": 3, "fill": False},
            interactive=False,
        ).add_to(grupo)
        centro = area.representative_point()
        folium.Marker(
            [centro.y, centro.x],
            icon=folium.DivIcon(
                html=f'<div style="transform: translate(-50%, -50%); width: max-content; padding: 2px 8px; '
                     f'border-radius: 10px; background: white; border: 2px solid {cor_de[distrito]}; '
                     f'font: 600 12px sans-serif; color: #263238">{escape(distrito)}</div>',
                icon_size=(0, 0),
            ),
            interactive=False,
        ).add_to(grupo)
    grupo.add_to(mapa)


def desenhar_pontos_fixos(mapa, pontos):
    """Uma camada por tipo de ponto fixo, com ícone conforme o tipo."""
    for tipo, grupo_df in pontos.groupby("_tipo", sort=True):
        icone, cor = icone_do_tipo(tipo)
        grupo = folium.FeatureGroup(name=f"{tipo[:1].upper()}{tipo[1:]} ({milhar(len(grupo_df))})")
        # Círculo pequeno com o ícone: com centenas de unidades, alfinetes grandes escondem os clusters
        marcador = (
            f'<div style="width: 22px; height: 22px; border-radius: 50%; background: {cor}; '
            f'border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,.45); display: flex; '
            f'align-items: center; justify-content: center">{svg_icone(icone, 12)}</div>'
        )
        for _, row in grupo_df.iterrows():
            folium.Marker(
                [row["_lat"], row["_lon"]],
                icon=folium.DivIcon(html=marcador, icon_size=(26, 26), icon_anchor=(13, 13)),
                tooltip=row["_nome"] or tipo,
                popup=folium.Popup(row["_popup"], max_width=320),
            ).add_to(grupo)
        grupo.add_to(mapa)


class ControlesMapa(JSCSSMixin, MacroElement):
    """
    Barra abaixo do zoom com dois botões: voltar ao enquadramento inicial dos casos e
    baixar um PNG do que está na tela, com o tamanho exato do mapa.
    """
    # O st_folium só carrega scripts declarados em default_js, como nos plugins do folium
    default_js = [("dom_to_image", "https://unpkg.com/dom-to-image@2.6.0/dist/dom-to-image.min.js")]
    _template = Template("""
        {% macro script(this, kwargs) %}
            var ControlesMapa = L.Control.extend({
                options: { position: "topleft" },
                onAdd: function (mapa) {
                    var div = L.DomUtil.create("div", "leaflet-bar leaflet-control");
                    L.DomEvent.disableClickPropagation(div);
                    function botao(titulo, icone, acao) {
                        var link = L.DomUtil.create("a", "", div);
                        link.href = "#";
                        link.title = titulo;
                        link.setAttribute("role", "button");
                        link.style.display = "flex";
                        link.style.alignItems = "center";
                        link.style.justifyContent = "center";
                        link.innerHTML = icone;
                        L.DomEvent.on(link, "click", function (e) {
                            L.DomEvent.preventDefault(e);
                            acao();
                        });
                    }

                    var limites = {{ this.limites|tojson }};
                    botao({{ this.titulo_enquadrar|tojson }}, {{ this.icone_enquadrar|tojson }}, function () {
                        if (limites) { mapa.fitBounds(limites); }
                        else { mapa.setView({{ this.centro|tojson }}, 12); }
                    });

                    botao({{ this.titulo_imagem|tojson }}, {{ this.icone_imagem|tojson }}, function () {
                        var area = mapa.getContainer();
                        domtoimage.toPng(area, {
                            width: area.clientWidth,
                            height: area.clientHeight,
                            // Sem os botões do topo; a atribuição dos mapas base (rodapé) fica na imagem
                            filter: function (no) {
                                return !(no.classList && no.classList.contains("leaflet-top"));
                            }
                        }).then(function (url) {
                            var a = document.createElement("a");
                            a.download = {{ this.arquivo|tojson }} + ".png";
                            a.href = url;
                            document.body.appendChild(a);
                            a.click();
                            a.remove();
                        });
                    });
                    return div;
                }
            });
            new ControlesMapa().addTo({{ this._parent.get_name() }});
        {% endmacro %}
    """)

    def __init__(self, titulo_enquadrar, centro, limites, titulo_imagem, arquivo):
        super().__init__()
        self._name = "ControlesMapa"
        self.titulo_enquadrar = titulo_enquadrar
        self.centro = [float(c) for c in centro]
        self.limites = [[float(v) for v in canto] for canto in limites] if limites else None
        self.icone_enquadrar = svg_icone("expand", 14, "#333")
        self.titulo_imagem = titulo_imagem
        self.arquivo = arquivo
        self.icone_imagem = svg_icone("camera", 14, "#333")


# ------------------------------------------------------------
# UPLOAD E PRÉ-PROCESSAMENTO
# ------------------------------------------------------------
html(section("fi-rr-file-upload", t("cluster_upload_header")))
uploaded_file = st.file_uploader(t("cluster_upload_label"), type=["csv", "xlsx"])

if not uploaded_file:
    html(mini_cards([
        ("fi-rr-marker", t("cluster_req_coords")),
        ("fi-rr-calendar-lines", t("cluster_req_date")),
        ("fi-rr-table-list", t("cluster_req_format")),
    ]))
    st.write("")
    st.page_link("pages/coordenadas.py", label=t("cluster_req_link"), icon=":material/my_location:")
    st.stop()

try:
    with st.spinner(t("cluster_loading")):
        df = ler_base(uploaded_file.getvalue(), uploaded_file.name).copy()
except Exception as erro:
    st.error(t("cluster_read_error").format(error=erro))
    st.stop()

if df.empty:
    st.error(t("cluster_empty_file"))
    st.stop()

# --------------------------------------------------------
# COLUNAS: detecção automática, com escolha manual quando necessário
# --------------------------------------------------------
ALIASES = {
    "data": ["dt_notificacao", "dt_notific", "data_notificacao", "data_de_notificacao", "dt_notif",
             "data", "date", "dt_sin_pri", "dt_diagnostico_sintoma", "data_sintomas"],
    "lat": ["latitude", "lat", "y"],
    "lon": ["longitude", "long", "lon", "lng", "x"],
}
colunas = list(df.columns)
detectadas = {campo: detectar_coluna(colunas, aliases) for campo, aliases in ALIASES.items()}
faltando = [campo for campo, coluna in detectadas.items() if coluna is None]
rotulos = {"data": t("cluster_col_date"), "lat": t("cluster_col_lat"), "lon": t("cluster_col_lon")}

with st.expander(t("cluster_columns_title"), expanded=bool(faltando), icon=":material/view_column:"):
    if faltando:
        st.warning(t("cluster_columns_missing").format(missing=", ".join(rotulos[c] for c in faltando)))
    c1, c2, c3 = st.columns(3)
    escolhidas = {}
    for col, campo in zip((c1, c2, c3), ("data", "lat", "lon")):
        with col:
            escolhidas[campo] = st.selectbox(
                rotulos[campo],
                options=colunas,
                index=colunas.index(detectadas[campo]) if detectadas[campo] is not None else None,
                placeholder=t("cluster_col_placeholder"),
                key=f"cluster_col_{campo}",
            )

if any(coluna is None for coluna in escolhidas.values()):
    st.stop()

# --------------------------------------------------------
# VALIDAÇÃO DOS DADOS
# --------------------------------------------------------
datas = pd.to_datetime(df[escolhidas["data"]], errors="coerce", dayfirst=True, format="mixed")
if datas.notna().sum() == 0:
    exemplos = ", ".join(map(str, df[escolhidas["data"]].dropna().astype(str).unique()[:3])) or "–"
    st.error(t("cluster_error_dates").format(col=escolhidas["data"], examples=exemplos))
    st.stop()

lat = para_numero(df[escolhidas["lat"]])
lon = para_numero(df[escolhidas["lon"]])
coord_ok = lat.between(-90, 90) & lon.between(-180, 180)
if not coord_ok.any():
    st.error(t("cluster_error_no_coords").format(lat=escolhidas["lat"], lon=escolhidas["lon"]))
    st.page_link("pages/coordenadas.py", label=t("cluster_req_link"), icon=":material/my_location:")
    st.stop()

df["latitude"] = lat.where(coord_ok)
df["longitude"] = lon.where(coord_ok)
df["semana_epi"], df["ano_epi"] = semanas_epidemiologicas(datas)

# --------------------------------------------------------
# RESUMO DA BASE CARREGADA
# --------------------------------------------------------
validos = datas.notna() & coord_ok
periodo = f"{datas.min():%d/%m/%Y} – {datas.max():%d/%m/%Y}"
html(f"""
<div class="ds-grid ds-grid-4" style="margin-top: 6px">
    <div class="ds-card ds-mini"><div class="ds-icon"><i class="fi fi-rr-table-list"></i></div>
        <p><small>{t("cluster_summary_rows")}</small><br><b>{milhar(len(df))}</b></p></div>
    <div class="ds-card ds-mini"><div class="ds-icon"><i class="fi fi-rr-marker"></i></div>
        <p><small>{t("cluster_summary_coords")}</small><br><b>{milhar(int(coord_ok.sum()))}</b> ({coord_ok.mean():.0%})</p></div>
    <div class="ds-card ds-mini"><div class="ds-icon"><i class="fi fi-rr-calendar-lines"></i></div>
        <p><small>{t("cluster_summary_period")}</small><br><b>{periodo}</b></p></div>
    <div class="ds-card ds-mini"><div class="ds-icon"><i class="fi fi-rr-table-columns"></i></div>
        <p><small>{t("cluster_summary_columns")}</small><br><b>{escolhidas["data"]}, {escolhidas["lat"]}, {escolhidas["lon"]}</b></p></div>
</div>
""")
if (~validos).sum():
    st.caption(t("cluster_summary_dropped").format(n=int((~validos).sum())))

# --------------------------------------------------------
# CAMADAS DE REFERÊNCIA (opcional): pontos fixos e distritos sanitários
# --------------------------------------------------------
pontos_fixos = pd.DataFrame()
bairros_ds, extras_ds = None, []
with st.expander(t("layers_title"), icon=":material/layers:"):
    st.caption(t("layers_lead"))
    col_pontos, col_distritos = st.columns(2, gap="large")

    with col_pontos:
        st.markdown(f"**{t('layers_points_title')}**")
        st.caption(t("layers_points_help"))
        arquivos_pontos = st.file_uploader(
            t("layers_points_upload"), type=["csv", "xlsx"], accept_multiple_files=True, key="layers_points"
        )
        incluir_unidades = st.checkbox(t("layers_points_unidades"), key="layers_unidades")
        incluir_sedes = st.checkbox(t("layers_points_sedes"), key="layers_sedes")
        st.download_button(t("layers_points_template"), MODELO_PONTOS.encode("utf-8-sig"),
                           "modelo_pontos_fixos.csv", "text/csv", icon=":material/download:")

        fontes = [(arquivo.name, arquivo.getvalue()) for arquivo in arquivos_pontos or []]
        for incluir, arquivo in ((incluir_unidades, UNIDADES_SAUDE), (incluir_sedes, SEDES_DISTRITOS)):
            if incluir:
                fontes.append((arquivo.name, arquivo.read_bytes()))
        lidos = []
        for nome, dados in fontes:
            try:
                pontos = preparar_pontos(ler_base(dados, nome), nome)
            except Exception as erro:
                st.warning(t("layers_points_error").format(file=nome, error=erro))
                continue
            if pontos.empty:
                st.warning(t("layers_points_no_coords").format(file=nome))
            else:
                lidos.append(pontos)
        if lidos:
            pontos_fixos = pd.concat(lidos, ignore_index=True)
            contagem = pontos_fixos["_tipo"].value_counts()
            st.caption(t("layers_points_loaded").format(
                n=milhar(len(pontos_fixos)), k=len(contagem),
                types=", ".join(f"{tipo} ({milhar(int(n))})" for tipo, n in contagem.items()),
            ))

    with col_distritos:
        st.markdown(f"**{t('layers_districts_title')}**")
        st.caption(t("layers_districts_help"))
        usar_recife = st.checkbox(t("layers_districts_recife"), key="layers_districts_recife")
        arquivo_ds = st.file_uploader(t("layers_districts_upload"), type=["csv", "xlsx"], key="layers_districts")
        st.download_button(t("layers_districts_template"), MODELO_DISTRITOS.encode("utf-8-sig"),
                           "modelo_distritos.csv", "text/csv", icon=":material/download:")

        # Um arquivo enviado tem prioridade sobre a divisão pronta do Recife
        fonte_ds = (arquivo_ds.name, arquivo_ds.getvalue()) if arquivo_ds else \
            (BAIRROS_DISTRITOS.name, BAIRROS_DISTRITOS.read_bytes()) if usar_recife else None
        if fonte_ds:
            try:
                tabela_ds = ler_base(fonte_ds[1], fonte_ds[0])
                resultado = associar_distritos(tabela_ds, carregar_bairros())
            except Exception as erro:
                st.warning(t("layers_points_error").format(file=fonte_ds[0], error=erro))
            else:
                if resultado is None:
                    st.warning(t("layers_districts_missing_cols").format(cols=", ".join(map(str, tabela_ds.columns))))
                    # Arquivo de pontos (com coordenadas) enviado no campo errado
                    if detectar_coluna(tabela_ds.columns, ALIASES["lat"]) and detectar_coluna(tabela_ds.columns, ALIASES["lon"]):
                        st.info(t("layers_districts_points_hint"))
                elif resultado[1] is None:
                    st.warning(t("layers_districts_no_match"))
                else:
                    bairros_ds, municipio_ds, nao_encontrados, extras_ds = resultado
                    com_ds = bairros_ds["distrito"].notna()
                    st.caption(t("layers_districts_loaded").format(
                        n=int(com_ds.sum()), mun=municipio_ds, k=bairros_ds["distrito"].nunique()
                    ))
                    if (~com_ds).sum():
                        st.caption(t("layers_districts_unassigned").format(n=int((~com_ds).sum()), mun=municipio_ds))
                    if nao_encontrados:
                        st.warning(t("layers_districts_unmatched").format(names=", ".join(nao_encontrados)))

# --------------------------------------------------------
# PARÂMETROS DBSCAN
# --------------------------------------------------------
st.sidebar.header(t("cluster_sidebar_header"))

eps_km = st.sidebar.slider(
    t("cluster_eps_label"),
    min_value=0.05,
    max_value=5.0,
    value=0.3,
    step=0.05,
    help=t("cluster_eps_help")
)
eps = eps_km / 6371.0088  # conversão para radianos

min_samples = st.sidebar.slider(t("cluster_min_samples_label"), 2, 20, 5, 1)

# Abre no ano e na semana com mais casos com coordenadas, para o primeiro mapa já mostrar clusters
df_geo = df[validos]
anos_disp = sorted(df["ano_epi"].dropna().unique())
ano_padrao = df_geo["ano_epi"].mode().iloc[0] if not df_geo.empty else anos_disp[0]
ano_sel = st.sidebar.selectbox(t("cluster_year_label"), anos_disp, index=anos_disp.index(ano_padrao))

semanas_disp = sorted(df.loc[df["ano_epi"] == ano_sel, "semana_epi"].dropna().unique())
semanas_ano = df_geo.loc[df_geo["ano_epi"] == ano_sel, "semana_epi"]
semana_padrao = [semanas_ano.mode().iloc[0]] if not semanas_ano.empty else semanas_disp[:1]
semanas_sel = st.sidebar.multiselect(
    t("cluster_weeks_label"), semanas_disp, default=semana_padrao
)

df_filtro = df[(df["ano_epi"] == ano_sel) & (df["semana_epi"].isin(semanas_sel))].copy()

if df_filtro.empty:
    st.warning(t("cluster_warning_empty_period"))
    st.stop()

# --------------------------------------------------------
# CLUSTERIZAÇÃO (ignora coordenadas ausentes)
# --------------------------------------------------------
df_validos = df_filtro.dropna(subset=["latitude", "longitude"]).copy()
df_cluster = executar_clusterizacao(df_validos, eps, min_samples)

# --------------------------------------------------------
# MAPA INTERATIVO
# --------------------------------------------------------
# Enquadra os casos a até 50 km da mediana: alguns pontos geocodificados longe (outro estado)
# puxariam a média e abririam o mapa no lugar errado
centro = [df_cluster["latitude"].median(), df_cluster["longitude"].median()]
dist_km = 6371.0088 * np.hypot(
    np.radians(df_cluster["latitude"] - centro[0]),
    np.radians(df_cluster["longitude"] - centro[1]) * np.cos(np.radians(centro[0])),
)
perto = df_cluster[dist_km <= 50]
mapa = folium.Map(location=centro, zoom_start=12, tiles=None)
limites = None
if len(perto) > 1:
    limites = [[perto["latitude"].min(), perto["longitude"].min()],
               [perto["latitude"].max(), perto["longitude"].max()]]
    mapa.fit_bounds(limites)

# Mapas base gratuitos (sem chave de API); o primeiro é o padrão e os demais começam ocultos
# cross_origin carrega os tiles com CORS, sem o que o botão de imagem do mapa sairia sem o fundo
esri = "https://server.arcgisonline.com/ArcGIS/rest/services/{}/MapServer/tile/{{z}}/{{y}}/{{x}}"
atrib_esri = "Tiles &copy; Esri &mdash; Esri, HERE, Garmin, &copy; OpenStreetMap contributors"
folium.TileLayer(esri.format("Canvas/World_Light_Gray_Base"), attr=atrib_esri, name="Cinza claro",
                 cross_origin=True).add_to(mapa)
folium.TileLayer("OpenStreetMap", name="OpenStreetMap", show=False, cross_origin=True).add_to(mapa)
folium.TileLayer(esri.format("World_Street_Map"), attr=atrib_esri, name="Ruas", show=False,
                 cross_origin=True).add_to(mapa)
folium.TileLayer(esri.format("World_Imagery"), attr=atrib_esri, name="Satélite", show=False,
                 cross_origin=True).add_to(mapa)
# Nomes de bairros e ruas sobrepostos ao mapa base
folium.TileLayer(
    esri.format("Canvas/World_Light_Gray_Reference"), attr=atrib_esri,
    name="Nomes (bairros e ruas)", overlay=True, control=True, cross_origin=True,
).add_to(mapa)

cores = [
    "#C62828", "#1565C0", "#2E7D32", "#EF6C00", "#6A1B9A",
    "#00838F", "#AD1457", "#4527A0", "#0277BD", "#9E9D24",
    "#8E24AA", "#43A047", "#E53935", "#039BE5"
]

# Distritos por baixo dos casos e pontos fixos por cima, para não esconder os clusters
if bairros_ds is not None:
    desenhar_distritos(mapa, bairros_ds, extras_ds)
desenhar_clusters(mapa, df_cluster, cores, eps_km)
if not pontos_fixos.empty:
    desenhar_pontos_fixos(mapa, pontos_fixos)
folium.LayerControl(collapsed=True).add_to(mapa)
ControlesMapa(
    t("cluster_map_reset"), centro, limites,
    t("cluster_map_print"), f"denguesphere_{ano_sel}_{'_'.join(semanas_sel)}",
).add_to(mapa)

semanas_str = ", ".join(semanas_sel)
html(section("fi-rr-map", t("cluster_header_period").format(year=ano_sel, weeks=semanas_str)))
# returned_objects=[] evita recarregar a página a cada movimento do mapa
st_folium(mapa, height=620, use_container_width=True, returned_objects=[])

# --------------------------------------------------------
# ESTATÍSTICAS
# --------------------------------------------------------
html(section("fi-rr-stats", t("cluster_stats_title")))

if df_cluster["cluster"].max() < 0:
    st.info(t("cluster_info_no_clusters"))
    st.stop()

resumo = (
    df_cluster[df_cluster["cluster"] != -1]
    .groupby("cluster")
    .agg(
        N_Casos=("latitude", "count"),
        Semanas=("semana_epi", lambda x: ", ".join(sorted(set(x)))),
        Lat_Média=("latitude", "mean"),
        Lon_Média=("longitude", "mean"),
    )
    .reset_index()
    .sort_values("N_Casos", ascending=False)
)

total_casos = resumo["N_Casos"].sum()
maior_cluster = resumo.loc[resumo["N_Casos"].idxmax(), "cluster"]
maior_qtd = resumo["N_Casos"].max()
media_cluster = resumo["N_Casos"].mean()
mediana_cluster = resumo["N_Casos"].median()
desvio_cluster = resumo["N_Casos"].std()

k1, k2, k3, k4 = st.columns(4)
k1.metric(t("cluster_metric_n_clusters"), len(resumo))
k2.metric(t("cluster_metric_total_cases"), int(total_casos))
k3.metric(t("cluster_metric_noise"), int((df_cluster["cluster"] == -1).sum()))
k4.metric(t("cluster_metric_biggest_cluster_cases"), int(maior_qtd))

k5, k6, k7, k8 = st.columns(4)
k5.metric(t("cluster_metric_biggest_cluster_id"), int(maior_cluster))
k6.metric(t("cluster_metric_mean_cases"), f"{media_cluster:.2f}")
k7.metric(t("cluster_metric_median_cases"), f"{mediana_cluster:.2f}")
k8.metric(t("cluster_metric_sd_cases"), f"{desvio_cluster:.2f}" if pd.notna(desvio_cluster) else "–")

st.write("")
col_tabela, col_barras = st.columns([1, 1.3], gap="large")
with col_tabela:
    with st.container(border=True):
        st.markdown(f"**{t('cluster_table_title')}**")
        st.dataframe(resumo, hide_index=True, width="stretch", height=360)
with col_barras:
    with st.container(border=True):
        fig_bar = px.bar(
            resumo,
            x="cluster",
            y="N_Casos",
            color="N_Casos",
            color_continuous_scale=ESCALA,
            text="N_Casos",
            labels={
                "cluster": t("cluster_plot_cases_bar_x"),
                "N_Casos": t("cluster_plot_cases_bar_y")
            },
            title=t("cluster_plot_cases_bar_title")
        )
        fig_bar.update_traces(textposition="outside", marker_line_width=0)
        fig_bar.update_layout(showlegend=False, coloraxis_showscale=False, height=380)
        st.plotly_chart(estilizar(fig_bar), width="stretch")

col_centros, col_tendencia = st.columns(2, gap="large")
with col_centros:
    with st.container(border=True):
        fig_scatter = px.scatter(
            resumo,
            x="Lon_Média", y="Lat_Média",
            size="N_Casos",
            color="cluster",
            color_continuous_scale=ESCALA,
            hover_name="Semanas",
            labels={
                "Lon_Média": t("cluster_plot_centers_x"),
                "Lat_Média": t("cluster_plot_centers_y")
            },
            title=t("cluster_plot_centers_title")
        )
        fig_scatter.update_traces(marker=dict(line=dict(width=1, color="white")))
        fig_scatter.update_layout(height=380)
        st.plotly_chart(estilizar(fig_scatter), width="stretch")
with col_tendencia:
    with st.container(border=True):
        df_cluster["semana_num"] = df_cluster["semana_epi"].str.extract(r"S(\d+)").astype(float)
        tendencia = (
            df_cluster.groupby(["semana_num", "semana_epi"])
            .size()
            .reset_index(name="Casos")
            .sort_values("semana_num")
        )
        fig_line = px.line(
            tendencia,
            x="semana_epi",
            y="Casos",
            markers=True,
            title=t("cluster_plot_trend_title"),
            labels={
                "semana_epi": t("cluster_plot_trend_x"),
                "Casos": t("cluster_plot_trend_y")
            },
            line_shape="spline",
            color_discrete_sequence=["#0d47a1"]
        )
        fig_line.update_traces(line=dict(width=3), marker=dict(size=8, color="#00acc1"))
        fig_line.update_layout(height=380)
        st.plotly_chart(estilizar(fig_line), width="stretch")

# ------------------------------------------------------------
# ANÁLISE AVANÇADA DE QUALIDADE E ESTABILIDADE DOS CLUSTERS
# ------------------------------------------------------------
html(section("fi-rr-microscope", t("cluster_advanced_title")))
st.caption(t("cluster_advanced_caption"))

mostrar_analise_avancada = st.toggle(
    t("cluster_advanced_toggle"),
    value=False,
    key="toggle_analise_avancada"
)

if mostrar_analise_avancada:
    # ignora ruídos
    df_sil = df_cluster[df_cluster["cluster"] != -1].copy()

    # precisa de pelo menos 2 clusters
    if df_sil["cluster"].nunique() < 2:
        st.info(t("cluster_info_silhouette_not_defined"))
    else:
        coords_rad = np.radians(df_sil[["latitude", "longitude"]].values)
        labels = df_sil["cluster"].values

        silhouette_global = silhouette_score(coords_rad, labels, metric="haversine")
        df_sil["silhouette"] = silhouette_samples(coords_rad, labels, metric="haversine")

        # ------------------------------------------------------------
        # BLOCO 1 - SILHOUETTE
        # ------------------------------------------------------------
        with st.container(border=True):
            st.markdown(f"### {t('cluster_silhouette_title')}")
            st.caption(t("cluster_silhouette_caption"))

            colS1, colS2 = st.columns([1, 2], gap="large")

            with colS1:
                st.metric(t("cluster_silhouette_metric"), f"{silhouette_global:.3f}")

                if silhouette_global >= 0.70:
                    st.success(t("cluster_silhouette_interp_high"))
                elif silhouette_global >= 0.50:
                    st.info(t("cluster_silhouette_interp_good"))
                elif silhouette_global >= 0.30:
                    st.warning(t("cluster_silhouette_interp_mid"))
                else:
                    st.error(t("cluster_silhouette_interp_low"))

            with colS2:
                st.write(t("cluster_silhouette_explanation"))

            st.markdown(f"#### {t('cluster_silhouette_dist_title')}")

            fig_sil = px.box(
                df_sil,
                x="cluster",
                y="silhouette",
                points="all",
                color_discrete_sequence=["#00838f"],
                labels={
                    "cluster": t("cluster_silhouette_label_cluster"),
                    "silhouette": t("cluster_silhouette_label_value")
                }
            )
            fig_sil.update_layout(margin=dict(l=20, r=20, t=20, b=20), title=None)
            st.plotly_chart(estilizar(fig_sil), width="stretch")

        # ------------------------------------------------------------
        # BLOCO 2 - ARI
        # ------------------------------------------------------------
        with st.container(border=True):
            st.markdown(f"### {t('cluster_ari_title')}")
            st.caption(t("cluster_ari_caption"))

            if "mostrar_ari" not in st.session_state:
                st.session_state["mostrar_ari"] = False

            colA1, colA2 = st.columns([1, 3], gap="large")

            with colA1:
                if st.button(
                    t("cluster_ari_button"),
                    width="stretch",
                    type="primary",
                    key="btn_calcular_ari"
                ):
                    st.session_state["mostrar_ari"] = True

            with colA2:
                st.write(t("cluster_ari_help"))

            if st.session_state["mostrar_ari"]:
                with st.spinner(t("cluster_ari_spinner")):
                    resultados_ari = avaliar_estabilidade_ari(df_validos, eps, min_samples)

                if resultados_ari:
                    melhor_ari = max(ari for _, _, ari in resultados_ari)

                    st.markdown(f"#### {t('cluster_ari_results_title')}")
                    cols_ari = st.columns(len(resultados_ari))

                    for col, (param, var, ari) in zip(cols_ari, resultados_ari):
                        with col:
                            st.metric(
                                label=f"{param} = {var}",
                                value=f"{ari:.3f}",
                                delta=t("cluster_ari_best_result") if ari == melhor_ari else None
                            )

                    st.markdown(f"#### {t('cluster_ari_interp_title')}")
                    if melhor_ari >= 0.80:
                        st.success(t("cluster_ari_interp_high"))
                    elif melhor_ari >= 0.65:
                        st.info(t("cluster_ari_interp_mid"))
                    else:
                        st.warning(t("cluster_ari_interp_low"))
