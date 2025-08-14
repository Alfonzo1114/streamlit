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

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import format_spanish_date, convertir_a_fecha, convert_double_currency

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
        FECHA_NACIMIENTO = DAY_BIRTH + '/' + MONTH_BIRTH + '/' + YEAR_BIRTH
        # Convert string to datetime object
        FECHA_NACIMIENTO_date = convertir_a_fecha(FECHA_NACIMIENTO)
        # Convert string to spanish date string
        FECHA_NACIMIENTO = format_spanish_date(FECHA_NACIMIENTO)
        print(f"FECHA DE NACIMIENTO: {FECHA_NACIMIENTO}")
        self.fecha_nacimiento = FECHA_NACIMIENTO
        self.fecha_nacimiento_date = FECHA_NACIMIENTO_date

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
        out = texto_array[position_date_report[0]]
        out = out.replace(' ', '')
        self.fecha_emision_reporte_date = convertir_a_fecha(out)
        print(f"FECHA DE EMISIÓN DEL REPORTE: {out}, type: {type(out)}")

        self.fecha_emision_reporte = format_spanish_date(out)

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

class FechasGenerales:
    def __init__(self, texto, FechaEmisionReporte):
        self.texto = texto
        self.FechaEmisionReporte = FechaEmisionReporte

    def tabla_fechas_generales(self):
        texto = self.texto
        FechaEmisionReporte = self.FechaEmisionReporte
        # Define the search string
        bajas_string = 'Fecha de baja'
        value_added = 12 # Assuming 12 characters for the date
        # Find the indices of the search string
        bajas = [m.start() for m in re.finditer(bajas_string, texto)]
        # Get the index of the first occurrence
        ultima_baja = bajas[0]
        # Calculate the end index
        ultima_final = ultima_baja + len(bajas_string) + value_added
        # Extract the desired substring
        sigue_cotizando = "vigente" in texto.lower()  #Check if sigue_cotizando is contained in the text
        # Initialize an array to store dates
        fecha_bajas = np.zeros(len(bajas), dtype=object)
        fecha_bajas_date = np.zeros(len(bajas), dtype=object)

        for idx, baja in enumerate(bajas):
            if idx == 0:
                if not sigue_cotizando:
                    fechas_ultima_baja = convertir_a_fecha(texto[ultima_baja + len(bajas_string):ultima_final].strip())
                    fecha_bajas[idx] = fechas_ultima_baja
                    fecha_bajas_date[idx] = format_spanish_date(
                        texto[ultima_baja + len(bajas_string):ultima_final].strip())
                else:
                    fecha_bajas[idx] = FechaEmisionReporte
                    fecha_bajas_date[idx] = format_spanish_date(fecha_bajas[idx])
                    fechas_ultima_baja = fecha_bajas[idx]

                if not isinstance(fechas_ultima_baja, date):
                    fechas_ultima_baja = fechas_ultima_baja.date()
            else:
                start_idx = baja + len(bajas_string)
                end_idx = start_idx + value_added  # Assuming 12 characters for the date
                fecha_bajas[idx] = texto[start_idx:end_idx].strip()
                fecha_bajas_date[idx] = format_spanish_date(fecha_bajas[idx])
                fecha_bajas[idx] = convertir_a_fecha(fecha_bajas[idx])

        altas_string = 'Fecha de alta'
        altas = [m.start() for m in re.finditer(altas_string, texto)]

        ultima_alta = altas[0]
        ultima_alta_final = ultima_alta + len(altas_string) + value_added

        fechas_ultima_alta = texto[ultima_alta + len(altas_string):ultima_alta_final].strip()

        fecha_altas = np.zeros(len(altas), dtype=object)
        fecha_altas_date = np.zeros(len(altas), dtype=object)
        dias_transcurridos_cotizados = np.zeros(len(altas), dtype=object)
        semanas_transcurridas_cotizadas = np.zeros(len(altas), dtype=object)

        for idx, alta in enumerate(altas):
            start_idx = alta + len(altas_string)
            end_idx = start_idx + value_added
            fecha_altas[idx] = convertir_a_fecha(texto[start_idx:end_idx].strip())
            fecha_altas_date[idx] = format_spanish_date(texto[start_idx:end_idx].strip())

            dias_transcurridos_cotizados[idx] = (fecha_bajas[idx] - fecha_altas[idx]).days
            semanas_transcurridas_cotizadas[idx] = dias_transcurridos_cotizados[idx] // 7

            inicio_patron_str = 'Nombre del patrón'
            final_patron_str = 'Registro Patronal'
            final_patron_str_entidad = 'Entidad federativa'
            inicio_patron = [m.start() for m in re.finditer(inicio_patron_str, texto)]
            final_patron = [m.start() for m in re.finditer(final_patron_str, texto)]

            if len(final_patron) != len(inicio_patron):
                missing_registro_patronal = [m.start() for m in re.finditer(final_patron_str_entidad, texto)]
                final_patron.append(missing_registro_patronal[-1])

            patrones = []
            # using list comprehension
            patrones = [texto[inicio + len(inicio_patron_str):final_patron[idx] - 1].strip()
                        for idx, inicio in enumerate(inicio_patron)]

            inicio_ef_str = 'Entidad federativa'
            final_ef_str = 'Fecha de alta'
            inicio_ef = [m.start() for m in re.finditer(inicio_ef_str, texto)]
            final_ef = [m.start() for m in re.finditer(final_ef_str, texto)]

            entidad_federativa = []

            for idx, inicio in enumerate(inicio_ef):
                start_idx = inicio + len(inicio_ef_str)
                end_idx = final_ef[idx] - 1
                entidad_federativa.append(texto[start_idx:end_idx].strip())

            # Alternatively, using list comprehension
            entidad_federativa = [texto[inicio + len(inicio_ef_str):final_ef[idx] - 1].strip()
                                for idx, inicio in enumerate(inicio_ef)]

            FechasGenerales_num = pd.DataFrame({
            'Fecha de alta': fecha_altas,
            'Fecha de baja': fecha_bajas,
            'Dias transcurridos cotizados': dias_transcurridos_cotizados,
            'Semanas transcurridas cotizadas': semanas_transcurridas_cotizadas,
            'Patrones': patrones,
            'Entidad federativa': entidad_federativa
        })
            FechasGenerales_date = pd.DataFrame({
            'Fecha de alta': fecha_altas_date,
            'Fecha de baja': fecha_bajas_date,
            'Dias transcurridos cotizados': dias_transcurridos_cotizados,
            'Semanas transcurridas cotizadas': semanas_transcurridas_cotizadas,
            'Patrones': patrones,
            'Entidad federativa': entidad_federativa
        })
        return FechasGenerales_num, FechasGenerales_date, sigue_cotizando, fechas_ultima_baja

