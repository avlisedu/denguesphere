import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from rapidfuzz import process, fuzz
import unicodedata, re
from time import sleep
from i18n import t

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

# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================
st.title(t("coords_title"))

st.write(t("coords_intro"))

# ============================================================
# UPLOAD DE ARQUIVO
# ============================================================
uploaded_file = st.file_uploader(t("coords_uploader_label"), type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success(
        t("coords_file_loaded").format(n_rows=len(df), n_cols=len(df.columns))
    )

    st.subheader(t("coords_select_columns_subheader"))

    # Seletores dinâmicos de colunas
    col1, col2, col3 = st.columns(3)
    with col1:
        cep_col = st.selectbox(t("coords_select_cep"), options=df.columns)
    with col2:
        rua_col = st.selectbox(t("coords_select_rua"), options=df.columns)
    with col3:
        bairro_col = st.selectbox(t("coords_select_bairro"), options=df.columns)

    # ============================================================
    # 1. Função de normalização de texto
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
        return re.sub(r"\D", "", str(valor))

    # ============================================================
    # 2. Preparação da base
    # ============================================================
    ruas_unicas = sorted(set(df[rua_col].dropna().apply(normalizar_texto)))
    geolocator = Nominatim(user_agent="geo_ferramenta_cep")
    cache = {}

    # ============================================================
    # 3. Correção fuzzy de ruas
    # ============================================================
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

    # ============================================================
    # 4. Função principal de geocodificação
    # ============================================================
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

    # ============================================================
    # 5. Executar processamento
    # ============================================================
    if st.button(t("coords_button_start")):
        st.info(t("coords_processing_info"))
        progress_bar = st.progress(0)
        results = []
        required_columns = [
            "CEP_processado",
            "latitude",
            "longitude",
            "bairro_utilizado",
            "tipo_match",
        ]

        for i, row in df.iterrows():
            result = get_coordinates(row)
            if not isinstance(result, dict):
                st.error(f"Resultado invalido na linha {i + 1}.")
                result = {column: None for column in required_columns}
            results.append(result)
            progress_bar.progress((i + 1) / len(df))

        progress_bar.empty()
        st.success(t("coords_processing_done"))

        results_df = pd.DataFrame(results)
        for column in required_columns:
            if column not in results_df.columns:
                results_df[column] = None
        results_df = results_df[required_columns]

        df = pd.concat(
            [df.reset_index(drop=True), results_df.reset_index(drop=True)],
            axis=1,
        )
        st.dataframe(df.head())

        # ============================================================
        # 6. Exportar resultado
        # ============================================================
        output_file = "resultado_geocodificado.xlsx"
        df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button(
                label=t("coords_download_button"),
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.info(t("coords_no_file_info"))
