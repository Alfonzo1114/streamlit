import streamlit as st
from docxtpl import DocxTemplate
from io import BytesIO

st.title("Generación de Reporte de Pensión")

# User inputs
name = st.text_input("Name", "Carlos")
date = st.text_input("Date", "2025-08-17")

# Populate template
if st.button("Generate Document"):
    data = {"name": name, "date": date}
    doc = DocxTemplate("templates/template.docx")
    doc.render(data)

    # Save to BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    # Download button
    st.download_button(
        label="Download Document",
        data=buffer,
        file_name="output.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
