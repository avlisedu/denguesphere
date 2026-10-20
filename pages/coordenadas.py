import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from rapidfuzz import process, fuzz
import unicodedata, re, io
from time import sleep, monotonic
from i18n import t
from ui import inject_styles, html, page_header, step, mini_cards, footer, tip, DATASET_URL

COLUNAS_RESULTADO = ["CEP_processado", "latitude", "longitude", "bairro_utilizado", "municipio_encontrado", "tipo_match"]

# Municípios da Região Metropolitana do Recife: (sul, norte, oeste, leste), limites administrativos do OpenStreetMap
CIDADES_RMR = {
    "Recife": (-8.1552, -7.9290, -35.0186, -34.8515),
    "Olinda": (-8.0509, -7.9547, -34.9170, -34.8266),
    "Jaboatão dos Guararapes": (-8.2424, -8.0564, -35.0970, -34.9089),
    "Paulista": (-7.9813, -7.8380, -35.0310, -34.8192),
    "Camaragibe": (-8.0376, -7.9247, -35.0349, -34.9597),
    "São Lourenço da Mata": (-8.0924, -7.9411, -35.2223, -34.9932),
    "Abreu e Lima": (-7.9356, -7.7923, -35.1400, -34.8600),
    "Igarassu": (-7.9000, -7.6907, -35.0998, -34.8320),
    "Cabo de Santo Agostinho": (-8.3664, -8.1841, -35.2660, -34.9210),
    "Ipojuca": (-8.6078, -8.3099, -35.2381, -34.9464),
    "Moreno": (-8.2248, -8.0751, -35.2273, -35.0601),
    "Itapissuma": (-7.8081, -7.6824, -34.9433, -34.8624),
    "Ilha de Itamaracá": (-7.8164, -7.6878, -34.8902, -34.8233),
    "Araçoiaba": (-7.8800, -7.7226, -35.1400, -35.0204),
    "Goiana": (-7.7147, -7.4620, -35.0770, -34.8062),
}

inject_styles()

# ============================================================
# CABEÇALHO
# ============================================================
page_header("fi-rr-map-location-track", t("coords_title"), t("coords_lead"))

html(f"""
<div style="margin-top: 18px">
{mini_cards([
    ("fi-rr-table-columns", t("coords_feat_columns")),
    ("fi-rr-text-check", t("coords_feat_fix")),
    ("fi-rr-search-location", t("coords_feat_osm")),
    ("fi-rr-file-download", t("coords_feat_download")),
])}
</div>
""")


