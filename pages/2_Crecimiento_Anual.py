import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Crecimiento Anual",
    page_icon="📈",
    layout="wide"
)

st.title("Crecimiento Anual")

# Sidebar for inputs
with st.sidebar:
    st.header("Parámetros de Cálculo")
    
    # Pensión Mensual (currency input)
    pension_mensual = st.number_input(
        "Pensión Mensual",
        min_value=0.0,
        step=100.0,
        format="%.2f",
        value=0.0,
        help="Ingrese el monto de la pensión mensual"
    )
    
    # Año de pensión (integer input with min/max)
    anio_pension = st.number_input(
        "Año de pensión",
        min_value=2015,
        max_value=2030,
        step=1,
        value=date.today().year,
        help="Seleccione el año de la pensión"
    )
    
    # Cambio de asignaciones familiares (percentage input)
    cambio_asignaciones = st.number_input(
        "Nuevo porcentaje de asignaciones familiares (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        value=0.0,
        format="%.1f",
        help="Ingrese el porcentaje de cambio en asignaciones familiares"
    )
    
    # Conditional date input
    if cambio_asignaciones > 0:
        fecha_cambio = st.date_input(
            "Fecha de cambio de asignaciones",
            value=date.today(),
            min_value=date(2015, 1, 1),
            max_value=date(2030, 12, 31),
            help="Seleccione la fecha del cambio de asignaciones"
        )

# Main content area
st.write("Bienvenido a la página de Crecimiento Anual. Aquí podrás ver el análisis de crecimiento anual.")

# Display the selected values
with st.expander("Resumen de parámetros"):
    st.write(f"- Pensión Mensual: ${pension_mensual:,.2f}")
    st.write(f"- Año de Pensión: {anio_pension}")
    
    if cambio_asignaciones > 0:
        st.write(f"- Nuevo porcentaje de asignaciones familiares: {cambio_asignaciones:.1f}%")
        st.write(f"- Fecha de cambio: {fecha_cambio.strftime('%d/%m/%Y')}")
    else:
        st.write("- Sin cambios en asignaciones familiares")
