import streamlit as st

# ============================================================
# ESTILO VISUAL
# ============================================================
st.markdown("""
<style>
.block-container {
    padding-top: 3rem !important;
    padding-bottom: 2rem !important;
}
h1, h2, h3 {
    color: #0d47a1;
}
.info-box {
    background-color: #e3f2fd;
    border-left: 5px solid #2196f3;
    padding: 16px 20px;
    border-radius: 6px;
    margin-bottom: 20px;
}
.footer-box {
    background-color: #e3f2fd;
    border-radius: 6px;
    padding: 10px 16px;
    margin-top: 40px;
    font-size: 14px;
    color: #0d47a1;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONTEÚDO
# ============================================================
st.title("Sobre o DengueSphere")

st.markdown("""
<div class="info-box">
    <p><strong>DengueSphere</strong> é uma plataforma interativa desenvolvida para 
    apoiar a análise, o tratamento e a visualização de dados geográficos relacionados à dengue. 
    Seu objetivo é facilitar a integração de informações, o mapeamento de áreas de risco 
    e o suporte à tomada de decisões estratégicas no controle da doença.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Equipe de desenvolvimento")
st.markdown("""
- **Eduardo da Silva** — Doutorando do Programa de Pós-Graduação em Engenharia de Produção (PPGEP/UFPE) - (2025 - Atual) 
- **Profa. Dra. Maísa Mendonça Silva** — Orientadora, Docente Permanente do PPGEP/UFPE  
- **Grupo de Pesquisa em Sistemas de Informação e Decisão (GPSID)** — PPGEP/UFPE  
""")

st.subheader("Objetivos principais")
st.markdown("""
- Integrar dados geográficos e epidemiológicos.  
- Permitir análises espaciais e temporais de casos de dengue.  
- Apoiar gestores públicos e pesquisadores na tomada de decisão.  
- Disponibilizar ferramentas modulares, incluindo:
  - Tratamento de CEP e Geocodificação  
  - Clusterização geográfica  
  - Visualização interativa em mapas
  - Análises estatísticas
""")

st.markdown("""
<div class="footer-box">
    Versão 1.0 – Desenvolvido por Eduardo da Silva sob orientação da Profa. Dra. Maísa Mendonça Silva.<br>
    Grupo de Pesquisa em Sistemas de Informação e Decisão (GPSID) – PPGEP/UFPE.
</div>
""", unsafe_allow_html=True)
