import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date
from core.calculations import crecimiento_anual_pension_fcn

# Custom CSS for better UI
st.set_page_config(
    page_title="Crecimiento Anual",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
        .main {
            max-width: 1200px;
            padding: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre;
            background-color: #2d3748;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding: 0 20px;
            color: #e2e8f0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4a5568;
            border-color: #4a5568;
            color: #ffffff;
        }
        .stTabs [role="tab"] [data-testid="stMarkdownContainer"] p {
            font-size: 1.1rem;
            font-weight: 600;
            color: #ffffff;
        }
        [data-testid="stMetricValue"] > div {
            font-size: 1.5rem;
        }
        .stExpander {
            background: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 0.5rem;
            margin: 1rem 0;
            color: #e2e8f0;
        }
        .stExpander .streamlit-expanderHeader {
            background-color: #2d3748;
            color: #ffffff;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem 0.5rem 0 0;
            font-weight: 600;
        }
        .stExpander .streamlit-expanderContent {
            padding: 1rem;
            background-color: #2d3748;
            color: #e2e8f0;
        }
        .stExpander .stMarkdown p, 
        .stExpander .stMarkdown h1, 
        .stExpander .stMarkdown h2, 
        .stExpander .stMarkdown h3, 
        .stExpander .stMarkdown h4, 
        .stExpander .stMarkdown h5, 
        .stExpander .stMarkdown h6 {
            color: #e2e8f0 !important;
        }
    </style>
""", unsafe_allow_html=True)

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
        min_value=0,
        max_value=100,
        step=5,
        value=0,
        # format="%.1f",
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

    calculate_button = st.button("Calcular")

# Initialize session state for chart type if it doesn't exist
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = 'line'

# Main content area
st.markdown('### Bienvenido a la página de Crecimiento Anual. Aquí podrás ver el análisis de crecimiento anual.')

if calculate_button:
    with st.spinner('Calculando crecimiento anual...'):
        # Calculate the growth data
        tabla_crecimiento_num, tabla_crecimiento_str = crecimiento_anual_pension_fcn(
            ano_pension=anio_pension, 
            pension_final=pension_mensual, 
            year_max=2030
        )
        
        # Store the data in session state to avoid recalculation
        st.session_state.tabla_crecimiento_num = tabla_crecimiento_num
        st.session_state.tabla_crecimiento_str = tabla_crecimiento_str

# Check if we have data to display
if 'tabla_crecimiento_num' in st.session_state and 'tabla_crecimiento_str' in st.session_state:
    # Create two columns for the chart and data
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chart type selector
        chart_type = st.radio(
            "Tipo de gráfico:",
            ["Línea", "Barras"],
            horizontal=True,
            key='chart_type_radio'
        )
        
        # Convert the data to a DataFrame for easier plotting
        df = st.session_state.tabla_crecimiento_num
        
        # Create the appropriate chart based on selection
        if chart_type == "Línea":
            fig = px.line(
                df, 
                x='Año', 
                y='Pensión recibida mensual',
                title='Crecimiento Anual de la Pensión',
                labels={'Pensión': 'Pensión ($)', 'Año': 'Año'},
                markers=True
            )
        else:  # Bar chart
            fig = px.bar(
                df, 
                x='Año', 
                y='Pensión recibida mensual',
                title='Crecimiento Anual de la Pensión',
                labels={'Pensión': 'Pensión ($)', 'Año': 'Año'},
                text_auto='.2s'
            )
        
        # Update layout for better appearance
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#4a5568'),
            margin=dict(l=20, r=20, t=50, b=20),
            height=500
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display the data table
        with st.expander("📊 Datos Detallados", expanded=True):
            st.dataframe(
                st.session_state.tabla_crecimiento_str,
                use_container_width=True,
                height=500
            )
            
            # Add download button for the data
            csv = st.session_state.tabla_crecimiento_str.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Datos",
                data=csv,
                file_name='crecimiento_anual_pension.csv',
                mime='text/csv'
            )
    
    # Show summary metrics
    st.subheader("Resumen")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Pensión Inicial",
            value=f"${st.session_state.tabla_crecimiento_num['Pensión'].iloc[0]:,.2f}"
        )
    
    with col2:
        st.metric(
            label="Pensión Final",
            value=f"${st.session_state.tabla_crecimiento_num['Pensión'].iloc[-1]:,.2f}"
        )
    
    with col3:
        growth_rate = ((st.session_state.tabla_crecimiento_num['Pensión'].iloc[-1] / 
                      st.session_state.tabla_crecimiento_num['Pensión'].iloc[0]) - 1) * 100
        st.metric(
            label="Crecimiento Total",
            value=f"{growth_rate:.2f}%"
        )