def HistorialLaboralTabla_fcn(texto):
    # Define the search string
    BloqueInicio = 'Nombre del patrón'
    BloqueFinal = '* Valor del último salario base de cotización diario en pesos.'

    # Find occurrences of the start and end blocks
    Inicio = [m.start() for m in re.finditer(re.escape(BloqueInicio), texto)]
    Final = [m.start() for m in re.finditer(re.escape(BloqueFinal), texto)]
    HistoriaLaboral = []

    # Extract information between blocks
    for start, end in zip(Inicio, Final):
        substring = texto[start + len(BloqueInicio):end].strip()
        output = [line.strip() for line in substring.splitlines() if len(line.strip()) > 1]
        HistoriaLaboral.append(output)

    # Initialize an empty DataFrame for the final table
    target_strings = {'ALTA', 'REINGRESO', 'MODIFICACION', 'BAJA'}
    Movimiento = list()
    FechaMovimiento = list()
    Sueldo = list()
    Empleador = list()
    EntidadFederativa = list()
    for entry in HistoriaLaboral:
        for line in entry:
            # if any(string in line for string in target_strings):
            if any(string in line.split()[0] for string in target_strings):
                Empleador.append(entry[0])
                EntidadFederativa.append(entry[2].split()[2:])
                array = line.split()
                if array[0] == 'MODIFICACION':
                    Movimiento.append('MODIFICACION DE SALARIO')
                else:
                    Movimiento.append(array[0])
                FechaMovimiento.append(array[-3])
                Sueldo.append(array[-1])

    # Convert 'Sueldo' elements to float before formatting
    Sueldo_str = [convert_double_currency(float(valor)) for valor in Sueldo]
    HistoriaLaboralTable_str = pd.DataFrame({
        'Movimiento': Movimiento,
        # We will apply the format_spanish_date function to the list FechaMovimiento
        'Fecha de Movimiento': FechaMovimiento,
        'Sueldo': Sueldo_str,
        'Empleador': Empleador,
        'Entidad Federativa': EntidadFederativa
    })

    HistoriaLaboralTable_str['Entidad Federativa'] = HistoriaLaboralTable_str['Entidad Federativa'].apply(lambda x: " ".join(x))

    HistoriaLaboralTable_num = HistoriaLaboralTable_str.copy()

    HistoriaLaboralTable_str['Fecha de Movimiento'] = [format_spanish_date(date) for date in FechaMovimiento]
    HistoriaLaboralTable_num['Sueldo'] = Sueldo
    return HistoriaLaboralTable_str, HistoriaLaboralTable_num

