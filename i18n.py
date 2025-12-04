# i18n.py
import streamlit as st

# -------------------------------------------------
# DICIONÁRIO DE TRADUÇÕES
# -------------------------------------------------
TRANSLATIONS = {
    "pt": {
        # ---------------- Globais / Navegação ----------------
        "app_title": "DengueSphere v1.0",
        "nav_home": "Início",
        "nav_coords": "Gerar Coordenadas por CEP",
        "nav_cluster": "Clusterizador",
        "nav_about": "Sobre o Projeto",
        "lang_label": "Idioma / Language",
        "lang_pt": "Português",
        "lang_en": "Inglês",

        # ---------------- Página Home ----------------
        "home_title_h2": "DengueSphere v1.0",
        "home_subtitle": "Sistema Interativo de Clusterização Espacial da Dengue",
        "home_welcome_header": "Bem-vindo ao DengueSphere v1.0",
        "home_main_text": """
O **DengueSphere** é uma plataforma interativa para análise espacial e clusterização de casos de dengue,
baseada no algoritmo **DBSCAN (Density-Based Spatial Clustering)**.

Com o sistema, é possível:

- Carregar bases de dados geográficas (latitude, longitude e data);
- Definir parâmetros de clusterização;
- Visualizar agrupamentos em mapas interativos;
- Gerar estatísticas de distribuição dos clusters.

> **Dica:** Caso sua base **não possua coordenadas geográficas**, utilize o módulo **"Coordenadas por CEP"** para **gerar as coordenadas automaticamente**, **baixar a base atualizada** e depois **inseri-la no módulo "Clusterizador"**.  
> Dependendo do tamanho da base e da taxa de requisições, o processo pode **levar alguns minutos**.

Utilize o menu no topo para navegar entre as seções.
""",
        "home_footer_info": "Versão atual: 1.0 – Desenvolvido pelo Grupo de Pesquisa em Sistemas de Informação e Decisão (GPSID) - PPGEP/UFPE.",

        # ---------------- Página Sobre ----------------
        "about_title": "Sobre o DengueSphere",
        "about_infobox": """
**DengueSphere** é uma plataforma interativa desenvolvida para 
apoiar a análise, o tratamento e a visualização de dados geográficos relacionados à dengue. 
Seu objetivo é facilitar a integração de informações, o mapeamento de áreas de risco 
e o suporte à tomada de decisões estratégicas no controle da doença.
""",
        "about_team_header": "Equipe de desenvolvimento",
        "about_team_list": """
- **Eduardo da Silva** — Doutorando do Programa de Pós-Graduação em Engenharia de Produção (PPGEP/UFPE) - (2025 - Atual) 
- **Profa. Dra. Maísa Mendonça Silva** — Orientadora, Docente Permanente do PPGEP/UFPE  
- **Grupo de Pesquisa em Sistemas de Informação e Decisão (GPSID)** — PPGEP/UFPE  
""",
        "about_objectives_header": "Objetivos principais",
        "about_objectives_list": """
- Integrar dados geográficos e epidemiológicos.  
- Permitir análises espaciais e temporais de casos de dengue.  
- Apoiar gestores públicos e pesquisadores na tomada de decisão.  
- Disponibilizar ferramentas modulares, incluindo:
  - Tratamento de CEP e Geocodificação  
  - Clusterização geográfica  
  - Visualização interativa em mapas
  - Análises estatísticas
""",
        "about_footer": """
Versão 1.0 – Desenvolvido por Eduardo da Silva sob orientação da Profa. Dra. Maísa Mendonça Silva.<br>
Grupo de Pesquisa em Sistemas de Informação e Decisão (GPSID) – PPGEP/UFPE.
""",


        # ---------------- Página Coordenadas ----------------
        "coords_title": "Tratamento de CEP e Geocodificação",
        "coords_intro": """
Esta ferramenta permite:
- Escolher colunas com CEP, Rua e Bairro de qualquer planilha Excel  
- Corrigir nomes de ruas automaticamente (fuzzy matching)  
- Obter coordenadas geográficas via OpenStreetMap (Nominatim)  
- Gerar e baixar um arquivo Excel com os resultados geocodificados
""",
        "coords_uploader_label": "Selecione o arquivo Excel (.xlsx)",
        "coords_file_loaded": "Arquivo carregado com {n_rows} linhas e {n_cols} colunas.",
        "coords_select_columns_subheader": "Selecione as colunas correspondentes",
        "coords_select_cep": "Coluna do CEP",
        "coords_select_rua": "Coluna do nome da rua/logradouro",
        "coords_select_bairro": "Coluna do bairro",
        "coords_button_start": "Iniciar Geocodificação",
        "coords_processing_info": "Processando endereços, isso pode levar alguns minutos dependendo da base...",
        "coords_processing_done": "Geocodificação concluída.",
        "coords_download_button": "Baixar arquivo Excel",
        "coords_no_file_info": "Envie um arquivo Excel para começar.",
        "coords_logo_warning": "Logo não encontrada. Coloque o arquivo **logo.png** na pasta raiz do projeto.",

        # ---------------- Página Clusterizador ----------------
        "cluster_title": "Clusterização Geográfica de Casos de Dengue",
        "cluster_upload_label": "Selecione um arquivo CSV ou XLSX",
        "cluster_error_dt": "A base precisa conter a coluna 'dt_notificacao'.",
        "cluster_sidebar_header": "Parâmetros DBSCAN",
        "cluster_eps_label": "EPS (distância em quilômetros)",
        "cluster_eps_help": "Define o raio máximo de vizinhança entre casos (em quilômetros). Valores menores detectam microáreas; valores maiores agrupam bairros próximos.",
        "cluster_min_samples_label": "Mínimo de pontos por cluster",
        "cluster_year_label": "Ano epidemiológico",
        "cluster_weeks_label": "Semanas epidemiológicas",
        "cluster_warning_empty_period": "Não há registros para o período selecionado.",
        "cluster_header_period": "Ano: {year} | Semanas selecionadas: {weeks}",
        "cluster_stats_title": "Estatísticas Descritivas dos Clusters",
        "cluster_metric_n_clusters": "Clusters identificados",
        "cluster_metric_noise": "Pontos isolados (ruído)",
        "cluster_stats_comp_title": "Estatísticas Complementares dos Clusters",
        "cluster_metric_total_cases": "Total de Casos Agrupados",
        "cluster_metric_biggest_cluster_id": "Maior Cluster (ID)",
        "cluster_metric_biggest_cluster_cases": "Casos no Maior Cluster",
        "cluster_metric_mean_cases": "Média de Casos/Cluster",
        "cluster_metric_median_cases": "Mediana de Casos/Cluster",
        "cluster_metric_sd_cases": "Desvio Padrão",
        "cluster_plot_cases_bar_title": "Distribuição de Casos por Cluster",
        "cluster_plot_cases_bar_x": "Cluster",
        "cluster_plot_cases_bar_y": "Número de Casos",
        "cluster_plot_centers_title": "Centros Geográficos dos Clusters",
        "cluster_plot_centers_x": "Longitude Média",
        "cluster_plot_centers_y": "Latitude Média",
        "cluster_plot_trend_title": "Tendência de Casos por Semana Epidemiológica",
        "cluster_plot_trend_x": "Semana Epidemiológica",
        "cluster_plot_trend_y": "Número de Casos",
        "cluster_info_no_clusters": "Nenhum cluster identificado para os parâmetros atuais.",
        "cluster_info_upload_start": "Carregue a base de dados para iniciar.",
        "cluster_footer": "Versão 1.0 – Desenvolvido pelo Grupo de Pesquisa em Sistemas de Informação e Decisão (GPSID) - PPGEP/UFPE.",
    },

    "en": {
        # ---------------- Global / Navigation ----------------
        "app_title": "DengueSphere v1.0",
        "nav_home": "Home",
        "nav_coords": "Generate Coordinates by ZIP Code",
        "nav_cluster": "Clustering Tool",
        "nav_about": "About the Project",
        "lang_label": "Idioma / Language",
        "lang_pt": "Portuguese",
        "lang_en": "English",

        # ---------------- Home Page ----------------
        "home_title_h2": "DengueSphere v1.0",
        "home_subtitle": "Interactive System for Spatial Clustering of Dengue Cases",
        "home_welcome_header": "Welcome to DengueSphere v1.0",
        "home_main_text": """
**DengueSphere** is an interactive platform for spatial analysis and clustering of dengue cases,
based on the **DBSCAN (Density-Based Spatial Clustering)** algorithm.

With the system, you can:

- Load geographic datasets (latitude, longitude and date);
- Define clustering parameters;
- Visualize clusters on interactive maps;
- Generate statistics on the distribution of clusters.

> **Tip:** If your dataset **does not contain geographic coordinates**, use the **\"Coordinates by ZIP Code\"** module to **automatically generate coordinates**, **download the updated dataset**, and then **load it into the \"Clustering Tool\" module**.  
> Depending on the dataset size and request rate, this process may **take a few minutes**.

Use the top menu to navigate between sections.
""",
        "home_footer_info": "Current version: 1.0 – Developed by the Information and Decision Systems Research Group (GPSID) - PPGEP/UFPE.",

        # ---------------- About Page ----------------
        "about_title": "About DengueSphere",
        "about_infobox": """
**DengueSphere** is an interactive platform developed to support the analysis, processing and visualization 
of geographic data related to dengue. Its goal is to facilitate the integration of information, 
the mapping of risk areas, and to support strategic decision-making in disease control.
""",
        "about_team_header": "Development team",
        "about_team_list": """
- **Eduardo da Silva** — PhD student, Graduate Program in Production Engineering (PPGEP/UFPE) - (2025 - Present) 
- **Prof. Maísa Mendonça Silva, PhD** — Supervisor, permanent faculty member of PPGEP/UFPE  
- **Information and Decision Systems Research Group (GPSID)** — PPGEP/UFPE  
""",
        "about_objectives_header": "Main objectives",
        "about_objectives_list": """
- Integrate geographic and epidemiological data.  
- Enable spatial and temporal analyses of dengue cases.  
- Support public managers and researchers in decision-making.  
- Provide modular tools, including:
  - ZIP code processing and geocoding  
  - Geographic clustering  
  - Interactive map visualization
  - Statistical analyses
""",
        "about_footer": """
Version 1.0 – Developed by Eduardo da Silva under the supervision of Prof. Maísa Mendonça Silva, PhD.<br>
Information and Decision Systems Research Group (GPSID) – PPGEP/UFPE.
""",


        # ---------------- Coordinates Page ----------------
        "coords_title": "ZIP Code Processing and Geocoding",
        "coords_intro": """
This tool allows you to:
- Choose columns with ZIP Code, Street and Neighborhood from any Excel spreadsheet  
- Automatically correct street names (fuzzy matching)  
- Obtain geographic coordinates via OpenStreetMap (Nominatim)  
- Generate and download an Excel file with geocoded results
""",
        "coords_uploader_label": "Select the Excel file (.xlsx)",
        "coords_file_loaded": "File loaded with {n_rows} rows and {n_cols} columns.",
        "coords_select_columns_subheader": "Select the corresponding columns",
        "coords_select_cep": "ZIP Code column",
        "coords_select_rua": "Street / Address column",
        "coords_select_bairro": "Neighborhood column",
        "coords_button_start": "Start Geocoding",
        "coords_processing_info": "Processing addresses; this may take a few minutes depending on the dataset...",
        "coords_processing_done": "Geocoding completed.",
        "coords_download_button": "Download Excel file",
        "coords_no_file_info": "Upload an Excel file to begin.",
        "coords_logo_warning": "Logo not found. Please place the **logo.png** file in the project root folder.",

        # ---------------- Cluster Page ----------------
        "cluster_title": "Geographical Clustering of Dengue Cases",
        "cluster_upload_label": "Select a CSV or XLSX file",
        "cluster_error_dt": "The dataset must contain the 'dt_notificacao' column.",
        "cluster_sidebar_header": "DBSCAN Parameters",
        "cluster_eps_label": "EPS (distance in kilometers)",
        "cluster_eps_help": "Defines the maximum neighborhood radius between cases (in kilometers). Smaller values detect micro-areas; larger values group nearby neighborhoods.",
        "cluster_min_samples_label": "Minimum points per cluster",
        "cluster_year_label": "Epidemiological year",
        "cluster_weeks_label": "Epidemiological weeks",
        "cluster_warning_empty_period": "There are no records for the selected period.",
        "cluster_header_period": "Year: {year} | Selected weeks: {weeks}",
        "cluster_stats_title": "Descriptive Statistics of Clusters",
        "cluster_metric_n_clusters": "Identified clusters",
        "cluster_metric_noise": "Isolated points (noise)",
        "cluster_stats_comp_title": "Additional Cluster Statistics",
        "cluster_metric_total_cases": "Total Grouped Cases",
        "cluster_metric_biggest_cluster_id": "Largest Cluster (ID)",
        "cluster_metric_biggest_cluster_cases": "Cases in Largest Cluster",
        "cluster_metric_mean_cases": "Average Cases/Cluster",
        "cluster_metric_median_cases": "Median Cases/Cluster",
        "cluster_metric_sd_cases": "Standard Deviation",
        "cluster_plot_cases_bar_title": "Distribution of Cases per Cluster",
        "cluster_plot_cases_bar_x": "Cluster",
        "cluster_plot_cases_bar_y": "Number of Cases",
        "cluster_plot_centers_title": "Geographical Centers of Clusters",
        "cluster_plot_centers_x": "Mean Longitude",
        "cluster_plot_centers_y": "Mean Latitude",
        "cluster_plot_trend_title": "Trend of Cases by Epidemiological Week",
        "cluster_plot_trend_x": "Epidemiological Week",
        "cluster_plot_trend_y": "Number of Cases",
        "cluster_info_no_clusters": "No clusters identified for the current parameters.",
        "cluster_info_upload_start": "Upload a dataset to start.",
        "cluster_footer": "Version 1.0 – Developed by the Information and Decision Systems Research Group (GPSID) - PPGEP/UFPE.",
    },
}

# -------------------------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------------------------
def init_lang():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "pt"


def lang_selector():
    """
    Exibe um seletor de idioma no topo da tela e atualiza st.session_state['lang'].
    """
    init_lang()
    col1, col2 = st.columns([8, 2])
    with col2:
        lang = st.selectbox(
            TRANSLATIONS[st.session_state["lang"]]["lang_label"],
            options=["pt", "en"],
            index=["pt", "en"].index(st.session_state["lang"]),
            format_func=lambda x: TRANSLATIONS[x]["lang_pt"] if x == "pt" else TRANSLATIONS[x]["lang_en"],
        )
    st.session_state["lang"] = lang
    return lang


def t(key: str) -> str:
    """
    Retorna o texto traduzido para a chave informada.
    Se a chave não existir, retorna a própria chave.
    """
    init_lang()
    lang = st.session_state.get("lang", "pt")
    return TRANSLATIONS.get(lang, {}).get(key, key)
