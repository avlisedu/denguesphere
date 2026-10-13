# Estudo numérico retrospectivo — DengueSphere × dengue no Recife (2013–2025)

Avaliação quantitativa do módulo de clusterização do DengueSphere em dados históricos,
sem uso operacional pela prefeitura: o software é "reexecutado" sobre 13 anos de notificações
e suas saídas são confrontadas com o que de fato aconteceu nas semanas seguintes.

## Dados

- `../Casos Dengue/AAAA.csv` — notificações de dengue do SINAN, portal de dados abertos do Recife
  (dados.recife.pe.gov.br, licença ODbL). Os arquivos vêm em dois esquemas de colunas, três
  formatos de CSV e três codificações; `carregar.py` padroniza tudo.
- OpenStreetMap (Overpass): malha viária nomeada (18.739 trechos) e limites de bairros (`baixar_osm.py`; 96 no OSM, dos quais 94 dentro do Recife).
- IBGE, Censo 2022 — malha de setores censitários com atributos de Pernambuco (`dados/ibge/PE_setores_CD2022.gpkg`,
  ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/malha_com_atributos/setores/gpkg/UF/PE/);
  população (`v0001`) distribuída na grade de 100 m por ponderação areal.
- `../dataset/baserecife.xlsx` — amostra de 2021 geocodificada pelo próprio DengueSphere (Nominatim), usada só na validação.

**Casos incluídos:** residentes no Recife (IBGE 261160), classificação final confirmada —
códigos antigos 1–4 (dengue clássico, com complicações, FHD, SCD) e atuais 10–12 (dengue,
com sinais de alarme, grave). Descartados (5) e inconclusivos (8) ficam de fora, exceto na
análise de sensibilidade "não descartados", que reproduz o que a vigilância vê em tempo real.
Data do caso = início dos sintomas (ou notificação, se ausente); datas a mais de um ano do
arquivo são descartadas.

**Limitações conhecidas dos dados:** o arquivo de 2014 termina em julho; ~90% das confirmações
são por critério clínico-epidemiológico; o pico do fim de 2015/início de 2016 coincide com a
epidemia de Zika (possível má classificação); população de 2022 usada como denominador para todos os anos.

## Pipeline

```bash
cd estudo
python3 -m venv .venv && .venv/bin/pip install pandas numpy scikit-learn shapely rapidfuzz matplotlib statsmodels scipy requests openpyxl fastapi python-multipart geopandas pyogrio
# baixar PE_setores_CD2022.gpkg do IBGE para dados/ibge/ (link acima)
.venv/bin/python baixar_osm.py              # base OSM -> dados/
.venv/bin/python geocodificar.py            # -> dados/casos_geocodificados.csv.gz
.venv/bin/python validar_geocodificacao.py  # concordância com o Nominatim do software
.venv/bin/python analises.py                # tabelas -> resultados/, figuras -> figuras/
.venv/bin/python gerar_latex.py             # tabelas LaTeX -> artigo/tabelas/
cd artigo && latexmk -pdf resultados.tex
```

## Métodos (resumo)

1. **Geocodificação local** (`geocodificar.py`): mesma cascata do `GeocodingService` do software
   (rua → bairro → não encontrado), trocando o Nominatim por casamento difuso
   (rapidfuzz, limiar 85) contra os trechos de rua do OSM recortados por bairro. Normaliza
   abreviações, ordinais, números por extenso e caracteres corrompidos.
2. **Validação da geocodificação**: distância até as coordenadas do Nominatim na amostra de 2021.
3. **Sensibilidade de parâmetros**: grade eps ∈ {0,1…1,0 km} × min_samples ∈ {3…20} em janelas de
   4 semanas não sobrepostas; nº de clusters, % de ruído, maior cluster, silhueta (haversine),
   estratificado por nível de incidência da janela.
4. **Estabilidade**: ARI sob eps ±10% e min_samples ±1 (`stability_analysis` do software) e sob
   subamostragem de 90% (10 réplicas por janela).
5. **Validação prospectiva**: a cada semana, DBSCAN sobre as 4 semanas anteriores; área sinalizada =
   células de 100 m a até eps de um ponto em cluster. Mede-se a captura dos casos das 4 semanas
   seguintes e o *Predictive Accuracy Index* (PAI = % casos capturados ÷ % da área do município).
   Também o PAI populacional (% casos capturados ÷ % da população na área). Referências: KDE com a mesma área,
   ranking de bairros por incidência, células mais populosas com a mesma área, buffer de todos os casos.
   Parâmetros escolhidos em 2013–2019 (treino) e avaliados em 2020–2025 (teste); comparação pareada
   por Wilcoxon.
6. **Persistência interanual**: correlação de Spearman entre anos dos casos por célula de 500 m e
   sobreposição dos 10% de células com mais casos.
7. **Desempenho**: tempo do `executar_clusterizacao` do software de 1 mil a 40 mil casos (Apple M2, 16 GB).
