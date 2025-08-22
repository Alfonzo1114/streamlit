import streamlit as st
import base64

from streamlit_extras.stylable_container import stylable_container

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import convert_double_currency

from core.data_processing import (
    pdf_a_texto,
    DatosGenerales,
    FechasGenerales,
    HistorialLaboralTabla_fcn,
    HistorialLaboralDesglosada_fcn,
    SessionVars
)
session = SessionVars()
from core.calculations import salario_promedio_fcn, salario_promedio_250tabla


# Set page config
st.set_page_config(
    page_title="Datos Generales - Mejorado",
    page_icon="📋",
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
        /* Target only the tab headers */
        .stTabs [role="tab"] [data-testid="stMarkdownContainer"] p {
            font-size: 1.1rem;
            font-weight: 600;
            color: #ffffff;
        }
        
        /* Style for metric values */
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

# Title and sidebar setup
st.title("📋 Datos Generales")
st.sidebar.title("📊 Parámetros del Usuario")

# PDF Upload and Display
with st.sidebar:
    st.markdown("### 📄 Documento PDF")
    
    # File uploader with custom styling
    with stylable_container(
        key="file_uploader_container",
        css_styles="""
            {
                border: 2px dashed #cbd5e1;
                border-radius: 0.5rem;
                padding: 1rem;
                text-align: center;
                margin-bottom: 1rem;
            }
        """,
    ):
        uploaded_file = st.file_uploader(
            label="Sube un archivo PDF",
            type=["pdf"],
            label_visibility="collapsed",
            accept_multiple_files=False,
            help="Sube tu archivo PDF con los datos del trabajador"
        )
    
    # Default file path if no file is uploaded
@st.cache_resource
def file_path_fcn(file_path=None):
    if file_path is None:
        file_path = 'REPORTES/RICARDO.pdf'  # Default file path
    return file_path

file_path = file_path_fcn(file_path=uploaded_file)

# Display PDF in sidebar if uploaded or using default
if uploaded_file is not None:
    base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
    pdf_display = f"""
    <div style="border: 1px solid #e2e8f0; border-radius: 0.5rem; overflow: hidden; margin-top: 1rem;">
        <div style="background: #f8fafc; padding: 0.5rem; border-bottom: 1px solid #e2e8f0; font-weight: 600;">
            Vista Previa del PDF
        </div>
        <iframe src="data:application/pdf;base64,{base64_pdf}" 
                width="100%" 
                height="500" 
                style="border: none;">
        </iframe>
    </div>
    """
    st.sidebar.markdown(pdf_display, unsafe_allow_html=True)
else:
    # Show default PDF preview
    try:
        with open('REPORTES/RICARDO.pdf', 'rb') as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 0.5rem; overflow: hidden; margin-top: 1rem;">
                <div style="background: #f0fdf4; padding: 0.5rem; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #166534;">
                    📋 PDF por defecto cargado
                </div>
                <iframe src="data:application/pdf;base64,{base64_pdf}" 
                        width="100%" 
                        height="500" 
                        style="border: none;">
                </iframe>
            </div>
            """
            st.sidebar.markdown(pdf_display, unsafe_allow_html=True)
    except FileNotFoundError:
        st.sidebar.warning("No se encontró el archivo PDF por defecto en la ruta 'REPORTES/RICARDO.pdf'")

# Extract text from PDF
texto = pdf_a_texto(file_path)

# Example usage
with st.spinner('Procesando datos...'):
    Usuario = DatosGenerales(texto)
    df = Usuario.tabla_datos()

fechas_generales = FechasGenerales(texto=texto,
                                   FechaEmisionReporte=Usuario.fecha_emision_reporte_string)

fechasGeneralesNumerico, fechasGeneralesDate, sigueCotizando, fechasUltimaBaja = fechas_generales.tabla_fechas_generales()

HistoriaLaboralTable_str, HistorialLaboralTable_num = HistorialLaboralTabla_fcn(texto)

HistoriaLaboralTable, HistorialLaboralTable_str_desglosada = HistorialLaboralDesglosada_fcn(HistoriaLaboralTable=HistorialLaboralTable_num,
                                                                                            sigueCotizando=sigueCotizando,
                                                                                            FechasUltimaBaja=fechasUltimaBaja)
session.set("Historia Laboral Table", HistoriaLaboralTable)
tabla_salarios_date, tabla_salarios_str = salario_promedio_250tabla(HistoriaLaboralTable)
session.set("Tabla Salarios", tabla_salarios_date)

SEMANAS_CONTAR = min(250, int(Usuario.semanas_cotizadas))
SALARIO_PROMEDIO_DIARIO, tabla_salario_promedio_num, tabla_salario_promedio_str = salario_promedio_fcn(semanas_contar=SEMANAS_CONTAR,
                                                                                                        semanas_reconocidas=Usuario.semanas_totales,
                                                                                                 tabla_salarios=tabla_salarios_date)
# Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["📋 Datos Personales", "📅 Historial Laboral", "💰 Cálculos"])

# Tab 1: Datos Personales
with tab1:
    st.subheader("Información Personal")
    
    # Personal Information Card
    with st.expander("📌 Datos Básicos", expanded=True):
            # Using a 3:2 ratio for better space distribution
        col1, col2 = st.columns([3, 2])
        with col1:
            st.metric("Nombre", Usuario.Nombre)
            session.set("Nombre", Usuario.Nombre)
            st.metric("CURP", Usuario.curp)
            st.metric("Fecha de Nacimiento", Usuario.fecha_nacimiento_string)
            st.metric("Año de Inscripción al IMSS", Usuario.AnoInicio)
            if sigueCotizando:
                st.metric("Sigue Cotizando", "Si")
            else:
                st.metric("Sigue Cotizando", "No")


        with col2:
            st.metric("NSS", Usuario.nss)
            st.metric("Régimen", Usuario.Regimen)
            st.metric("Fecha de Emision del Reporte", Usuario.fecha_emision_reporte_string, )
            # Add empty metric to balance the layout if needed
            st.metric("Salario Promedio últimas " + str(min(250, int(Usuario.semanas_cotizadas))) + " semanas", convert_double_currency(SALARIO_PROMEDIO_DIARIO))
            st.metric(" ", " ")
    
    # Weeks Information Card
    with st.expander("📊 Semanas Cotizadas", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cotizadas", Usuario.semanas_cotizadas)
        with col2:
            st.metric("Descontadas", Usuario.semanas_descontadas)
        with col3:
            st.metric("Reintegradas", Usuario.semanas_reintegradas)
        with col4:
            st.metric("Totales", Usuario.semanas_totales)
            session.set("Semanas Totales", Usuario.semanas_totales)

# Tab 2: Historial Laboral
with tab2:
    st.subheader("Historial Laboral")
    # HistoriaLaboralTable_str
    # Add your existing historial laboral code here
    with st.expander("📋 Ver Historial Laboral Detallado", expanded=False):
        if fechasGeneralesDate is not None:
            st.write("Tabla detallada del historial laboral")
            st.dataframe(fechasGeneralesDate)
        else:
            st.write("No se encontraron datos de historial laboral.")

    with st.expander("📋 Ver Historial de movimientos", expanded=False):
        if fechasGeneralesDate is not None:
            st.write("Tabla detallada de Movimientos")
            st.dataframe(HistoriaLaboralTable_str)
        else:
            st.write("No se encontraron datos de historial laboral.")

    with st.expander("📋 Ver Historial Laboral Desglosado", expanded=False):
        if HistoriaLaboralTable is not None:
            st.write("Tabla detallada del historial laboral")
            st.dataframe(HistorialLaboralTable_str_desglosada)
        else:
            st.write("No se encontraron datos de historial laboral.")

# Tab 3: Cálculos
with tab3:
    st.subheader("Cálculos de Pensión")
    
    with st.expander("📈 Salario Promedio", expanded=True):
        # Calculate the maximum value for the slider (minimum between 250 and semanas_cotizadas)
        max_semanas = min(250, int(Usuario.semanas_cotizadas))
        semanas_seleccionadas = st.slider(
            "Número de semanas a considerar:",
            min_value=1,
            max_value=max_semanas,
            value=max_semanas,  # Default to the maximum value
            step=1,
            help=f"Selecciona el número de semanas (máximo {max_semanas})"
        )
        st.write(f"Cálculos de salario promedio para {semanas_seleccionadas} semanas")
        # tabla_salarios_date, tabla_salarios_str = salario_promedio_250tabla(HistoriaLaboralTable)
        st.dataframe(tabla_salarios_str)
    
    with st.expander("📅 Fechas Clave", expanded=True):
        st.write("Fechas importantes para la pensión irían aquí")
        # st.metric("Fecha de Pensión Mínima", fecha_pension_minima)

# Add some spacing at the bottom
st.markdown("---")
st.caption("© 2025 Sistema de Análisis de Pensiones - Carlos Alfonzo")

# Add a button to export data
if st.button("📥 Exportar Datos", use_container_width=True):
    # Add export functionality here
    st.success("¡Datos exportados exitosamente!")

if "dynamic_vars" not in st.session_state:
    st.session_state.dynamic_vars = {}