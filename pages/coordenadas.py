import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from rapidfuzz import process, fuzz
import unicodedata, re, io
from time import sleep
from i18n import t
from ui import inject_styles, html, page_header, step, mini_cards, footer, tip, DATASET_URL

COLUNAS_RESULTADO = ["CEP_processado", "latitude", "longitude", "bairro_utilizado", "tipo_match"]

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

# ============================================================
# 4. Estado da busca (permite parar e continuar)
# ============================================================
state = st.session_state
assinatura = (uploaded_file.name, uploaded_file.size, cep_col, rua_col, bairro_col)
if state.get("geo_sig") != assinatura:
    state.geo_sig = assinatura
    state.geo_results = []
    state.geo_cache = {}
    state.geo_status = "idle"  # idle | running | stopped | done


def iniciar():
    state.geo_results = []
    state.geo_status = "running"


def continuar():
    state.geo_status = "running"


def parar():
    state.geo_status = "stopped"


# ============================================================
# 5. Geocodificação
# ============================================================
ruas_unicas = sorted(set(df[rua_col].dropna().apply(normalizar_texto)))
geolocator = Nominatim(user_agent="geo_ferramenta_cep")
cache = state.geo_cache


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

    def build_payload(latitude=None, longitude=None, tipo_match="nao_encontrado"):
        return {
            "CEP_processado": cep,
            "latitude": latitude,
            "longitude": longitude,
            "bairro_utilizado": bairro,
            "tipo_match": tipo_match,
        }

    if cache_key in cache:
        return cache[cache_key].copy()

    def tentar_geocodificar(consultas, tipo_match):
        for consulta in consultas:
            try:
                location = geolocator.geocode(consulta, timeout=10)
                sleep(1)
                if location:
                    return build_payload(
                        latitude=location.latitude,
                        longitude=location.longitude,
                        tipo_match=tipo_match,
                    )
            except Exception:
                sleep(1)
                continue
        return None

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
                f"{rua_corrigida}, {bairro}, Recife, Pernambuco, Brasil",
                f"rua {rua_corrigida}, {bairro}, Recife, Pernambuco, Brasil",
                f"avenida {rua_corrigida}, {bairro}, Recife, Pernambuco, Brasil",
                f"travessa {rua_corrigida}, {bairro}, Recife, Pernambuco, Brasil",
            ],
            "rua_bairro",
        )
        if resultado:
            cache[cache_key] = resultado.copy()
            return resultado

    if bairro:
        resultado = tentar_geocodificar(
            [f"{bairro}, Recife, Pernambuco, Brasil"],
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
    st.button(t("coords_button_stop"), icon=":material/stop_circle:", on_click=parar)
    barra = st.progress(len(resultados) / total, text=t("coords_progress").format(done=len(resultados), total=total))
    ao_vivo = st.empty()

    for i in range(len(resultados), total):
        resultados.append(get_coordinates(df.iloc[i]))
        barra.progress((i + 1) / total, text=t("coords_progress").format(done=i + 1, total=total))
        with ao_vivo.container():
            mostrar_contagens(contar_por_tipo(resultados))

    state.geo_status = "done"
    st.rerun()

elif state.geo_status == "stopped":
    st.warning(t("coords_stopped").format(done=len(resultados), total=total))
    col_continuar, col_recomecar, _ = st.columns([1, 1, 2])
    with col_continuar:
        st.button(t("coords_button_resume"), type="primary", icon=":material/play_arrow:",
                  on_click=continuar, width="stretch")
    with col_recomecar:
        st.button(t("coords_button_restart"), icon=":material/restart_alt:", on_click=iniciar, width="stretch")

else:  # done
    st.success(t("coords_processing_done").format(total=total))
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
