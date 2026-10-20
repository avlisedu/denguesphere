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
        "nav_coords": "Localizar Coordenadas",
        "nav_cluster": "Clusterizador",
        "nav_about": "Sobre o Projeto",
        "lang_label": "Idioma / Language",
        "lang_pt": "Português",
        "lang_en": "Inglês",

        # ---------------- Página Home ----------------
        "home_eyebrow": "Plataforma de Vigilância Epidemiológica",
        "home_title": "DengueSphere",
        "home_subtitle": "Sistema Interativo de Clusterização Espacial da Dengue",
        "home_lead": "Identifique aglomerados de casos de dengue a partir de dados geográficos, com o algoritmo DBSCAN, mapas interativos e estatísticas para apoiar a tomada de decisão.",

        "home_start_header": "Comece por aqui",
        "home_link_coords": "Localizar Coordenadas",
        "home_link_cluster": "Abrir o Clusterizador",
        "home_link_about": "Sobre o projeto",

        "home_steps_header": "Como funciona",
        "home_step1_title": "Carregue sua base",
        "home_step1_text": "Envie uma planilha (.csv ou .xlsx) com latitude, longitude e data dos casos.",
        "home_step2_title": "Gere as coordenadas",
        "home_step2_text": "Sem latitude e longitude? Converta CEP e endereço em coordenadas automaticamente.",
        "home_step2_tag": "Se necessário",
        "home_step3_title": "Ajuste os parâmetros",
        "home_step3_text": "Defina o raio (km) e o número mínimo de casos que formam um cluster no DBSCAN.",
        "home_step4_title": "Analise os resultados",
        "home_step4_text": "Visualize os clusters no mapa e consulte as estatísticas de distribuição.",

        "home_tip": "<strong>Dica:</strong> se sua base não tiver coordenadas geográficas, use o módulo <strong>Localizar Coordenadas</strong> para gerá-las, baixe a base atualizada e carregue-a no <strong>Clusterizador</strong>. Dependendo do tamanho da base e da taxa de requisições, o processo pode levar alguns minutos.",

        "home_footer": "Desenvolvido pelo Grupo de Pesquisa em Sistemas de Informação e Decisão (GPSID) – PPGEP/UFPE",

        # ---------------- Página Sobre ----------------
        "about_eyebrow": "Sistema de Apoio à Decisão · Vigilância Epidemiológica",
        "about_title": "Sobre o DengueSphere",
        "about_lead": "Plataforma interativa para apoiar a análise, o tratamento e a visualização de dados geográficos da dengue, integrando informações, mapeando áreas de risco e apoiando decisões estratégicas no controle da doença.",

        "about_modules_header": "Módulos da plataforma",
        "about_mod_geo_title": "Geocodificação",
        "about_mod_geo_text": "Tratamento de CEP e endereços com correção automática de ruas e coordenadas via OpenStreetMap.",
        "about_mod_cluster_title": "Clusterização espacial",
        "about_mod_cluster_text": "Identificação de aglomerados de casos com o algoritmo DBSCAN e parâmetros ajustáveis.",
        "about_mod_map_title": "Mapas interativos",
        "about_mod_map_text": "Visualização dos clusters sobre mapas base, com camadas de bairros e navegação livre.",
        "about_mod_stats_title": "Análises estatísticas",
        "about_mod_stats_text": "Distribuição espacial e temporal dos clusters para apoiar a priorização de ações.",

        "about_objectives_header": "Objetivos",
        "about_obj_1": "Integrar dados geográficos e epidemiológicos.",
        "about_obj_2": "Permitir análises espaciais e temporais de casos de dengue.",
        "about_obj_3": "Apoiar gestores públicos e pesquisadores na tomada de decisão.",

        "about_pub_header": "Publicação",
        "about_pub_badge": "Artigo de conferência",
        "about_pub_published": "Publicado nos anais do",
        "about_pub_pages": "Vol. 1, pp. 154–160",
        "about_pub_cite_hint": "Ao usar o DengueSphere em trabalhos acadêmicos, cite:",
        "about_pub_bibtex": "Ver BibTeX",

        "about_releases_header": "Notas de versão",
        "about_release_current": "Versão atual",
        "about_release_future": "Próximas versões",
        "about_release_future_title": "Em desenvolvimento",
        "about_release_10_items": [
            "Geocodificação de CEP e endereços via OpenStreetMap, com correção automática de nomes de ruas",
            "Clusterização espacial de casos com DBSCAN e parâmetros ajustáveis (raio e mínimo de casos)",
            "Mapas interativos com seleção de mapa base e camada de bairros",
            "Estatísticas de distribuição dos clusters e avaliação de estabilidade (ARI)",
            "Interface em português e inglês",
        ],
        "about_release_future_items": [
            "Nowcasting para corrigir o atraso de notificação e evitar clusters subestimados nas semanas mais recentes",
            "Formação de clusters a partir de previsões (forecasting), antecipando aglomerados de casos",
        ],

        "about_team_header": "Equipe",
        "about_team_eduardo_role": "Doutorando no Programa de Pós-Graduação em Engenharia de Produção (PPGEP/UFPE) · 2025 – atual",
        "about_team_maisa_name": "Profa. Dra. Maisa Mendonça Silva",
        "about_team_maisa_role": "Orientadora · Docente permanente do PPGEP/UFPE",
        "about_team_gpsid_name": "GPSID",
        "about_team_gpsid_role": "Grupo de Pesquisa em Sistemas de Informação e Decisão · PPGEP/UFPE",

        "about_footer": "Desenvolvido por Eduardo da Silva sob orientação da Profa. Dra. Maisa Mendonça Silva · GPSID – PPGEP/UFPE",


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
    
            # ---------------- Análise Avançada / Validação ----------------
        "cluster_advanced_title": "Análise técnica do clustering",
        "cluster_advanced_caption": "Seção voltada à validação metodológica do modelo. Para uso técnico, pesquisa e apoio à interpretação dos agrupamentos.",
        "cluster_advanced_toggle": "Mostrar análise avançada (Silhouette e ARI)",
        "cluster_info_silhouette_not_defined": "A análise de Silhouette não pode ser calculada para a configuração atual.",

        # ---------------- Silhouette ----------------
        "cluster_silhouette_title": "Qualidade dos clusters (Silhouette)",
        "cluster_silhouette_caption": "Avalia o quão bem cada ponto está associado ao seu próprio cluster em comparação com os demais.",
        "cluster_silhouette_metric": "Silhouette média",
        "cluster_silhouette_interp_high": "Separação muito boa entre os clusters.",
        "cluster_silhouette_interp_good": "Boa estrutura de agrupamento, com separação razoável.",
        "cluster_silhouette_interp_mid": "Estrutura moderada, com alguma sobreposição entre clusters.",
        "cluster_silhouette_interp_low": "Baixa separação entre clusters.",
        "cluster_silhouette_explanation": "Valores mais altos indicam agrupamentos mais coesos e melhor separação entre grupos. Em dados espaciais reais, valores moderados já podem representar uma estrutura útil de organização territorial.",
        "cluster_silhouette_dist_title": "Distribuição da silhouette por cluster",
        "cluster_silhouette_label_cluster": "Cluster",
        "cluster_silhouette_label_value": "Silhouette",

        # ---------------- ARI ----------------
        "cluster_ari_title": "Estabilidade do clustering (ARI)",
        "cluster_ari_caption": "Compara a solução base com pequenas variações de ε e MinPts no mesmo período, verificando a robustez da estrutura encontrada.",
        "cluster_ari_button": "Calcular estabilidade",
        "cluster_ari_help": "Esse teste é útil para verificar se pequenas mudanças nos parâmetros alteram significativamente a solução de clustering.",
        "cluster_ari_spinner": "Calculando estabilidade do clustering...",
        "cluster_ari_results_title": "Resultados",
        "cluster_ari_best_result": "Melhor resultado",
        "cluster_ari_interp_title": "Interpretação",
        "cluster_ari_interp_high": "Alta estabilidade: a solução de clustering se manteve robusta mesmo com pequenas variações dos parâmetros.",
        "cluster_ari_interp_mid": "Estabilidade moderada: a estrutura geral dos clusters foi preservada, com pequenas variações.",
        "cluster_ari_interp_low": "Baixa estabilidade: os clusters parecem sensíveis aos parâmetros adotados.",
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
        "home_eyebrow": "Epidemiological Surveillance Platform",
        "home_title": "DengueSphere",
        "home_subtitle": "Interactive System for Spatial Clustering of Dengue Cases",
        "home_lead": "Detect clusters of dengue cases from geographic data using the DBSCAN algorithm, interactive maps and statistics that support decision-making.",

        "home_start_header": "Get started",
        "home_link_coords": "Locate Coordinates",
        "home_link_cluster": "Open the Clustering Tool",
        "home_link_about": "About the project",

        "home_steps_header": "How it works",
        "home_step1_title": "Load your dataset",
        "home_step1_text": "Upload a spreadsheet (.csv or .xlsx) with the latitude, longitude and date of each case.",
        "home_step2_title": "Generate coordinates",
        "home_step2_text": "No latitude and longitude? Convert ZIP codes and addresses into coordinates automatically.",
        "home_step2_tag": "If needed",
        "home_step3_title": "Tune the parameters",
        "home_step3_text": "Set the radius (km) and the minimum number of cases that form a DBSCAN cluster.",
        "home_step4_title": "Analyze the results",
        "home_step4_text": "See the clusters on the map and check the distribution statistics.",

        "home_tip": "<strong>Tip:</strong> if your dataset has no geographic coordinates, use the <strong>Locate Coordinates</strong> module to generate them, download the updated dataset and load it into the <strong>Clustering Tool</strong>. Depending on the dataset size and request rate, this may take a few minutes.",

        "home_footer": "Developed by the Information and Decision Systems Research Group (GPSID) – PPGEP/UFPE",

        # ---------------- About Page ----------------
        "about_eyebrow": "Decision Support System · Epidemiological Surveillance",
        "about_title": "About DengueSphere",
        "about_lead": "An interactive platform that supports the analysis, processing and visualization of dengue geographic data, integrating information, mapping risk areas and supporting strategic decisions in disease control.",

        "about_modules_header": "Platform modules",
        "about_mod_geo_title": "Geocoding",
        "about_mod_geo_text": "ZIP code and address processing with automatic street correction and coordinates from OpenStreetMap.",
        "about_mod_cluster_title": "Spatial clustering",
        "about_mod_cluster_text": "Detection of case clusters with the DBSCAN algorithm and adjustable parameters.",
        "about_mod_map_title": "Interactive maps",
        "about_mod_map_text": "Clusters displayed over base maps, with neighborhood layers and free navigation.",
        "about_mod_stats_title": "Statistical analyses",
        "about_mod_stats_text": "Spatial and temporal distribution of clusters to help prioritize actions.",

        "about_objectives_header": "Objectives",
        "about_obj_1": "Integrate geographic and epidemiological data.",
        "about_obj_2": "Enable spatial and temporal analyses of dengue cases.",
        "about_obj_3": "Support public managers and researchers in decision-making.",

        "about_pub_header": "Publication",
        "about_pub_badge": "Conference paper",
        "about_pub_published": "Published in the proceedings of the",
        "about_pub_pages": "Vol. 1, pp. 154–160",
        "about_pub_cite_hint": "If you use DengueSphere in academic work, please cite:",
        "about_pub_bibtex": "Show BibTeX",

        "about_releases_header": "Release notes",
        "about_release_current": "Current version",
        "about_release_future": "Upcoming versions",
        "about_release_future_title": "In development",
        "about_release_10_items": [
            "Geocoding of ZIP codes and addresses via OpenStreetMap, with automatic street name correction",
            "Spatial clustering of cases with DBSCAN and adjustable parameters (radius and minimum cases)",
            "Interactive maps with base map selection and a neighborhood layer",
            "Cluster distribution statistics and stability assessment (ARI)",
            "Portuguese and English interface",
        ],
        "about_release_future_items": [
            "Nowcasting to correct reporting delays and avoid underestimated clusters in the most recent weeks",
            "Cluster formation from forecasts, anticipating clusters of cases",
        ],

        "about_team_header": "Team",
        "about_team_eduardo_role": "PhD student, Graduate Program in Production Engineering (PPGEP/UFPE) · 2025 – present",
        "about_team_maisa_name": "Prof. Maisa Mendonça Silva, PhD",
        "about_team_maisa_role": "Supervisor · Permanent faculty member of PPGEP/UFPE",
        "about_team_gpsid_name": "GPSID",
        "about_team_gpsid_role": "Information and Decision Systems Research Group · PPGEP/UFPE",

        "about_footer": "Developed by Eduardo da Silva under the supervision of Prof. Maisa Mendonça Silva, PhD · GPSID – PPGEP/UFPE",


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
            # ---------------- Advanced Analysis / Validation ----------------
        "cluster_advanced_title": "Technical clustering analysis",
        "cluster_advanced_caption": "Section intended for methodological validation of the model. For technical use, research, and support in interpreting the identified clusters.",
        "cluster_advanced_toggle": "Show advanced analysis (Silhouette and ARI)",
        "cluster_info_silhouette_not_defined": "Silhouette analysis cannot be calculated for the current configuration.",

        # ---------------- Silhouette ----------------
        "cluster_silhouette_title": "Cluster quality (Silhouette)",
        "cluster_silhouette_caption": "Evaluates how well each point is associated with its own cluster compared with the others.",
        "cluster_silhouette_metric": "Average silhouette",
        "cluster_silhouette_interp_high": "Very good separation between clusters.",
        "cluster_silhouette_interp_good": "Good clustering structure, with reasonable separation.",
        "cluster_silhouette_interp_mid": "Moderate structure, with some overlap between clusters.",
        "cluster_silhouette_interp_low": "Low separation between clusters.",
        "cluster_silhouette_explanation": "Higher values indicate more cohesive groupings and better separation between groups. In real spatial data, moderate values may already represent a useful territorial organization structure.",
        "cluster_silhouette_dist_title": "Silhouette distribution by cluster",
        "cluster_silhouette_label_cluster": "Cluster",
        "cluster_silhouette_label_value": "Silhouette",

        # ---------------- ARI ----------------
        "cluster_ari_title": "Clustering stability (ARI)",
        "cluster_ari_caption": "Compares the baseline solution with small variations in ε and MinPts for the same period, checking the robustness of the identified structure.",
        "cluster_ari_button": "Calculate stability",
        "cluster_ari_help": "This test is useful to verify whether small changes in the parameters significantly alter the clustering solution.",
        "cluster_ari_spinner": "Calculating clustering stability...",
        "cluster_ari_results_title": "Results",
        "cluster_ari_best_result": "Best result",
        "cluster_ari_interp_title": "Interpretation",
        "cluster_ari_interp_high": "High stability: the clustering solution remained robust even with small parameter variations.",
        "cluster_ari_interp_mid": "Moderate stability: the general cluster structure was preserved, with small variations.",
        "cluster_ari_interp_low": "Low stability: the clusters appear to be sensitive to the adopted parameters.",
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
