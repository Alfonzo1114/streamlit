import streamlit as st
st.title("Modalidad 40")

st.sidebar.radio("Salario Asignado", ('1000', '2000'))

fecha_inicio = st.date_input("Fecha de inicio")
meses_mod40 = st.number_input("Meses de modalidad 40", min_value=1, max_value=12, value=1)
salario_asignado = st.number_input("Salario Asignado", min_value=1000, max_value=2000, value=1000)