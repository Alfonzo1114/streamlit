import streamlit as st
import pandas as pd
import numpy as np
import time
import sys
import os
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.calculations import PensionManual

st.title("Cálculo Manual")

wid_1, wid_2, wid_3 = st.columns(3)

edad_pension = wid_1.selectbox(
    "Edad al pensionarse",
    ("60", "61", "62", "63", "64", "65+"),
)

if edad_pension == "65+":
    edad_pension = 65
else:
    edad_pension = int(edad_pension)


year = wid_2.number_input(label="Año de pensión",
                       min_value=2015,
                       step=1)

semanas_reconocidas = wid_3.number_input(label="Semana de Reconocidas",
                                      min_value=500,
                                      step=1)

wid_4, wid_5 = st.columns(2)
salario_promedio = wid_4.number_input(
    label="Salario Diario Promedio últimas 250 semanas (MXN)",
    min_value=1.0,
    format="%.2f"
)
# We will format it as a percentage
porcentaje_asignaciones = wid_5.number_input(max_value=100,
                                          min_value=15,
                                          label="Porcentaje de Asignaciones Familiares")
porcentaje_asignaciones /= 100
calcular_pension = st.button("Calcular Pensión")

st.write(calcular_pension)
# @st.cache_resource
# class PensionManual:
#     def __init__(self, edad_pension, year, semanas_reconocidas, salario_promedio, porcentaje_asignaciones):
#         self.edad_pension = edad_pension
#         self.year = year
#         self.semanas_reconocidas = semanas_reconocidas
#         self.salario_promedio = salario_promedio
#         self.porcentaje_asignaciones = porcentaje_asignaciones
#         self.tabla_salarios_minimos = pd.read_csv('TABLAS/TABLA_SALARIOSMINIMOS.txt', sep='\t')
#         self.tabla_porcentaje_edad = pd.read_csv('TABLAS/TABLA_PORCENTAJE_EDAD.txt', sep='\t')
#         self.tabla_uma = pd.read_csv('TABLAS/TABLA_UMA.txt', sep='\t')
#         self.tabla_relacion_umas = pd.read_csv('TABLAS/TABLA_RELACION_UMAS_SALARIO_MINIMO.txt', sep='\t')
#
#     def salario_minimo_garantizado_fcn(self):
#             tabla = self.tabla_salarios_minimos
#             out = tabla[tabla.iloc[:, 0] == year]
#             salario_minimo_ano_actual = out.iloc[0, 1].strip("$")
#             salario_minimo_mensual = out.iloc[0, 4]
#             pension_minima_garantizada = out.iloc[0, -1]
#             salario_maximo_asignado_diario = out.iloc[0, 6]
#
#             # We will also create a pandas dataframe
#             df = pd.DataFrame({
#                 # 'Año': year,
#                 'Salario Minimo Diario': salario_minimo_ano_actual,
#                 'Salario Minimo Mensual': salario_minimo_mensual,
#                 'Pension Mínima Garantizada': pension_minima_garantizada,
#                 'Salario Máximo Asignado Diario': salario_maximo_asignado_diario
#             }, index=[self.year])
#             self.salario_minimo_ano_actual = salario_minimo_ano_actual
#             self.salario_minimo_mensual = salario_minimo_mensual
#             self.pension_minima_garantizada = pension_minima_garantizada
#             self.salario_maximo_asignado_diario = salario_maximo_asignado_diario
#
#             return salario_minimo_ano_actual, salario_minimo_mensual, pension_minima_garantizada, salario_maximo_asignado_diario, df
#
#     def porcentaje_vejez_fcn(self):
#         tabla = self.tabla_porcentaje_edad
#         idx = tabla[tabla['EDAD'] == min(self.edad_pension, 65)]['% PENSIÓN'] # Finds the position of the table with the target age
#         perc_string = idx.iloc[0] # Obtain the percentage by multiplying by 100%
#         porcentaje_vejez =float( perc_string.strip('%')) / 1e2
#         self.porcentaje_vejez = porcentaje_vejez
#
#     def valor_uma_actual_year_fcn(self):
#         tabla = self.tabla_uma
#         idx = tabla[tabla['AÑO'] == self.year]['VALOR $'] # Finds the position of the table with the target year
#         valor_uma_string = idx.iloc[0]
#         valor_uma_numerico =float( valor_uma_string.strip('$'))
#         self.valor_uma_numerico = valor_uma_numerico
#
#     def relacion_uma_salario_fcn(self):
#         relacion_salario_uma = round(self.salario_promedio / self.valor_uma_numerico, 2)
#         self.relacion_uma_salario = relacion_salario_uma
#
#     def porcentaje_cuantia_fcn(self):
#         tabla = self.tabla_relacion_umas
#         #subs substracts the variable from all values and then we take only those values inferior, finally we take the pos. of the largest value
#         closest_idx = tabla[tabla["Inferior"].sub(self.relacion_uma_salario) < 0]['Inferior'].idxmax()
#         out_string = tabla.iloc[closest_idx, 2] # Pos. 2 relates to Porcentaje cuantía básica [%]
#         porcentaje_cuantia = float(out_string.strip(('%')))/1e2
#         self.porcentaje_cuantia = porcentaje_cuantia
#
#     def semanas_equivalentes_year_fcn(self):
#         semanas_despues500 = semanas_reconocidas - 500
#         upper_bound = 0.5
#         lower_bound = 0.25
#         if lower_bound < abs(semanas_despues500/52 - np.fix(semanas_despues500/52)) <= upper_bound:
#             SEMANAS_EQUIVALENTES = np.fix(semanas_despues500 / 52) + 0.5
#         else:
#             SEMANAS_EQUIVALENTES = np.round(semanas_despues500/52, decimals=0)
#         self.semanas_equivalentes = SEMANAS_EQUIVALENTES
#
#     def salario_incremento_anual_perc_fcn(self):
#         tabla = self.tabla_relacion_umas
#         closest_idx = (tabla['Porcentaje cuantía básica \r\n[%]'].str.replace('%', '', regex=True)).astype(float)
#         closest_idx = closest_idx.sub(self.porcentaje_cuantia*1e2) <= 0
#         closest_idx = tabla[closest_idx]['Salario incremento anual [%]'].idxmax()
#         salario_incremento_anual_perc = tabla.loc[closest_idx, 'Salario incremento anual [%]']
#         salario_incremento_anual_perc = float(salario_incremento_anual_perc.strip('%')) / 1e2
#         self.salario_incremento_anual_perc = salario_incremento_anual_perc
#
#     def incremento_perc_fcn(self):
#         incremento_perc = round(self.salario_incremento_anual_perc * self.semanas_equivalentes, 4)
#         self.incremento_perc = incremento_perc
#         return incremento_perc
#
#     def incremento_dinero_fcn(self):
#         incremento_dinero = round(self.incremento_perc * self.salario_promedio * 1.11 * 365, 2)
#         self.incremento_dinero = incremento_dinero
#         # return incremento_dinero
#
#     def cuantia_basica_anual_fcn(self):
#         cuantia_basica_anual = round(self.porcentaje_cuantia * self.salario_promedio * 365 * 1.11, 2)
#         self.cuantia_basica_anual = cuantia_basica_anual
#         # return cuantia_basica_anual
#
#     def cuantia_vejez_fcn(self):
#         cuantia_vejez = self.cuantia_basica_anual + self.incremento_dinero
#         self.cuantia_vejez = cuantia_vejez
#
#     def pension_cesantia_edad_avanzada_fcn(self):
#         pension_cesantia_edad_avanzada = round(self.cuantia_vejez * self.porcentaje_vejez, 2)
#         self.pension_cesantia_edad_avanzada = pension_cesantia_edad_avanzada
#
#     def importe_asignaciones_familiares_fcn(self):
#         importe_asignaciones_familiares = round(self.porcentaje_asignaciones * self.pension_cesantia_edad_avanzada, 2)
#         self.importe_asignaciones_familiares = importe_asignaciones_familiares
#
#     def importe_anual_cesantia_fcn(self):
#         importe_anual_cesantia = round(self.importe_asignaciones_familiares + self.pension_cesantia_edad_avanzada, 2)
#         self.importe_anual_cesantia = importe_anual_cesantia
#
#     def importe_mensual_calculado_fcn(self):
#         importe_mensual_calculado = round(self.importe_anual_cesantia / 12, 1)
#         self.importe_mensual_calculado = importe_mensual_calculado
#
#     def pension_minima_garantizada_fcn(self):
#         pension_minima_garantizada = self.pension_minima_garantizada.replace('$', '').replace(',', '')
#         pension_minima_garantizada = float(pension_minima_garantizada)
#         self.pension_minima_garantizada = pension_minima_garantizada
#
#     def pension_final_fcn(self):
#         pension_final = round(max(self.importe_mensual_calculado, self.pension_minima_garantizada), 2)
#         self.pension_final = pension_final
#
#     def calculo_pension(self):
#         self.salario_minimo_garantizado_fcn()
#         self.porcentaje_vejez_fcn()
#         self.valor_uma_actual_year_fcn()
#         self.relacion_uma_salario_fcn()
#         self.porcentaje_cuantia_fcn()
#         self.semanas_equivalentes_year_fcn()
#         self.salario_incremento_anual_perc_fcn()
#         self.incremento_perc_fcn()
#         self.incremento_dinero_fcn()
#         self.cuantia_basica_anual_fcn()
#         self.cuantia_vejez_fcn()
#         self.pension_cesantia_edad_avanzada_fcn()
#         self.importe_asignaciones_familiares_fcn()
#         self.importe_anual_cesantia_fcn()
#         self.importe_mensual_calculado_fcn()
#         self.pension_minima_garantizada_fcn()
#         self.pension_final_fcn()
#
#         pension_df = pd.DataFrame({'Pensión Final': [self.pension_final],
#                                    'Semanas Reconocidas': [self.semanas_reconocidas],
#                                    'Salario Promedio': [self.salario_promedio],
#                                    'Pension Final': [self.pension_final]
#                                    })
#
#         detalles_df = pd.DataFrame({
#                                    'Porcentaje Asignaciones Familiares': [self.porcentaje_asignaciones],
#                                    'Porcentaje Vejez': [self.porcentaje_vejez],
#                                    'Valor UMA Actual Year': [self.valor_uma_numerico],
#                                    'Incremento %': [self.incremento_perc],
#                                    'Incremento Dinero': [self.incremento_dinero],
#                                    'Cuantia Basica Anual': [self.cuantia_basica_anual],
#                                    'Cuantia Vejez': [self.cuantia_vejez],
#                                    'Pension Cesantia Edad Avanzada': [self.pension_cesantia_edad_avanzada],
#                                    'Importe Asignaciones Familiares': [self.importe_asignaciones_familiares],
#                                    'Importe Anual Cesantia': [self.importe_anual_cesantia],
#                                    'Importe Mensual Calculado': [self.importe_mensual_calculado],
#                                    'Pension Minima Garantizada': [self.pension_minima_garantizada],
#                                    'Pension Final': [self.pension_final]
#                                    })
#
#         detalles_df = round(detalles_df.T, 2)
#         # We will rename the column
#         detalles_df.columns = ['Valores']
#
#         return pension_df, detalles_df

# Example Usage
if calcular_pension:
    with st.spinner('Procesando...'):
        time.sleep(2)
    pension_manual = PensionManual(edad_pension=edad_pension,
                                   year=year, semanas_reconocidas=semanas_reconocidas,
                                   salario_promedio=salario_promedio,
                                   porcentaje_asignaciones=porcentaje_asignaciones)

    pension_df, detalles_df = pension_manual.calculo_pension()

    st.dataframe(pension_df)

    st.dataframe(detalles_df)