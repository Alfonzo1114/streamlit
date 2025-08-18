import streamlit as st
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.calculations import pagos40, PensionManual

st.sidebar.title("Parametros Generales del Usuario")
with st.sidebar:
    start_date = st.date_input("Incio de pago env Modalidad 40")

    duration = st.number_input("Duración de la Modalidad 40", min_value=0, value=60)
    salario_mod40 = st.number_input("Salario Mensual en Modalidad 40", min_value=50, value=50)


    # We will add a button to start a new calculation
    calculate_button = st.button("Calcular Modalidad 40")

pension_manual = PensionManual(edad_pension=62,
                               year=2023,
                               semanas_reconocidas=966,
                               salario_promedio=1439.18,
                               porcentaje_asignaciones=0.15)

if calculate_button:
    tabla_pago40, tabla_pago40_string = pagos40(
        salario=salario_mod40,
        start_date=start_date,
        duration=duration)
    st.subheader("Pagos en Modalidad 40")
    st.dataframe(tabla_pago40_string)

    pension_df, detalles_df = pension_manual.calculo_pension()

    st.sidebar.dataframe(pension_df)