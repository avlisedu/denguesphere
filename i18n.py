# i18n.py
import streamlit as st

# -------------------------------------------------
# DICIONÁRIO DE TRADUÇÕES
# -------------------------------------------------
TRANSLATIONS = {
    "pt": {
        # ---------------- Globais / Navegação ----------------
        "app_title": "DengueSphere v1.1",
        "nav_home": "Início",
        "nav_coords": "Localizar Coordenadas",
        "nav_cluster": "Clusterizar Casos",
        "nav_about": "Sobre o Projeto",
        "lang_label": "Idioma / Language",

        # ---------------- Página Home ----------------
        "home_title": "DengueSphere",
        "home_subtitle": "Sistema Interativo de Clusterização Espacial da Dengue",
        "home_welcome_header": "Bem-vindo ao DengueSphere",
        "home_main_text": """
O **DengueSphere** é uma plataforma interativa para análise espacial e clusterização de casos de dengue,
baseada no algoritmo **[DBSCAN (Density-Based Spatial Clustering of Applications with Noise)](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)**.

Com o sistema, é possível:

- Carregar bases de dados geográficas (latitude, longitude e data);
- Definir parâmetros de clusterização;
- Visualizar agrupamentos em mapas interativos;
- Gerar estatísticas de distribuição dos clusters.

> **Dica:** Caso sua base **não possua coordenadas geográficas**, utilize o módulo **"Localizar Coordenadas"** para **gerar as coordenadas automaticamente**, **baixar a base atualizada** e depois **inseri-la no módulo "Clusterizar Casos"**.  
> Dependendo do tamanho da base e da taxa de requisições, o processo pode **levar alguns minutos**.

Utilize o menu no topo para navegar entre as seções.
""",
        "home_dataset_header": "Base de dados de exemplo",
        "home_dataset_badge": "Dados abertos da Prefeitura do Recife",
        "home_dataset_title": "Casos de Dengue, Zika e Chikungunya",
        "home_dataset_text": "Notificações registradas nas unidades de saúde públicas e privadas do Recife. Os arquivos de dengue trazem bairro, logradouro e CEP, mas não latitude e longitude: use primeiro o módulo <strong>Localizar Coordenadas</strong> e depois carregue a base em <strong>Clusterizar Casos</strong>.",
        "home_dataset_years": "Dengue: 2013–2025, um CSV por ano",
        "home_dataset_publisher": "Secretaria de Saúde do Recife",
        "home_dataset_license": "Licença ODbL",
        "home_dataset_update": "Atualização trimestral",
        "home_dataset_button": "Acessar a base no portal",

        # ---------------- Página Sobre ----------------
        "about_eyebrow": "Sistema de apoio à decisão para vigilância epidemiológica",
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
        "about_release_previous": "Versão anterior",
        "about_release_11_items": [
            "Camadas de referência no mapa do Clusterizar Casos: pontos fixos (unidades de saúde, armadilhas, imóveis abandonados, pontos estratégicos) com ícone por tipo, enviados em CSV ou Excel",
            "Divisão por Distritos Sanitários: bairros desenhados com os limites do IBGE (Censo 2022), coloridos pelo distrito e com os indicadores da planilha ao passar o mouse",
            "Camadas prontas do Recife: 182 unidades de saúde (Dados Abertos da Prefeitura), sedes e os 8 Distritos Sanitários com seus 94 bairros",
            "Mapa enquadrado na área dos casos, sem ser deslocado por pontos geocodificados longe",
            "Botões no mapa para voltar à visão de todos os casos e para baixar a imagem (PNG) do que está na tela, em alta resolução",
            "Área de cada cluster desenhada a partir dos pontos núcleo do DBSCAN, com núcleos e bordas identificados em cada caso",
            "Geocodificação restrita às cidades escolhidas da Região Metropolitana do Recife",
        ],
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
        "about_team_eduardo_role": "Doutorando no PPGEP/UFPE desde 2025 e pesquisador visitante na University of Exeter (out/2026 a mar/2027)",
        "about_team_maisa_name": "Profa. Dra. Maisa Mendonça Silva",
        "about_team_maisa_role": "Orientadora e docente permanente do PPGEP/UFPE",
        "about_team_theo_name": "Theo Economou, PhD",
        "about_team_theo_role": "Professor de Estatística da University of Exeter",

        # ---------------- Página Coordenadas ----------------
        "coords_title": "Localizar Coordenadas",
        "coords_lead": "Converta CEP, rua e bairro em latitude e longitude usando o OpenStreetMap, e baixe a base pronta para Clusterizar Casos.",
        "coords_feat_columns": "Escolha as colunas de CEP, rua e bairro de qualquer planilha",
        "coords_feat_fix": "Nomes de ruas são normalizados antes da busca",
        "coords_feat_osm": "Coordenadas obtidas no OpenStreetMap (Nominatim)",
        "coords_feat_download": "Baixe a planilha com latitude e longitude",
        "coords_step_upload": "Envie a planilha",
        "coords_uploader_label": "Planilha Excel (.xlsx) ou CSV",
        "coords_file_loaded": "Arquivo carregado com {n_rows} linhas e {n_cols} colunas.",
        "coords_preview": "Ver as primeiras linhas",
        "coords_step_columns": "Indique as colunas",
        "coords_select_cep": "Coluna do CEP",
        "coords_select_rua": "Coluna da rua ou logradouro",
        "coords_select_bairro": "Coluna do bairro",
        "coords_cities": "Cidades de interesse",
        "coords_cities_help": "A busca só aceita endereços dentro das cidades escolhidas. Um bairro com o mesmo nome em outra cidade é descartado, e a linha fica como não encontrada.",
        "coords_cities_all": "Toda a Região Metropolitana",
        "coords_cities_empty": "Escolha pelo menos uma cidade para buscar as coordenadas.",
        "coords_step_run": "Busque as coordenadas",
        "coords_processing_info": "A busca consulta o OpenStreetMap com uma pausa de 1 segundo entre as requisições, então bases grandes podem levar bastante tempo. Você pode parar a qualquer momento e baixar o que já foi processado.",
        "coords_button_start": "Iniciar busca",
        "coords_button_stop": "Parar busca",
        "coords_button_resume": "Continuar de onde parou",
        "coords_button_restart": "Recomeçar do zero",
        "coords_progress": "{done} de {total} linhas processadas",
        "coords_timer_running": "Tempo de busca",
        "coords_timer_total": "Tempo total de busca",
        "coords_stopped": "Busca interrompida com {done} de {total} linhas processadas. Você pode continuar de onde parou ou baixar o resultado parcial.",
        "coords_processing_done": "Busca concluída para todas as {total} linhas.",
        "coords_step_results": "Resultado",
        "coords_match_cep": "Encontrados pelo CEP",
        "coords_match_rua": "Encontrados por rua e bairro",
        "coords_match_bairro": "Encontrados só pelo bairro",
        "coords_match_none": "Não encontrados",
        "coords_map_title": "Pontos encontrados",
        "coords_download_button": "Baixar planilha (.xlsx)",
        "coords_download_partial": "Baixar resultado parcial (.xlsx)",
        "coords_no_file_info": "<strong>Não tem uma base em mãos?</strong> Teste com os <a href=\"{url}\" target=\"_blank\">casos de dengue dos dados abertos do Recife</a>: baixe o CSV de um ano e envie aqui.",
        "coords_logo_warning": "Logo não encontrada. Coloque o arquivo **logo.png** na pasta raiz do projeto.",

        # ---------------- Página Clusterizador ----------------
        "cluster_title": "Clusterizar Casos",
        "cluster_table_title": "Casos por cluster",
        "cluster_req_link": "Sua base não tem coordenadas? Gere em Localizar Coordenadas",
        "cluster_req_format": "Arquivo CSV ou Excel (.xlsx)",
        "cluster_req_date": "Uma coluna com a data de notificação dos casos",
        "cluster_req_coords": "Colunas latitude e longitude (ou lat e long)",
        "cluster_upload_header": "Base de dados",
        "cluster_lead": "Agrupe casos de dengue próximos no espaço e no tempo com o DBSCAN e veja os clusters no mapa, com estatísticas de cada um.",
        "cluster_upload_label": "Selecione um arquivo CSV ou XLSX",
        "cluster_loading": "Carregando a base...",
        "cluster_read_error": "Não foi possível ler o arquivo. Confira se é um CSV ou Excel válido. Detalhe: {error}",
        "cluster_empty_file": "O arquivo não tem nenhuma linha de dados.",
        "cluster_columns_title": "Colunas usadas na análise",
        "cluster_columns_missing": "Não encontramos automaticamente: {missing}. Escolha abaixo quais colunas da base usar.",
        "cluster_col_date": "Data de notificação",
        "cluster_col_lat": "Latitude",
        "cluster_col_lon": "Longitude",
        "cluster_col_placeholder": "Escolha uma coluna",
        "cluster_error_dates": "Nenhuma data válida na coluna {col}. Exemplos de valores encontrados: {examples}. Escolha outra coluna em Colunas usadas na análise.",
        "cluster_error_no_coords": "Nenhuma coordenada válida nas colunas {lat} e {lon}. Confira as colunas escolhidas ou gere as coordenadas antes.",
        "cluster_summary_rows": "Registros",
        "cluster_summary_coords": "Com coordenadas válidas",
        "cluster_summary_period": "Período",
        "cluster_summary_columns": "Colunas usadas",
        "cluster_summary_dropped": "{n} registros sem data ou sem coordenadas válidas ficaram de fora da análise.",
        "cluster_map_reset": "Voltar à visão de todos os casos",
        "cluster_point_label": "Cluster {id}: {n} casos",
        "cluster_point_noise": "Ruído (caso isolado)",
        "cluster_point_core": "ponto núcleo",
        "cluster_point_border": "ponto de borda",
        "cluster_map_print": "Baixar imagem do mapa (PNG)",

        # ---------------- Camadas de referência ----------------
        "layers_title": "Camadas de referência (opcional)",
        "layers_lead": "Quer mostrar no mapa pontos fixos (unidades de saúde, armadilhas, imóveis abandonados) ou a divisão por distrito sanitário? Envie os arquivos abaixo; os casos continuam sendo clusterizados normalmente.",
        "layers_points_title": "Pontos fixos",
        "layers_points_help": "CSV ou Excel com latitude e longitude. A coluna **tipo** define o ícone (unidade de saúde, hospital, pronto atendimento, zoonoses, armadilha, imóvel abandonado, ponto estratégico, sede de distrito); a coluna **nome** aparece no popup, junto com as demais colunas. Sem coluna tipo, o nome do arquivo vira o tipo.",
        "layers_points_upload": "Arquivos de pontos fixos",
        "layers_points_template": "Baixar modelo de pontos fixos",
        "layers_points_unidades": "Incluir as unidades de saúde do Recife (USF, UBS, policlínicas, pronto atendimento, hospitais e maternidades)",
        "layers_points_sedes": "Incluir as sedes dos 8 Distritos Sanitários do Recife",
        "layers_points_error": "Não foi possível usar {file}: {error}",
        "layers_points_no_coords": "{file}: nenhuma linha com latitude e longitude válidas (colunas esperadas: latitude e longitude).",
        "layers_points_loaded": "{n} pontos fixos carregados: {types}.",
        "layers_districts_title": "Distritos sanitários",
        "layers_districts_help": "CSV ou Excel com uma linha por bairro e as colunas **bairro** e **distrito** (ou DS). Os bairros são desenhados com os limites do IBGE (Censo 2022) e coloridos pelo distrito; as demais colunas numéricas aparecem ao passar o mouse.",
        "layers_districts_recife": "Usar os 8 Distritos Sanitários do Recife (94 bairros)",
        "layers_districts_upload": "Ou envie um arquivo de bairros por distrito",
        "layers_districts_template": "Baixar modelo de distritos",
        "layers_districts_missing_cols": "Este campo precisa de uma coluna de bairro e uma de distrito (ou DS). Colunas do arquivo: {cols}.",
        "layers_districts_points_hint": "Este arquivo tem latitude e longitude, então parece ser de pontos fixos. Envie-o no campo Arquivos de pontos fixos, ao lado.",
        "layers_districts_loaded": "{n} bairros de {mun} associados a {k} distritos.",
        "layers_districts_unassigned": "{n} bairros de {mun} não têm distrito no arquivo e aparecem em cinza.",
        "layers_districts_unmatched": "Bairros do arquivo não encontrados na malha do IBGE: {names}.",
        "layers_districts_no_match": "Nenhum bairro do arquivo foi encontrado na malha de bairros do IBGE para Pernambuco.",
        "layers_no_district": "Sem distrito informado",
        "layers_tooltip_bairro": "Bairro",
        "layers_tooltip_distrito": "Distrito",
        "cluster_sidebar_header": "Parâmetros DBSCAN",
        "cluster_eps_label": "EPS (distância em quilômetros)",
        "cluster_eps_help": "Define o raio máximo de vizinhança entre casos (em quilômetros). Valores menores detectam microáreas; valores maiores agrupam bairros próximos.",
        "cluster_min_samples_label": "Mínimo de pontos por cluster",
        "cluster_year_label": "Ano epidemiológico",
        "cluster_weeks_label": "Semanas epidemiológicas",
        "cluster_warning_empty_period": "Não há registros para o período selecionado.",
        "cluster_header_period": "Clusters em {year}, semanas {weeks}",
        "cluster_stats_title": "Estatísticas dos clusters",
        "cluster_metric_n_clusters": "Clusters identificados",
        "cluster_metric_noise": "Pontos isolados (ruído)",
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
        "app_title": "DengueSphere v1.1",
        "nav_home": "Home",
        "nav_coords": "Locate Coordinates",
        "nav_cluster": "Clustering Tool",
        "nav_about": "About the Project",
        "lang_label": "Idioma / Language",

        # ---------------- Home Page ----------------
        "home_title": "DengueSphere",
        "home_subtitle": "Interactive System for Spatial Clustering of Dengue Cases",
        "home_welcome_header": "Welcome to DengueSphere",
        "home_main_text": """
**DengueSphere** is an interactive platform for spatial analysis and clustering of dengue cases,
based on the **[DBSCAN (Density-Based Spatial Clustering of Applications with Noise)](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)** algorithm.

With the system, you can:

- Load geographic datasets (latitude, longitude and date);
- Define clustering parameters;
- Visualize clusters on interactive maps;
- Generate statistics on the distribution of clusters.

> **Tip:** If your dataset **does not contain geographic coordinates**, use the **"Locate Coordinates"** module to **automatically generate coordinates**, **download the updated dataset**, and then **load it into the "Clustering Tool" module**.  
> Depending on the dataset size and request rate, this process may **take a few minutes**.

Use the top menu to navigate between sections.
""",
        "home_dataset_header": "Sample dataset",
        "home_dataset_badge": "Open data from the City of Recife",
        "home_dataset_title": "Dengue, Zika and Chikungunya Cases",
        "home_dataset_text": "Cases reported by public and private health units in Recife. The dengue files include neighborhood, street and ZIP code, but no latitude and longitude: run them through <strong>Locate Coordinates</strong> first, then load the dataset into the <strong>Clustering Tool</strong>.",
        "home_dataset_years": "Dengue: 2013–2025, one CSV per year",
        "home_dataset_publisher": "Recife Health Department",
        "home_dataset_license": "ODbL license",
        "home_dataset_update": "Updated quarterly",
        "home_dataset_button": "Open the dataset on the portal",

        # ---------------- About Page ----------------
        "about_eyebrow": "Decision support system for epidemiological surveillance",
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
        "about_release_previous": "Previous version",
        "about_release_11_items": [
            "Reference layers on the Cluster Cases map: fixed points (health units, traps, abandoned properties, strategic points) with an icon per type, uploaded as CSV or Excel",
            "Health District division: neighborhoods drawn with IBGE boundaries (2022 Census), colored by district and showing the spreadsheet indicators on hover",
            "Ready-made Recife layers: 182 health units (City Hall Open Data), headquarters and the 8 Health Districts with their 94 neighborhoods",
            "Map framed on the area of the cases, without being shifted by points geocoded far away",
            "Map buttons to go back to the view of all cases and to download a high-resolution image (PNG) of the current view",
            "Area of each cluster drawn from the DBSCAN core points, with core and border points identified for each case",
            "Geocoding restricted to the chosen cities of the Recife Metropolitan Region",
        ],
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
        "about_team_eduardo_role": "PhD student at PPGEP/UFPE since 2025 and visiting researcher at the University of Exeter (Oct 2026 to Mar 2027)",
        "about_team_maisa_name": "Prof. Maisa Mendonça Silva, PhD",
        "about_team_maisa_role": "Supervisor and permanent faculty member of PPGEP/UFPE",
        "about_team_theo_name": "Theo Economou, PhD",
        "about_team_theo_role": "Statistics faculty member at the University of Exeter",

        # ---------------- Coordinates Page ----------------
        "coords_title": "Locate Coordinates",
        "coords_lead": "Turn ZIP codes, streets and neighborhoods into latitude and longitude with OpenStreetMap, and download a dataset ready for the Clustering Tool.",
        "coords_feat_columns": "Pick the ZIP code, street and neighborhood columns from any spreadsheet",
        "coords_feat_fix": "Street names are normalized before the search",
        "coords_feat_osm": "Coordinates come from OpenStreetMap (Nominatim)",
        "coords_feat_download": "Download the spreadsheet with latitude and longitude",
        "coords_step_upload": "Upload the spreadsheet",
        "coords_uploader_label": "Excel (.xlsx) or CSV file",
        "coords_file_loaded": "File loaded with {n_rows} rows and {n_cols} columns.",
        "coords_preview": "Show the first rows",
        "coords_step_columns": "Choose the columns",
        "coords_select_cep": "ZIP code column",
        "coords_select_rua": "Street column",
        "coords_select_bairro": "Neighborhood column",
        "coords_cities": "Cities of interest",
        "coords_cities_help": "The search only accepts addresses inside the selected cities. A neighborhood with the same name in another city is discarded, and the row is marked as not found.",
        "coords_cities_all": "Whole metropolitan region",
        "coords_cities_empty": "Choose at least one city to search for coordinates.",
        "coords_step_run": "Search for coordinates",
        "coords_processing_info": "The search queries OpenStreetMap with a 1-second pause between requests, so large datasets can take a long time. You can stop at any moment and download what has been processed so far.",
        "coords_button_start": "Start search",
        "coords_button_stop": "Stop search",
        "coords_button_resume": "Resume where it stopped",
        "coords_button_restart": "Start over",
        "coords_progress": "{done} of {total} rows processed",
        "coords_timer_running": "Search time",
        "coords_timer_total": "Total search time",
        "coords_stopped": "Search stopped with {done} of {total} rows processed. You can resume where it stopped or download the partial result.",
        "coords_processing_done": "Search finished for all {total} rows.",
        "coords_step_results": "Result",
        "coords_match_cep": "Found by ZIP code",
        "coords_match_rua": "Found by street and neighborhood",
        "coords_match_bairro": "Found by neighborhood only",
        "coords_match_none": "Not found",
        "coords_map_title": "Points found",
        "coords_download_button": "Download spreadsheet (.xlsx)",
        "coords_download_partial": "Download partial result (.xlsx)",
        "coords_no_file_info": "<strong>No dataset at hand?</strong> Try the <a href=\"{url}\" target=\"_blank\">dengue cases from Recife open data</a>: download one year as CSV and upload it here.",
        "coords_logo_warning": "Logo not found. Please place the **logo.png** file in the project root folder.",

        # ---------------- Cluster Page ----------------
        "cluster_title": "Clustering Tool",
        "cluster_table_title": "Cases per cluster",
        "cluster_req_link": "No coordinates in your dataset? Generate them in Locate Coordinates",
        "cluster_req_format": "CSV or Excel (.xlsx) file",
        "cluster_req_date": "A column with the notification date of each case",
        "cluster_req_coords": "latitude and longitude columns (or lat and long)",
        "cluster_upload_header": "Dataset",
        "cluster_lead": "Group dengue cases that are close in space and time with DBSCAN and see the clusters on the map, with statistics for each one.",
        "cluster_upload_label": "Select a CSV or XLSX file",
        "cluster_loading": "Loading the dataset...",
        "cluster_read_error": "Could not read the file. Check that it is a valid CSV or Excel file. Details: {error}",
        "cluster_empty_file": "The file has no data rows.",
        "cluster_columns_title": "Columns used in the analysis",
        "cluster_columns_missing": "Could not find automatically: {missing}. Choose below which dataset columns to use.",
        "cluster_col_date": "Notification date",
        "cluster_col_lat": "Latitude",
        "cluster_col_lon": "Longitude",
        "cluster_col_placeholder": "Choose a column",
        "cluster_error_dates": "No valid dates in column {col}. Sample values found: {examples}. Pick another column under Columns used in the analysis.",
        "cluster_error_no_coords": "No valid coordinates in columns {lat} and {lon}. Check the selected columns or generate the coordinates first.",
        "cluster_summary_rows": "Records",
        "cluster_summary_coords": "With valid coordinates",
        "cluster_summary_period": "Period",
        "cluster_summary_columns": "Columns used",
        "cluster_summary_dropped": "{n} records without a valid date or coordinates were left out of the analysis.",
        "cluster_map_reset": "Back to the view of all cases",
        "cluster_point_label": "Cluster {id}: {n} cases",
        "cluster_point_noise": "Noise (isolated case)",
        "cluster_point_core": "core point",
        "cluster_point_border": "border point",
        "cluster_map_print": "Download map image (PNG)",

        # ---------------- Reference layers ----------------
        "layers_title": "Reference layers (optional)",
        "layers_lead": "Want to show fixed points (health units, traps, abandoned properties) or the health district division on the map? Upload the files below; cases are still clustered as usual.",
        "layers_points_title": "Fixed points",
        "layers_points_help": "CSV or Excel with latitude and longitude. The **tipo** (type) column sets the icon (health unit, hospital, urgent care, zoonoses, trap, abandoned property, strategic point, district headquarters); the **nome** (name) column appears in the popup along with the other columns. Without a type column, the file name becomes the type.",
        "layers_points_upload": "Fixed point files",
        "layers_points_template": "Download fixed points template",
        "layers_points_unidades": "Include Recife's health units (family health, primary care, polyclinics, urgent care, hospitals and maternity wards)",
        "layers_points_sedes": "Include the headquarters of Recife's 8 Health Districts",
        "layers_points_error": "Could not use {file}: {error}",
        "layers_points_no_coords": "{file}: no rows with valid latitude and longitude (expected columns: latitude and longitude).",
        "layers_points_loaded": "{n} fixed points loaded: {types}.",
        "layers_districts_title": "Health districts",
        "layers_districts_help": "CSV or Excel with one row per neighborhood and the columns **bairro** (neighborhood) and **distrito** (or DS). Neighborhoods are drawn with IBGE boundaries (2022 Census) and colored by district; other numeric columns appear on hover.",
        "layers_districts_recife": "Use Recife's 8 Health Districts (94 neighborhoods)",
        "layers_districts_upload": "Or upload a neighborhoods by district file",
        "layers_districts_template": "Download districts template",
        "layers_districts_missing_cols": "This field needs a neighborhood column and a district (or DS) column. File columns: {cols}.",
        "layers_districts_points_hint": "This file has latitude and longitude, so it looks like a fixed points file. Upload it in the Fixed point files field, next to this one.",
        "layers_districts_loaded": "{n} neighborhoods of {mun} assigned to {k} districts.",
        "layers_districts_unassigned": "{n} neighborhoods of {mun} have no district in the file and are shown in gray.",
        "layers_districts_unmatched": "Neighborhoods in the file not found in the IBGE boundaries: {names}.",
        "layers_districts_no_match": "No neighborhood in the file was found in the IBGE neighborhood boundaries for Pernambuco.",
        "layers_no_district": "No district assigned",
        "layers_tooltip_bairro": "Neighborhood",
        "layers_tooltip_distrito": "District",
        "cluster_sidebar_header": "DBSCAN Parameters",
        "cluster_eps_label": "EPS (distance in kilometers)",
        "cluster_eps_help": "Defines the maximum neighborhood radius between cases (in kilometers). Smaller values detect micro-areas; larger values group nearby neighborhoods.",
        "cluster_min_samples_label": "Minimum points per cluster",
        "cluster_year_label": "Epidemiological year",
        "cluster_weeks_label": "Epidemiological weeks",
        "cluster_warning_empty_period": "There are no records for the selected period.",
        "cluster_header_period": "Clusters in {year}, weeks {weeks}",
        "cluster_stats_title": "Cluster statistics",
        "cluster_metric_n_clusters": "Identified clusters",
        "cluster_metric_noise": "Isolated points (noise)",
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


def _ao_trocar_idioma():
    escolha = st.session_state.get("lang_choice")
    if escolha:
        st.session_state["lang"] = escolha
    else:
        # clicar no botão já ativo desmarcaria a opção; mantém o idioma atual
        st.session_state["lang_choice"] = st.session_state["lang"]


def lang_selector():
    """
    Exibe os botões de idioma (PT-BR / EN) no topo da tela e atualiza st.session_state['lang'].
    """
    init_lang()
    if not st.session_state.get("lang_choice"):
        st.session_state["lang_choice"] = st.session_state["lang"]
    with st.container(horizontal=True, horizontal_alignment="right"):
        st.segmented_control(
            TRANSLATIONS[st.session_state["lang"]]["lang_label"],
            options=["pt", "en"],
            format_func=lambda x: {"pt": "PT-BR", "en": "EN"}[x],
            key="lang_choice",
            on_change=_ao_trocar_idioma,
            label_visibility="collapsed",
        )
    return st.session_state["lang"]


def t(key: str) -> str:
    """
    Retorna o texto traduzido para a chave informada.
    Se a chave não existir, retorna a própria chave.
    """
    init_lang()
    lang = st.session_state.get("lang", "pt")
    return TRANSLATIONS.get(lang, {}).get(key, key)
