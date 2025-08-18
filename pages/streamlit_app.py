import streamlit as st

pg = st.navigation([
    st.Page("CalculoManual.py"),
    st.Page("DatosGenerales.py"),
    st.Page("DatosGenerales_Mejorado.py"),
    st.Page("modalidad40.py"),
    st.Page("2_Crecimiento_Anual.py"),
    st.Page("GenerarReporte.py")
])

pg.run()