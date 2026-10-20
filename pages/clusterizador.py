import streamlit as st
import pandas as pd
import numpy as np
import io
from sklearn.cluster import DBSCAN
import folium
from folium import Circle
from streamlit_folium import st_folium
import plotly.express as px
from i18n import t
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.metrics import adjusted_rand_score
from ui import inject_styles, html, page_header, section, mini_cards, footer

# Escala de cor dos gráficos, na paleta do app
ESCALA = ["#b2ebf2", "#00acc1", "#0d47a1"]

inject_styles()
page_header("fi-rr-chart-network", t("cluster_title"), t("cluster_lead"))


# ------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------------------------------------
def calcular_semana_epi(data):
    """Retorna (semana_epi, ano_epi) padronizada S01–S52"""
    if pd.isna(data):
        return None, None
    data = pd.to_datetime(data, errors="coerce", dayfirst=True)
    if pd.isna(data):
        return None, None
    iso = data.isocalendar()
    return f"S{iso.week:02d}", iso.year


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
    footer(t("app_footer"))
    st.stop()

df = ler_base(uploaded_file.getvalue(), uploaded_file.name).copy()

# renomeia colunas para padrão esperado (inclui o nome usado nos dados abertos do Recife)
df.rename(columns={"lat": "latitude", "long": "longitude"}, inplace=True)
if "dt_notificacao" not in df.columns and "dt_notific" in df.columns:
    df.rename(columns={"dt_notific": "dt_notificacao"}, inplace=True)

if "dt_notificacao" not in df.columns:
    st.error(t("cluster_error_dt"))
    st.stop()
if not {"latitude", "longitude"}.issubset(df.columns):
    st.error(t("cluster_error_coords"))
    st.stop()

# adiciona colunas epidemiológicas
semanas, anos = zip(*df["dt_notificacao"].apply(calcular_semana_epi))
df["semana_epi"], df["ano_epi"] = semanas, anos

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

anos_disp = sorted(df["ano_epi"].dropna().unique())
ano_sel = st.sidebar.selectbox(t("cluster_year_label"), anos_disp)

semanas_disp = sorted(df.loc[df["ano_epi"] == ano_sel, "semana_epi"].dropna().unique())
semanas_sel = st.sidebar.multiselect(
    t("cluster_weeks_label"), semanas_disp, default=semanas_disp[:1]
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
centro = [df_cluster["latitude"].mean(), df_cluster["longitude"].mean()]
mapa = folium.Map(location=centro, zoom_start=12, tiles=None)

# Mapas base gratuitos (sem chave de API); o primeiro é o padrão e os demais começam ocultos
esri = "https://server.arcgisonline.com/ArcGIS/rest/services/{}/MapServer/tile/{{z}}/{{y}}/{{x}}"
atrib_esri = "Tiles &copy; Esri &mdash; Esri, HERE, Garmin, &copy; OpenStreetMap contributors"
folium.TileLayer(esri.format("Canvas/World_Light_Gray_Base"), attr=atrib_esri, name="Cinza claro").add_to(mapa)
folium.TileLayer("OpenStreetMap", name="OpenStreetMap", show=False).add_to(mapa)
folium.TileLayer(esri.format("World_Street_Map"), attr=atrib_esri, name="Ruas", show=False).add_to(mapa)
folium.TileLayer(esri.format("World_Imagery"), attr=atrib_esri, name="Satélite", show=False).add_to(mapa)
# Nomes de bairros e ruas sobrepostos ao mapa base
folium.TileLayer(
    esri.format("Canvas/World_Light_Gray_Reference"), attr=atrib_esri,
    name="Nomes (bairros e ruas)", overlay=True, control=True,
).add_to(mapa)

cores = [
    "#C62828", "#1565C0", "#2E7D32", "#EF6C00", "#6A1B9A",
    "#00838F", "#AD1457", "#4527A0", "#0277BD", "#9E9D24",
    "#8E24AA", "#43A047", "#E53935", "#039BE5"
]

desenhar_clusters(mapa, df_cluster, cores, eps_km)
folium.LayerControl(collapsed=True).add_to(mapa)

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
    footer(t("app_footer"))
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

# ------------------------------------------------------------
# RODAPÉ
# ------------------------------------------------------------
footer(t("app_footer"))
