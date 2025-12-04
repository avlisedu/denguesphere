import streamlit as st
from i18n import t

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
st.title(t("about_title"))

st.markdown(f"""
<div class="info-box">
    {t("about_infobox")}
</div>
""", unsafe_allow_html=True)

st.subheader(t("about_team_header"))
st.markdown(t("about_team_list"))

st.subheader(t("about_objectives_header"))
st.markdown(t("about_objectives_list"))

st.markdown(f"""
<div class="footer-box">
    {t("about_footer")}
</div>
""", unsafe_allow_html=True)
