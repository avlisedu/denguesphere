import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from rapidfuzz import process, fuzz
import unicodedata, re
from time import sleep

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
st.title("Tratamento de CEP e Geocodificação")

st.write(
    """
    Esta ferramenta permite:
    - Escolher colunas com CEP, Rua e Bairro de qualquer planilha Excel  
    - Corrigir nomes de ruas automaticamente (fuzzy matching)  
    - Obter coordenadas geográficas via OpenStreetMap (Nominatim)  
    - Gerar e baixar um arquivo Excel com os resultados geocodificados
    """
)

# ============================================================
# UPLOAD DE ARQUIVO
# ============================================================
uploaded_file = st.file_uploader("Selecione o arquivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success(f"Arquivo carregado com {len(df)} linhas e {len(df.columns)} colunas.")

    st.subheader("Selecione as colunas correspondentes")

    # Seletores dinâmicos de colunas
    col1, col2, col3 = st.columns(3)
    with col1:
        cep_col = st.selectbox("Coluna do CEP", options=df.columns)
    with col2:
        rua_col = st.selectbox("Coluna do nome da rua/logradouro", options=df.columns)
    with col3:
        bairro_col = st.selectbox("Coluna do bairro", options=df.columns)

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
        rua_raw = normalizar_texto(row[rua_col])
        cep = str(row[cep_col]).split('.')[0] if pd.notna(row[cep_col]) else ""

        rua_corrigida = corrigir_nome_rua(rua_raw)
        chave = f"{rua_corrigida}_{bairro}"

        # Cache para otimizar consultas repetidas
        if chave in cache:
            return pd.Series([cep, *cache[chave], bairro])

        tentativas = [
            f"{rua_corrigida}, {bairro}, Brasil",
            f"rua {rua_corrigida}, {bairro}, Brasil",
            f"travessa {rua_corrigida}, {bairro}, Brasil",
            f"avenida {rua_corrigida}, {bairro}, Brasil"
        ]

        for endereco in tentativas:
            try:
                location = geolocator.geocode(endereco, timeout=10)
                sleep(1)
                if location:
                    lat, lon = location.latitude, location.longitude
                    cache[chave] = (lat, lon, "endereco_exato")
                    return pd.Series([cep, lat, lon, bairro])
            except Exception:
                continue

        return pd.Series([cep, None, None, bairro])

    # ============================================================
    # 5. Executar processamento
    # ============================================================
    if st.button("Iniciar Geocodificação"):
        st.info("Processando endereços, isso pode levar alguns minutos dependendo da base...")
        progress_bar = st.progress(0)
        results = []

        for i, row in df.iterrows():
            results.append(get_coordinates(row))
            progress_bar.progress((i + 1) / len(df))

        progress_bar.empty()
        st.success("Geocodificação concluída.")

        # Resultado final
        df[['CEP_processado', 'latitude', 'longitude', 'bairro_utilizado']] = pd.DataFrame(results)
        st.dataframe(df.head())

        # ============================================================
        # 6. Exportar resultado
        # ============================================================
        output_file = "resultado_geocodificado.xlsx"
        df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button(
                label="Baixar arquivo Excel",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.info("Envie um arquivo Excel para começar.")
