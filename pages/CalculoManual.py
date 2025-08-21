import streamlit as st
import pandas as pd
import numpy as np
import time
import sys
import os
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.calculations import PensionManual, tabla_aguinaldo
from utils.currency_utils import convert_string_currency
st.title("Cálculo Manual")

wid_1, wid_2, wid_3 = st.columns(3)

edad_pension = wid_1.selectbox(
    "Edad al pensionarse",
    ("60", "61", "62", "63", "64", "65+"),
    index=1
)

if edad_pension == "65+":
    edad_pension = 65
else:
    edad_pension = int(edad_pension)

fecha_pension = wid_2.date_input(label="Fecha de pensión",
                                 min_value=pd.to_datetime("2015-01-01"),
                                 max_value=pd.to_datetime("2030-01-01"),
                                 )
year = fecha_pension.year
semanas_reconocidas = wid_3.number_input(label="Semana de Reconocidas",
                                      min_value=500,
                                      step=1)

wid_4, wid_5 = st.columns(2)
salario_promedio = wid_4.number_input(
    label="Salario Diario Promedio últimas 250 semanas (MXN)",
    min_value=1.0,
    value=1760.0,
    format="%.2f"
)
# We will format it as a percentage
porcentaje_asignaciones = wid_5.number_input(max_value=100,
                                          min_value=15,
                                             step=5,
                                          value=25,
                                          label="Porcentaje de Asignaciones Familiares")
porcentaje_asignaciones /= 100
calcular_pension = st.button("Calcular Pensión")

st.write(calcular_pension)

# Example Usage
if calcular_pension:
    with st.spinner('Procesando...'):
        time.sleep(2)
    pension_manual = PensionManual(edad_pension=edad_pension,
                                   year=year, semanas_reconocidas=semanas_reconocidas,
                                   salario_promedio=salario_promedio,
                                   porcentaje_asignaciones=porcentaje_asignaciones)

    pension_df, detalles_df = pension_manual.calculo_pension()

    valor_pension = convert_string_currency(pension_df['Pensión Final'].values[0])
    st.dataframe(pension_df)
    st.write(pension_df['Pensión Final'].values[0])
    st.dataframe(detalles_df)

    st.write("Aguinaldo")

    tabla_aguinaldo_num, tabla_aguinaldo_str = tabla_aguinaldo(fecha_inicio=fecha_pension,
                                 pension_final=valor_pension,
                                 year_max=2040,
                                 perc_asignaciones_familiares=porcentaje_asignaciones, year_cambio_asignaciones=None, perc_restar=None)
    st.dataframe(tabla_aguinaldo_str)