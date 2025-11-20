import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from shapely.geometry import MultiPoint
import folium
from folium import Polygon, Circle
from streamlit_folium import st_folium
import plotly.express as px
from datetime import datetime


st.markdown("""
<style>
.block-container {
    padding-top: 3rem !important;
    padding-bottom: 1rem !important;
}
h1 {
    text-align: left;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.title("Clusterização Geográfica de Casos de Dengue")

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


# ------------------------------------------------------------
# UPLOAD E PRÉ-PROCESSAMENTO
# ------------------------------------------------------------
uploaded_file = st.file_uploader("Selecione um arquivo CSV ou XLSX", type=["csv", "xlsx"])

if uploaded_file:
    # leitura 
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # renomeia colunas para padrão esperado
    df.rename(columns={"lat": "latitude", "long": "longitude"}, inplace=True)

    if "dt_notificacao" not in df.columns:
        st.error("A base precisa conter a coluna 'dt_notificacao'.")
        st.stop()

    # adiciona colunas epidemiológicas
    semanas, anos = zip(*df["dt_notificacao"].apply(calcular_semana_epi))
    df["semana_epi"], df["ano_epi"] = semanas, anos

    # --------------------------------------------------------
    # PARÂMETROS DBSCAN
    # --------------------------------------------------------
    st.sidebar.header("Parâmetros DBSCAN")

    eps_km = st.sidebar.slider(
        "EPS (distância em quilômetros)",
        min_value=0.05,
        max_value=5.0,
        value=0.3,
        step=0.05,
        help="Define o raio máximo de vizinhança entre casos (em quilômetros). "
             "Valores menores detectam microáreas; valores maiores agrupam bairros próximos."
    )
    eps = eps_km / 6371.0088  # conversão para radianos

    min_samples = st.sidebar.slider("Mínimo de pontos por cluster", 2, 20, 5, 1)

    anos_disp = sorted(df["ano_epi"].dropna().unique())
    ano_sel = st.sidebar.selectbox("Ano epidemiológico", anos_disp)

    semanas_disp = sorted(df.loc[df["ano_epi"] == ano_sel, "semana_epi"].dropna().unique())
    semanas_sel = st.sidebar.multiselect(
        "Semanas epidemiológicas", semanas_disp, default=semanas_disp[:1]
    )

    df_filtro = df[(df["ano_epi"] == ano_sel) & (df["semana_epi"].isin(semanas_sel))].copy()

    if df_filtro.empty:
        st.warning("Não há registros para o período selecionado.")
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
    mapa = folium.Map(location=centro, zoom_start=12, tiles="CartoDB positron")

    cores = [
        "#C62828", "#1565C0", "#2E7D32", "#EF6C00", "#6A1B9A",
        "#00838F", "#AD1457", "#4527A0", "#0277BD", "#9E9D24",
        "#8E24AA", "#43A047", "#E53935", "#039BE5"
    ]

    desenhar_clusters(mapa, df_cluster, cores, eps_km)

    st.markdown(f"### Ano: {ano_sel} | Semanas selecionadas: {', '.join(semanas_sel)}")
    st_folium(mapa, width=1200, height=650)

    # --------------------------------------------------------
    # ESTATÍSTICAS
    # --------------------------------------------------------
    st.markdown("### Estatísticas Descritivas dos Clusters")

    if df_cluster["cluster"].max() >= 0:
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

        col1, col2 = st.columns([1.4, 1])
        with col1:
            st.dataframe(resumo, hide_index=True, use_container_width=True)
        with col2:
            st.metric("Clusters identificados", len(resumo))
            st.metric("Pontos isolados (ruído)", int((df_cluster["cluster"] == -1).sum()))

        # --------------------------------------------------------
        # ESTATÍSTICAS COMPLEMENTARES
        # --------------------------------------------------------
        st.markdown("#### Estatísticas Complementares dos Clusters")
        total_casos = resumo["N_Casos"].sum()
        maior_cluster = resumo.loc[resumo["N_Casos"].idxmax(), "cluster"]
        maior_qtd = resumo["N_Casos"].max()
        media_cluster = resumo["N_Casos"].mean()
        mediana_cluster = resumo["N_Casos"].median()
        desvio_cluster = resumo["N_Casos"].std()

        colA, colB, colC = st.columns(3)
        with colA:
            st.metric("Total de Casos Agrupados", int(total_casos))
            st.metric("Maior Cluster (ID)", int(maior_cluster))
        with colB:
            st.metric("Casos no Maior Cluster", int(maior_qtd))
            st.metric("Média de Casos/Cluster", f"{media_cluster:.2f}")
        with colC:
            st.metric("Mediana de Casos/Cluster", f"{mediana_cluster:.2f}")
            st.metric("Desvio Padrão", f"{desvio_cluster:.2f}")

        # --------------------------------------------------------
        # GRÁFICOS
        # --------------------------------------------------------
        st.markdown("#### Distribuição de Casos por Cluster")
        fig_bar = px.bar(
            resumo,
            x="cluster",
            y="N_Casos",
            color="N_Casos",
            color_continuous_scale="Blues",
            text="N_Casos",
            labels={"cluster": "Cluster", "N_Casos": "Número de Casos"},
            title="Distribuição de Casos por Cluster"
        )
        fig_bar.update_traces(textposition="outside", marker_line_color="black", marker_line_width=1)
        fig_bar.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("#### Pontos Focais (Latitude e Longitude Médias)")
        fig_scatter = px.scatter(
            resumo,
            x="Lon_Média", y="Lat_Média",
            size="N_Casos",
            color="cluster",
            color_continuous_scale="Viridis",
            hover_name="Semanas",
            labels={"Lon_Média": "Longitude Média", "Lat_Média": "Latitude Média"},
            title="Centros Geográficos dos Clusters"
        )
        fig_scatter.update_traces(marker=dict(line=dict(width=1, color='black')))
        fig_scatter.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("#### Evolução de Casos por Semana Epidemiológica")
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
            title="Tendência de Casos por Semana Epidemiológica",
            labels={"semana_epi": "Semana Epidemiológica", "Casos": "Número de Casos"},
            line_shape="spline",
            color_discrete_sequence=["#E53935"]
        )
        fig_line.update_traces(line=dict(width=3))
        fig_line.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_line, use_container_width=True)

    else:
        st.info("Nenhum cluster identificado para os parâmetros atuais.")
else:
    st.info("Carregue a base de dados para iniciar.")

# ------------------------------------------------------------
# RODAPÉ
# ------------------------------------------------------------
st.info("Versão 1.0 – Desenvolvido pelo Grupo de Pesquisa em Sistemas de Informação e Decisão (GPSID) - PPGEP/UFPE.")
