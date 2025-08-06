import streamlit as st

pg = st.navigation([
    st.Page("CalculoManual.py"),
    st.Page("DatosGenerales.py"),

    st.Page("modalidad40.py")
])

pg.run()