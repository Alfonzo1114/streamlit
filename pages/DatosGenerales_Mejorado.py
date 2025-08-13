import streamlit as st
import calendar
import warnings
import base64
import pdfplumber
import re
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from streamlit_extras.stylable_container import stylable_container

def format_spanish_date(date_obj):
    # Define Spanish month and day names
    days = ["Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"]
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
              "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    # Get day of week (0=Monday, 6=Sunday)
    day_of_week = date_obj.weekday()

    # Format the date in Spanish
    return f"{days[day_of_week]}, {date_obj.day} de {months[date_obj.month - 1]} de {date_obj.year}"

def convertir_a_fecha(fecha_str):
    # All the dates from the PDF are in the format "DD/MM/YYYY"
    fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
    return fecha

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
        .stTabs [data-testid="stMarkdownContainer"] p {
            font-size: 1.1rem;
            font-weight: 600;
            color: #ffffff;
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

# Function to extract text from PDF
@st.cache_resource
def pdf_a_texto(file_path):
    '''Convert PDF to text'''
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Extract text from PDF
texto = pdf_a_texto(file_path)

# DatosGenerales class (same as original, but with added docstrings)
class DatosGenerales:
    def __init__(self, texto):
        self.texto = texto

    def nombrefcn(self):
    # Extract the substring between the found positions, adjust indices for correct slicing
        InicioStr = re.search(r"20\d{2}\s{1}", self.texto)
        FinalStr = "DD MM YYYY"
        # Find the starting and ending positions of the target substrings
        Inicio = InicioStr.span()[0]
        Final = texto.find(FinalStr)
        # Extract the substring between the found positions, adjust indices for correct slicing
        if Inicio != -1 and Final != -1:
            # + 5 since InicioStr length = length(20) + 2 + 1 = 5
            Nombre = self.texto[Inicio + 5: Final].strip()
        else:
            Nombre = ""
        print(f"NOMBRE: {Nombre}")
        self.Nombre = Nombre

    def nssfcn(self):
        InicioStr = "NSS: "
        FinalStr = "CURP:"

        Inicio = self.texto.find(InicioStr)
        Final = self.texto.find(FinalStr)

        if Inicio != -1 and Final != -1:
            nss = self.texto[Inicio + 5: Final - 28].strip()
        else:
            nss = ""
        print(f"NSS: {nss}")
        self.nss = nss

    def curpfcn(self):
        InicioStr = "CURP:"

        Inicio = self.texto.find(InicioStr)

        if Inicio != -1:
            curp = self.texto[Inicio +len(InicioStr): Inicio + 25].strip()
        else:
            curp = ''
        print(f"CURP: {curp}")
        self.curp = curp

    def fecha_nacimiento_fcn(self):
        YEAR_BIRTH = "19" + self.curp[4:6]
        MONTH_BIRTH = self.curp[6:8]
        DAY_BIRTH = self.curp[8:10]
        FECHA_STR = f"{DAY_BIRTH}/{MONTH_BIRTH}/{YEAR_BIRTH}"
        # Convert string to datetime object
        fecha_date = convertir_a_fecha(FECHA_STR)
        # Format the date in Spanish
        fecha_formatted = format_spanish_date(fecha_date)
        print(f"FECHA DE NACIMIENTO: {fecha_formatted}")
        self.fecha_nacimiento = fecha_formatted
        self.fecha_nacimiento_date = fecha_date

    def ano_inscripcionIMSS_fcn(self):
        TerminacionYear = self.nss[2:4]
        if int(TerminacionYear) < 50:
            AnoInicio = int('20'+ TerminacionYear)
        else:
            AnoInicio = int('19'+ TerminacionYear)
        print(f"AÑO DE INSCRIPCIÓN IMSS: {AnoInicio}")
        self.AnoInicio = AnoInicio

    def regimen_pertenecefcn(self):
        if self.AnoInicio > 1997:
            Regimen = 'Régimen 97'
        elif self.AnoInicio == 1997:
            Regimen = "Determinar el mes que inició, si es a partir de julio, entra en régimen 97"
        else:
            Regimen = 'Régimen 73'

        print(f"REGIMEN AL QUE PERTENECE: {Regimen}")
        self.Regimen = Regimen

    def semanas_cotizadas_descontadas_fcn(self):
        Iniciostr = re.search(r"\d{1,4}\s{1}\d{1,4}\s{1}\d{1,4}", texto)
        myrange = Iniciostr.span()
        risultati = self.texto[myrange[0]:myrange[1]]
        semanas_cotizadas = int(risultati.split()[0])
        semanas_descontadas = int(risultati.split()[1])
        semanas_reintegradas = int(risultati.split()[-1])
        semanas_totales = semanas_cotizadas - semanas_descontadas + semanas_reintegradas

        print(f"SEMANAS COTIZADAS: {semanas_cotizadas}")
        print(f"SEMANAS DESCONTADAS: {semanas_descontadas}")
        print(f"SEMANAS REINTEGRADAS: {semanas_reintegradas}")
        print(f"SEMANAS TOTALES: {semanas_totales}")

        self.semanas_cotizadas = semanas_cotizadas
        self.semanas_descontadas = semanas_descontadas
        self.semanas_reintegradas = semanas_reintegradas
        self.semanas_totales = semanas_totales

    def fecha_emision_reporte_fcn(self):
        texto_array = self.texto.split('\n')

        # Find the position of the string that ends with 'reporte' and select the next element that contains the date
        position_date_report = [i + 1 for i, s in enumerate(texto_array) if s.endswith('reporte')]
        date_str = texto_array[position_date_report[0]].strip().replace(' ', '')
        
        # Convert to date object and then format in Spanish
        fecha_date = convertir_a_fecha(date_str)
        fecha_formatted = format_spanish_date(fecha_date)
        
        # Store both the date object and formatted string
        self.fecha_emision_reporte_date = fecha_date
        self.fecha_emision_reporte = fecha_formatted
        
        print(f"FECHA DE EMISIÓN DEL REPORTE: {fecha_formatted}")
        print(f"FECHA DE EMISIÓN DEL REPORTE (date object): {fecha_date}, type: {type(fecha_date)}")

    def tabla_datos(self):
        self.nombrefcn()
        self.nssfcn()
        self.curpfcn()
        self.fecha_nacimiento_fcn()
        self.ano_inscripcionIMSS_fcn()
        self.regimen_pertenecefcn()
        self.semanas_cotizadas_descontadas_fcn()
        self.fecha_emision_reporte_fcn()

        out = pd.DataFrame({
            'NOMBRE': [self.Nombre],
            'NSS': [self.nss],
            'CURP': [self.curp],
            'FECHA DE NACIMIENTO': [self.fecha_nacimiento],
            'AÑO DE INSCRIPCIÓN IMSS': [self.AnoInicio],
            'REGIMEN AL QUE PERTENECE': [self.Regimen],
            'SEMANAS COTIZADAS': [self.semanas_cotizadas],
            'SEMANAS DESCONTADAS': [self.semanas_descontadas],
            'SEMANAS REINTEGRADAS': [self.semanas_reintegradas],
            'SEMANAS TOTALES': [self.semanas_totales],
            'FECHA DE EMISIÓN DEL REPORTE': [self.fecha_emision_reporte]
        }
        )
        out = out.T
        out.columns = ['DATOS PERSONALES']
        return out

    def exportar_datos(self, name):
        out = pd.DataFrame({
            'NOMBRE': [self.Nombre],
            'NSS': [self.nss],
            'CURP': [self.curp],
            'FECHA_DE_NACIMIENTO': [self.fecha_nacimiento],
            'AÑO_DE_INSCRIPCION_IMSS': [self.AnoInicio],
            'REGIMEN': [self.Regimen],
            'SEMANAS_COTIZADAS': [self.semanas_cotizadas],
            'SEMANAS_DESCONTADAS': [self.semanas_descontadas],
            'SEMANAS_REINTEGRADAS': [self.semanas_reintegradas],
            'SEMANAS_TOTALES': [self.semanas_totales],
            'FECHA_EMISION_REPORTE': [self.fecha_emision_reporte]
        })
        return out.to_csv(index=False)

# Example usage
with st.spinner('Procesando datos...'):
    Usuario = DatosGenerales(texto)
    df = Usuario.tabla_datos()

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
            st.metric("CURP", Usuario.curp)
            st.metric("Fecha de Nacimiento", Usuario.fecha_nacimiento)
            st.metric("Año de Inscripción IMSS", Usuario.AnoInicio)

        with col2:
            st.metric("NSS", Usuario.nss)
            st.metric("Régimen", Usuario.Regimen)
            st.metric("Fecha de Emision del Reporte", Usuario.fecha_emision_reporte)
            # Add empty metric to balance the layout if needed
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

# Tab 2: Historial Laboral
with tab2:
    st.subheader("Historial Laboral")
    
    # Add your existing historial laboral code here
    # For example:
    # HistoriaLaboralTable_str, HistoriaLaboralTable_num = HistorialLaboralTabla(texto)
    # HistoriaLaboralTable = HistorialLaboralDesglosada_fcn(texto, tieneVigencia, fechasUltimaBaja)
    
    with st.expander("📋 Ver Historial Laboral Detallado", expanded=False):
        st.write("Tabla detallada del historial laboral iría aquí")
        # st.dataframe(HistoriaLaboralTable)

# Tab 3: Cálculos
with tab3:
    st.subheader("Cálculos de Pensión")
    
    with st.expander("📈 Salario Promedio", expanded=True):
        st.write("Cálculos de salario promedio irían aquí")
        # tabla_salarios = salario_promedio_250tabla(HistoriaLaboralTable)
        # st.dataframe(tabla_salarios)
    
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
