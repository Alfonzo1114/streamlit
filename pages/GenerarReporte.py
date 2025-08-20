import streamlit as st
from docxtpl import DocxTemplate
from io import BytesIO
from core.data_processing import SessionVars
from datetime import datetime

session = SessionVars()
st.title("Generación de Reporte de Pensión")

# User inputs
name = st.text_input("Nombre", session.get("Nombre"))
date = st.date_input("Fecha")

# Populate template
if st.button("Generar Reporte"):
    data = {"name": name, "date": date}
    doc = DocxTemplate("templates/template.docx")
    doc.render(data)

    # Save to BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    # Download button
    st.download_button(
        label="Descargar Reporte",
        data=buffer,
        file_name="output.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
