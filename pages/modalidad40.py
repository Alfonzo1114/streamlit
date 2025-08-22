import streamlit as st
import os
import sys
from dateutil.relativedelta import relativedelta
from core.data_processing import SessionVars
from core.calculations import PensionManual
from utils.currency_utils import convert_double_currency

session = SessionVars()

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.calculations import pagos40, PensionManual, pivot_pagos40, heatmap_pagos40, tabla_salarios_modificada, salario_promedio_fcn

st.sidebar.title("Parametros Generales del Usuario")
with st.sidebar:
    start_date = st.date_input("Incio de pago env Modalidad 40")

    duration = st.number_input("Duración de la Modalidad 40", min_value=0, value=25)
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
        durata=duration)

    fecha_final = start_date + relativedelta(years= int(duration / 12),
                                                       months=duration % 12) - relativedelta(days=start_date.day)

    HistoriaLaboralDesglosada = session.get("Historia Laboral Table")

    tabla_salarios_date = session.get("Tabla Salarios")

    nueva_tabla, nueva_tabla_str = tabla_salarios_modificada(tabla_salarios_original=tabla_salarios_date,
                                                             fecha_inicio=start_date,
                                                             fecha_final=fecha_final,
                                                             salario=salario_mod40)

    SEMANAS_CONTAR = 250
    SALARIO_PROMEDIO_DIARIO, tabla_salario_promedio_num, tabla_salario_promedio_str = salario_promedio_fcn(
        semanas_contar=SEMANAS_CONTAR,
        semanas_reconocidas=session.get("Semanas Totales"),
        tabla_salarios=nueva_tabla)

    # Compute pension and pivot only once
    # pension_df, detalles_df = pension_manual.calculo_pension()
    ordered_pivot_table, ordered_pivot_table_string, total_payment = pivot_pagos40(tabla_pago40)

    # nueva_edad_pension = 62 + int(duration / 12)
    # pension_manual = PensionManual(edad_pension=nueva_edad_pension,
    #                                year=year, semanas_reconocidas=semanas_reconocidas,
    #                                salario_promedio=salario_promedio, porcentaje_asignaciones=porcentaje_asignaciones)

    pension_df, detalles_df = pension_manual.calculo_pension()
    pension_final = detalles_df.loc['Pension Final']['Valores']

    # Tabs structure similar to DatosGenerales_Mejorado
    tab1, tab2, tab3 = st.tabs(["📄 Pagos", "📊 Resumen y Heatmap", "🧮 Pensión Manual"])

    with tab1:
        st.subheader("Resumen por Año/Mes")
        # Show metric as first row, not in a cramped side column
        st.markdown("## Total a pagar")
        st.metric(label="Total a pagar", value=total_payment)

        st.subheader("Pagos en Modalidad 40")
        with st.expander("📋 Ver tabla de pagos", expanded=True):
            st.dataframe(tabla_pago40_string, use_container_width=True)


    with tab2:
        st.metric(label="Nuevo Salario Promedio", value=convert_double_currency(SALARIO_PROMEDIO_DIARIO))
        with st.expander("Nueva Tabla de salarios", expanded=True):
            st.dataframe(nueva_tabla_str, use_container_width=True)

        with st.expander("Salario Promedio", expanded=True):
            st.dataframe(tabla_salario_promedio_str, use_container_width=True)

        with st.expander("📋 Tabla dinámica (pivot)", expanded=False):
            st.dataframe(ordered_pivot_table_string, use_container_width=True)

        # Heatmap with default colorscale
        with st.expander("📊 Mapa de Calor", expanded=False):
            fig = heatmap_pagos40(ordered_pivot_table)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Cálculo de Pensión (Manual)")
        with st.expander("📋 Resumen de pensión", expanded=True):
            st.dataframe(pension_df, use_container_width=True)
        with st.expander("📋 Detalles del cálculo", expanded=False):
            st.dataframe(detalles_df, use_container_width=True)