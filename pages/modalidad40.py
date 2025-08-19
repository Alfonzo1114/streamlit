import streamlit as st
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.calculations import pagos40, PensionManual, pivot_pagos40, heatmap_pagos40

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

    # Tabs structure similar to DatosGenerales_Mejorado
    tab1, tab2, tab3 = st.tabs(["📄 Pagos", "📊 Resumen y Heatmap", "🧮 Pensión Manual"])

    with tab1:
        st.subheader("Pagos en Modalidad 40")
        with st.expander("📋 Ver tabla de pagos", expanded=True):
            st.dataframe(tabla_pago40_string, use_container_width=True)

    # Compute pension and pivot only once
    pension_df, detalles_df = pension_manual.calculo_pension()
    ordered_pivot_table, ordered_pivot_table_string, total_payment = pivot_pagos40(tabla_pago40)

    with tab2:
        st.subheader("Resumen por Año/Mes")
        # Show metric as first row, not in a cramped side column
        st.markdown("## Total a pagar")
        st.metric(label="Total a pagar", value=total_payment)

        with st.expander("📋 Tabla dinámica (pivot)", expanded=True):
            st.dataframe(ordered_pivot_table_string, use_container_width=True)

        # Heatmap with default colorscale
        with st.expander("📊 Mapa de Calor", expanded=True):
            fig = heatmap_pagos40(ordered_pivot_table)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Cálculo de Pensión (Manual)")
        with st.expander("📋 Resumen de pensión", expanded=True):
            st.dataframe(pension_df, use_container_width=True)
        with st.expander("📋 Detalles del cálculo", expanded=False):
            st.dataframe(detalles_df, use_container_width=True)