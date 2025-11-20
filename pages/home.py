import streamlit as st
import base64
from pathlib import Path


# ======================================
# CONFIGURAÇÃO DE ESTILO
# ======================================
st.markdown("""
<style>
    /* Fundo branco fixo */
    .stApp {
        background-color: #ffffff !important;
    }

    /* Centralização da logo e layout */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        margin-top: 30px;
        margin-bottom: 10px;
    }

    .logo-container img {
        max-width: 280px;
        height: auto;
        border-radius: 0;
        box-shadow: none;
        pointer-events: none;
    }

    /* Centraliza textos principais */
    .content {
        text-align: center;
        margin: 0 auto;
        max-width: 800px;
    }

    .content h2 {
        color: #0d47a1;
        margin-top: 15px;
    }

    .content em {
        color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)


logo_path = Path("img/logo.png")
if logo_path.exists():
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}">
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("Logo não encontrada. Coloque o arquivo **logo.png** na pasta raiz do projeto.")


st.markdown("""
<div class="content">
    <h2><strong>DengueSphere v1.0</strong></h2>
    <p><em>Sistema Interativo de Clusterização Espacial da Dengue</em></p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.header("Bem-vindo ao DengueSphere v1.0")

st.markdown("""
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
""")

st.info(
    "Versão atual: 1.0 – Desenvolvido pelo Grupo de Pesquisa em Sistemas de Informação e Decisão (GPSID) - PPGEP/UFPE."
)