HistoriaLaboralTable_str, HistorialLaboralTable_num = HistorialLaboralTabla_fcn(texto)

def HistorialLaboralDesglosada_fcn(HistoriaLaboralTable, texto, sigueCotizando, FechasUltimaBaja):
    Bajas = np.where(HistoriaLaboralTable['Movimiento'] == 'BAJA')[0]
    FechaFinal = HistoriaLaboralTable['Fecha de Movimiento'].values
    # We will apply the convertir_a_fecha function to the list FechaFinal
    FechaFinal = [convertir_a_fecha(fecha) for fecha in FechaFinal]

    for idx in range(len(HistoriaLaboralTable)):
        # print(FechaFinal[idx], type(FechaFinal[idx]))
        if idx not in Bajas:
            FechaFinal[idx] =  FechaFinal[idx] - timedelta(days=1)

    FechaFinal = np.roll(FechaFinal, 1)
    if sigueCotizando:
        FechaFinal[0] = FechasUltimaBaja
#
    HistoriaLaboralDesglosada = HistoriaLaboralTable.copy()
    HistoriaLaboralDesglosada['Fecha Final'] = FechaFinal
    HistoriaLaboralDesglosada.drop(Bajas, inplace=True)
    HistoriaLaboralDesglosada = HistoriaLaboralDesglosada.rename(columns={"Fecha de Movimiento": "Fecha Inicial"})

    HistoriaLaboralDesglosada["Fecha Inicial"] = [convertir_a_fecha(fecha) for fecha in HistoriaLaboralDesglosada["Fecha Inicial"]]
#
    HistoriaLaboralDesglosada["Fecha Inicial"] = HistoriaLaboralDesglosada["Fecha Inicial"] + timedelta(days = 1)

#     # Move the column "FechaFinal" to be after "FechaInicial"
    cols = list(HistoriaLaboralDesglosada.columns)
    cols.insert(cols.index("Fecha Inicial") + 1, cols.pop(cols.index("Fecha Final")))
    HistoriaLaboralDesglosada = HistoriaLaboralDesglosada[cols]

    HistoriaLaboralDesglosada_str = HistoriaLaboralDesglosada.copy()
    HistoriaLaboralDesglosada_str['Fecha Inicial'] = [format_spanish_date(str(date)) for date in
                                                      HistoriaLaboralDesglosada_str['Fecha Inicial']]
    HistoriaLaboralDesglosada_str['Fecha Final'] = [format_spanish_date(str(date)) for date in
                                                    HistoriaLaboralDesglosada_str['Fecha Final']]
    HistoriaLaboralDesglosada_str['Sueldo'] = [convert_double_currency(float(valor)) for valor in
                                               HistoriaLaboralDesglosada_str['Sueldo']]

    return HistoriaLaboralDesglosada, HistoriaLaboralDesglosada_str

fechas_generales = FechasGenerales(texto=texto, FechaEmisionReporte=Usuario.fecha_emision_reporte)
fechasGeneralesNumerico, fechasGeneralesDate, sigueCotizando, fechasUltimaBaja = fechas_generales.tabla_fechas_generales()

HistoriaLaboralTable, HistorialLaboralTable_str = HistorialLaboralDesglosada_fcn(HistorialLaboralTable_num, texto, sigueCotizando, fechasUltimaBaja)
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
            st.metric("Año de Inscripción al IMSS", Usuario.AnoInicio)
            if sigueCotizando:
                st.metric("Sigue Cotizando", "Si")
            else:
                st.metric("Sigue Cotizando", "No")


        with col2:
            st.metric("NSS", Usuario.nss)
            st.metric("Régimen", Usuario.Regimen)
            st.metric("Fecha de Emision del Reporte", Usuario.fecha_emision_reporte, )
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
            st.dataframe(HistoriaLaboralTable_str)
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
        # tabla_salarios = salario_promedio_250tabla(HistoriaLaboralTable, num_semanas=semanas_seleccionadas)
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