# ============================================================
# 1. Funções de normalização
# ============================================================
def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = re.sub(r'\b(de|da|do|das|dos|rua|avenida|av|travessa|tv)\b', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def limpar_cep(valor):
    if pd.isna(valor):
        return ""
    # CEP lido como número (ex.: 51111150.0) não pode virar "511111500"
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    cep = re.sub(r"\D", "", str(valor))
    # CEPs que começam com 0 perdem esse dígito quando lidos como número
    return cep.zfill(8) if len(cep) == 7 else cep


def adivinhar_coluna(colunas, preferidas, trechos):
    """Sugere a coluna pelo nome: primeiro nomes exatos, depois trechos (ignorando colunas de código id_*)."""
    nomes = [normalizar_texto(c).replace(" ", "_") for c in colunas]
    for preferida in preferidas:
        if preferida in nomes:
            return nomes.index(preferida)
    for i, nome in enumerate(nomes):
        if not nome.startswith("id_") and any(trecho in nome for trecho in trechos):
            return i
    return 0


@st.cache_data(show_spinner=False)
def ler_planilha(dados: bytes, nome: str) -> pd.DataFrame:
    if nome.lower().endswith(".csv"):
        for encoding in ("utf-8", "latin-1"):
            try:
                return pd.read_csv(io.BytesIO(dados), sep=None, engine="python", encoding=encoding)
            except UnicodeDecodeError:
                continue
    return pd.read_excel(io.BytesIO(dados))


def montar_resultado(df, resultados):
    """Junta a base original com as colunas de coordenadas; linhas ainda não processadas ficam vazias."""
    res = pd.DataFrame(resultados, columns=COLUNAS_RESULTADO).reindex(range(len(df)))
    return pd.concat([df.reset_index(drop=True), res], axis=1)


def para_excel(df) -> bytes:
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()


def contar_por_tipo(resultados):
    tipos = pd.Series([r["tipo_match"] for r in resultados], dtype="object")
    return {tipo: int((tipos == tipo).sum()) for tipo in ("cep", "rua_bairro", "bairro", "nao_encontrado")}


def mostrar_contagens(contagens):
    cols = st.columns(4)
    rotulos = [
        ("cep", "coords_match_cep"),
        ("rua_bairro", "coords_match_rua"),
        ("bairro", "coords_match_bairro"),
        ("nao_encontrado", "coords_match_none"),
    ]
    for col, (tipo, chave) in zip(cols, rotulos):
        col.metric(t(chave), contagens[tipo])


# ============================================================
# 2. Upload
# ============================================================
html(step(1, t("coords_step_upload")))
uploaded_file = st.file_uploader(t("coords_uploader_label"), type=["xlsx", "csv"])

if uploaded_file is None:
    tip(t("coords_no_file_info").format(url=DATASET_URL), icon="fi-rr-database")
    footer(t("app_footer"))
    st.stop()

df = ler_planilha(uploaded_file.getvalue(), uploaded_file.name)
st.success(t("coords_file_loaded").format(n_rows=len(df), n_cols=len(df.columns)))
with st.expander(t("coords_preview")):
    st.dataframe(df.head(20), width="stretch")

# ============================================================
# 3. Seleção de colunas
# ============================================================
html(step(2, t("coords_step_columns")))
colunas = list(df.columns)
col1, col2, col3 = st.columns(3)
with col1:
    cep_col = st.selectbox(t("coords_select_cep"), options=colunas,
                           index=adivinhar_coluna(colunas, ["nu_cep", "cep"], ["cep"]))
with col2:
    rua_col = st.selectbox(t("coords_select_rua"), options=colunas,
                           index=adivinhar_coluna(colunas, ["nm_logrado", "logradouro", "rua", "endereco"],
                                                  ["logradouro", "logrado", "rua", "endereco", "street"]))
with col3:
    bairro_col = st.selectbox(t("coords_select_bairro"), options=colunas,
                              index=adivinhar_coluna(colunas, ["nm_bairro", "bairro"], ["bairro", "neighborhood"]))


def incluir_rmr():
    st.session_state["geo_cidades"] = list(CIDADES_RMR)


if "geo_cidades" not in st.session_state:
    st.session_state["geo_cidades"] = ["Recife"]
col_cidades, col_rmr = st.columns([3, 1], vertical_alignment="bottom")
with col_cidades:
    cidades = st.multiselect(t("coords_cities"), options=list(CIDADES_RMR), key="geo_cidades")
with col_rmr:
    st.button(t("coords_cities_all"), icon=":material/add_location_alt:", on_click=incluir_rmr, width="stretch")
st.caption(t("coords_cities_help"))

if not cidades:
    st.warning(t("coords_cities_empty"))
    footer(t("app_footer"))
    st.stop()

# ============================================================
# 4. Estado da busca (permite parar e continuar)
# ============================================================
state = st.session_state
assinatura = (uploaded_file.name, uploaded_file.size, cep_col, rua_col, bairro_col, tuple(cidades))
if state.get("geo_sig") != assinatura:
    state.geo_sig = assinatura
    state.geo_results = []
    state.geo_cache = {}
    state.geo_status = "idle"  # idle | running | stopped | done
    state.geo_elapsed = 0.0     # segundos acumulados nas buscas já paradas ou concluídas
    state.geo_run_start = None  # início da execução atual (monotonic)


def iniciar():
    state.geo_results = []
    state.geo_status = "running"
    state.geo_elapsed = 0.0
    state.geo_run_start = monotonic()


def continuar():
    state.geo_status = "running"
    state.geo_run_start = monotonic()


def encerrar_cronometro():
    if state.geo_run_start is not None:
        state.geo_elapsed += monotonic() - state.geo_run_start
        state.geo_run_start = None


def parar():
    state.geo_status = "stopped"
    encerrar_cronometro()


def tempo_decorrido():
    extra = monotonic() - state.geo_run_start if state.geo_run_start is not None else 0
    return state.geo_elapsed + extra


def formatar_tempo(segundos):
    segundos = int(segundos)
    h, resto = divmod(segundos, 3600)
    m, seg = divmod(resto, 60)
    return f"{h}:{m:02d}:{seg:02d}" if h else f"{m:02d}:{seg:02d}"


def cronometro(rotulo, ao_vivo):
    """Relógio do tempo de busca; ao vivo, o navegador avança o contador a cada segundo."""
    segundos = tempo_decorrido()
    classe = "ds-timer live" if ao_vivo else "ds-timer"
    marcador = f"ds-timer-{len(state.geo_results)}-{int(segundos * 1000)}"
    script = f"""
    <script>
    (() => {{
        const base = {segundos:.3f}, inicio = performance.now();
        const fmt = s => {{
            s = Math.floor(s);
            const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), seg = s % 60;
            const dd = n => String(n).padStart(2, "0");
            return h ? `${{h}}:${{dd(m)}}:${{dd(seg)}}` : `${{dd(m)}}:${{dd(seg)}}`;
        }};
        let tentativas = 0;
        const id = setInterval(() => {{
            const el = document.getElementById("{marcador}");
            if (!el) {{ if (++tentativas > 5) clearInterval(id); return; }}
            tentativas = 0;
            el.textContent = fmt(base + (performance.now() - inicio) / 1000);
        }}, 250);
    }})();
    </script>
    """ if ao_vivo else ""
    st.html(
        f'<div class="{classe}"><i class="fi fi-rr-stopwatch"></i>'
        f'<span><small>{rotulo}</small><b id="{marcador}">{formatar_tempo(segundos)}</b></span></div>{script}',
        width="content",
        unsafe_allow_javascript=ao_vivo,
    )


# ============================================================
# 5. Geocodificação
# ============================================================
ruas_unicas = sorted(set(df[rua_col].dropna().apply(normalizar_texto)))
geolocator = Nominatim(user_agent="geo_ferramenta_cep")
cache = state.geo_cache

# Área de busca: retângulo que cobre as cidades escolhidas (com folga de ~1 km)
caixas = [CIDADES_RMR[c] for c in cidades]
area_busca = [
    (min(c[0] for c in caixas) - 0.01, min(c[2] for c in caixas) - 0.01),
    (max(c[1] for c in caixas) + 0.01, max(c[3] for c in caixas) + 0.01),
]
cidades_norm = {normalizar_texto(c): c for c in cidades}


def municipio_valido(location):
    """Devolve o município escolhido em que o resultado caiu, ou None se caiu fora deles."""
    endereco = location.raw.get("address", {})
    for chave in ("city", "town", "municipality", "village"):
        nome = endereco.get(chave)
        if nome:
            return cidades_norm.get(normalizar_texto(nome))
    # Sem município no endereço: aceita se o ponto estiver dentro do limite de uma cidade escolhida
    for cidade in cidades:
        sul, norte, oeste, leste = CIDADES_RMR[cidade]
        if sul <= location.latitude <= norte and oeste <= location.longitude <= leste:
            return cidade
    return None


def corrigir_nome_rua(rua_digitada):
    if not rua_digitada:
        return ""
    rua_norm = normalizar_texto(rua_digitada)
    if not ruas_unicas:
        return rua_norm
    melhor, score, _ = process.extractOne(
        rua_norm, ruas_unicas, scorer=fuzz.token_sort_ratio
    )
    if score >= 70 and melhor != rua_norm:
        return melhor
    return rua_norm


def get_coordinates(row):
    bairro = normalizar_texto(row[bairro_col])
    rua = normalizar_texto(row[rua_col])
    cep = limpar_cep(row[cep_col])
    rua_corrigida = corrigir_nome_rua(rua)
    cache_key = f"cep:{cep}|rua:{rua_corrigida}|bairro:{bairro}"

    def build_payload(latitude=None, longitude=None, municipio=None, tipo_match="nao_encontrado"):
        return {
            "CEP_processado": cep,
            "latitude": latitude,
            "longitude": longitude,
            "bairro_utilizado": bairro,
            "municipio_encontrado": municipio,
            "tipo_match": tipo_match,
        }

    if cache_key in cache:
        return cache[cache_key].copy()

    def tentar_geocodificar(consultas, tipo_match):
        for consulta in consultas:
            try:
                # Busca só dentro da área das cidades escolhidas e confere o município de cada candidato:
                # um bairro com o mesmo nome em outra cidade não é aceito
                candidatos = geolocator.geocode(
                    consulta, timeout=10, exactly_one=False, limit=5,
                    viewbox=area_busca, bounded=True, country_codes="br", addressdetails=True,
                )
                sleep(1)
                for location in candidatos or []:
                    municipio = municipio_valido(location)
                    if municipio:
                        return build_payload(
                            latitude=location.latitude,
                            longitude=location.longitude,
                            municipio=municipio,
                            tipo_match=tipo_match,
                        )
            except Exception:
                sleep(1)
                continue
        return None

    # Com uma cidade, o nome dela entra na consulta; com várias, a área de busca e a conferência do município decidem
    local = f"{cidades[0]}, Pernambuco, Brasil" if len(cidades) == 1 else "Pernambuco, Brasil"

    if cep:
        resultado = tentar_geocodificar(
            [
                f"{cep}, Brasil",
                f"CEP {cep}, Brasil",
            ],
            "cep",
        )
        if resultado:
            cache[cache_key] = resultado.copy()
            return resultado

    if rua_corrigida and bairro:
        resultado = tentar_geocodificar(
            [
                f"{rua_corrigida}, {bairro}, {local}",
                f"rua {rua_corrigida}, {bairro}, {local}",
                f"avenida {rua_corrigida}, {bairro}, {local}",
                f"travessa {rua_corrigida}, {bairro}, {local}",
            ],
            "rua_bairro",
        )
        if resultado:
            cache[cache_key] = resultado.copy()
            return resultado

    if bairro:
        resultado = tentar_geocodificar(
            [f"{bairro}, {local}"],
            "bairro",
        )
        if resultado:
            cache[cache_key] = resultado.copy()
            return resultado

    resultado = build_payload(tipo_match="nao_encontrado")
    cache[cache_key] = resultado.copy()
    return resultado


html(step(3, t("coords_step_run")))
total = len(df)
resultados = state.geo_results

if state.geo_status == "idle":
    st.caption(t("coords_processing_info"))
    st.button(t("coords_button_start"), type="primary", icon=":material/travel_explore:", on_click=iniciar)

elif state.geo_status == "running":
    st.caption(t("coords_processing_info"))
    # O botão precisa existir antes do laço: clicar nele interrompe a execução atual
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        st.button(t("coords_button_stop"), icon=":material/stop_circle:", on_click=parar)
        if state.geo_run_start is None:  # execução retomada sem passar pelos botões
            state.geo_run_start = monotonic()
        cronometro(t("coords_timer_running"), ao_vivo=True)
    barra = st.progress(len(resultados) / total, text=t("coords_progress").format(done=len(resultados), total=total))
    ao_vivo = st.empty()

    for i in range(len(resultados), total):
        resultados.append(get_coordinates(df.iloc[i]))
        barra.progress((i + 1) / total, text=t("coords_progress").format(done=i + 1, total=total))
        with ao_vivo.container():
            mostrar_contagens(contar_por_tipo(resultados))

    encerrar_cronometro()
    state.geo_status = "done"
    st.rerun()

elif state.geo_status == "stopped":
    st.warning(t("coords_stopped").format(done=len(resultados), total=total))
    cronometro(t("coords_timer_total"), ao_vivo=False)
    col_continuar, col_recomecar, _ = st.columns([1, 1, 2])
    with col_continuar:
        st.button(t("coords_button_resume"), type="primary", icon=":material/play_arrow:",
                  on_click=continuar, width="stretch")
    with col_recomecar:
        st.button(t("coords_button_restart"), icon=":material/restart_alt:", on_click=iniciar, width="stretch")

else:  # done
    st.success(t("coords_processing_done").format(total=total))
    cronometro(t("coords_timer_total"), ao_vivo=False)
    st.button(t("coords_button_restart"), icon=":material/restart_alt:", on_click=iniciar)

# ============================================================
# 6. Resultado (completo ou parcial)
# ============================================================
if resultados and state.geo_status in ("stopped", "done"):
    html(step(4, t("coords_step_results")))
    mostrar_contagens(contar_por_tipo(resultados))

    df_final = montar_resultado(df, resultados)

    encontrados = df_final.dropna(subset=["latitude", "longitude"])
    if not encontrados.empty:
        st.markdown(f"**{t('coords_map_title')}**")
        st.map(encontrados[["latitude", "longitude"]], color="#00838f", size=25)

    with st.expander(t("coords_preview")):
        st.dataframe(df_final.head(50), width="stretch")

    # Gera o Excel uma vez por estado do resultado (evita refazer a cada interação)
    chave_excel = (assinatura, len(resultados))
    if state.get("geo_excel_key") != chave_excel:
        state.geo_excel = para_excel(df_final)
        state.geo_excel_key = chave_excel

    st.download_button(
        label=t("coords_download_button") if state.geo_status == "done" else t("coords_download_partial"),
        data=state.geo_excel,
        file_name="resultado_geocodificado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        icon=":material/download:",
    )

footer(t("app_footer"))
