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

st.title("Datos Generales")

st.sidebar.title("Parametros Generales del Usuario")

sinistra, destra = st.columns(2)
sinistra.button("Cargar ejemplo")
# Get the file from Streamlit
uploaded_file = destra.file_uploader(label="Sube un PDF",
                                label_visibility=("visible" ),
                                accept_multiple_files=False,
                                 type=["pdf"])

@st.cache_resource
def file_path_fcn(file_path=None):
    if file_path is None:
        file_path = 'REPORTES/RICARDO.pdf'
    return file_path

file_path = file_path_fcn(file_path=uploaded_file)

# Convert PDF to base64
if uploaded_file is not None:
    base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')

    # Embed PDF in HTML
    pdf_display = f"""
    <iframe src="data:application/pdf;base64,{base64_pdf}" width="450" height="500" type="application/pdf"></iframe>
    """

    # Display PDF
    st.sidebar.markdown(pdf_display, unsafe_allow_html=True)
@st.cache_resource
def pdf_a_texto(file_path):
    '''Conversion del pdf a texto'''
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

texto = pdf_a_texto(file_path)



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
        return Nombre

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
        return nss

    def curpfcn(self):
        InicioStr = "CURP:"

        Inicio = self.texto.find(InicioStr)

        if Inicio != -1:
            curp = self.texto[Inicio +len(InicioStr): Inicio + 25].strip()
        else:
            curp = ''
        print(f"CURP: {curp}")
        self.curp = curp
        return curp


    def fecha_nacimiento_fcn(self):
        YEAR_BIRTH = "19" + self.curp[4:6]
        MONTH_BIRTH = self.curp[6:8]
        DAY_BIRTH = self.curp[8:10]
        FECHA_NACIMIENTO = DAY_BIRTH + '/' + MONTH_BIRTH + '/' + YEAR_BIRTH
        # Convert string to datetime object
        FECHA_NACIMIENTO = datetime.strptime(FECHA_NACIMIENTO, '%d/%m/%Y').date()
        print(f"FECHA DE NACIMIENTO: {FECHA_NACIMIENTO.strftime('%A %d %b %Y')}")
        self.fecha_nacimiento = FECHA_NACIMIENTO
        return FECHA_NACIMIENTO.strftime('%A %d %b %Y'), FECHA_NACIMIENTO

    def ano_inscripcionIMSS_fcn(self):
        TerminacionYear = self.nss[2:4]
        if int(TerminacionYear) < 50:
            AnoInicio = int('20'+ TerminacionYear)
        else:
            AnoInicio = int('19'+ TerminacionYear)
        print(f"AÑO DE INSCRIPCIÓN IMSS: {AnoInicio}")
        self.AnoInicio = AnoInicio
        return AnoInicio

    def regimen_pertenecefcn(self):
        if self.AnoInicio > 1997:
            Regimen = 'Régimen 97'
        elif self.AnoInicio == 1997:
            Regimen = "Determinar el mes que inició, si es a partir de julio, entra en régimen 97"
        else:
            Regimen = 'Régimen 73'

        print(f"REGIMEN AL QUE PERTENECE: {Regimen}")
        self.Regimen = Regimen
        return Regimen

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

        return semanas_cotizadas, semanas_descontadas, semanas_reintegradas


    def fecha_emision_reporte_fcn(self):
        texto_array = self.texto.split('\n')

        # Find the position of the string that ends with 'reporte' and select the next element that contains the date
        position_date_report = [i + 1 for i, s in enumerate(texto_array) if s.endswith('reporte')]
        out = texto_array[position_date_report[0]]
        out = out.replace(' ', '')
        out = datetime.strptime(out, '%d/%m/%Y').date()
        print(f"FECHA DE EMISIÓN DEL REPORTE: {out}")
        self.fecha_emision_reporte = out
        return out

    def exportar_datos(self, name):
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

        out.to_csv(name)
        return out

    def tabla_datos(self):
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

# Example usage
# @st.cache_resource # cache the function
Usuario = DatosGenerales(texto)
Usuario.nombrefcn()
Usuario.nssfcn()
Usuario.curpfcn()
Usuario.fecha_nacimiento_fcn()
Usuario.ano_inscripcionIMSS_fcn()
Usuario.regimen_pertenecefcn()
Usuario.semanas_cotizadas_descontadas_fcn()
Usuario.fecha_emision_reporte_fcn()

df = Usuario.tabla_datos()
# st.sidebar.table(df)
st.sidebar.dataframe(df, height=300)  # Adjust the height as needed

# Tabla de Fechas Generales
# @st.cache_resource
class FechasGenerales:
    def __init__(self, texto, FechaEmisionReporte):
        self.texto = texto
        self.FechaEmisionReporte = FechaEmisionReporte

    def tabla_fechas_generales(self):
        texto = self.texto
        FechaEmisionReporte = self.FechaEmisionReporte
        # Define the search string
        bajas_string = 'Fecha de baja'
        value_added = 12
        # Find the indices of the search string
        bajas = [m.start() for m in re.finditer(bajas_string, texto)]
        # Get the index of the first occurrence
        ultima_baja = bajas[0]
        # Calculate the end index
        ultima_final = ultima_baja + len(bajas_string) + value_added
        # Extract the desired substring
        sigue_cotizando = "vigente" in texto.lower() #Check if sigue_cotizando is contained in the text
        # Initialize an array to store dates
        fecha_bajas = np.zeros(len(bajas), dtype=object)
        # Note: num2cell is not needed in Python, as numpy arrays can store objects

        for idx, baja in enumerate(bajas):
            if idx == 0:
                if not sigue_cotizando:
                    fechas_ultima_baja = datetime.strptime(texto[ultima_baja + len(bajas_string):ultima_final].strip(), "%d/%m/%Y")
                    fecha_bajas[idx] = fechas_ultima_baja
                else:
                    fecha_bajas[idx] = FechaEmisionReporte
                    fechas_ultima_baja = fecha_bajas[idx]

                if not isinstance(fechas_ultima_baja, date):
                    fechas_ultima_baja = fechas_ultima_baja.date()
            else:
                start_idx = baja + len(bajas_string)
                end_idx = start_idx + value_added  # Assuming 12 characters for the date
                fecha_bajas[idx] = texto[start_idx:end_idx].strip()
                fecha_bajas[idx] = datetime.strptime(fecha_bajas[idx], "%d/%m/%Y")


        altas_string = 'Fecha de alta'
        altas = [m.start() for m in re.finditer(altas_string, texto)]

        ultima_alta = altas[0]
        ultima_alta_final = ultima_alta + len(altas_string) + value_added

        fechas_ultima_alta = texto[ultima_alta + len(altas_string):ultima_alta_final].strip()

        fecha_altas = np.zeros(len(altas), dtype=object)
        dias_transcurridos_cotizados = np.zeros(len(altas), dtype=object)
        semanas_transcurridas_cotizadas = np.zeros(len(altas), dtype=object)

        for idx, alta in enumerate(altas):
            start_idx = alta + len(altas_string)
            end_idx = start_idx + value_added
            fecha_altas[idx] = datetime.strptime(texto[start_idx:end_idx].strip(), "%d/%m/%Y")
            # Convert fecha_bajas[idx] to datetime.datetime if it's a datetime.date
            if isinstance(fecha_bajas[idx], date):
                fecha_bajas[idx] = datetime.combine(fecha_bajas[idx], datetime.min.time())

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

        # Method using vectorize
        def format_date(date_str):
            try:
                # First try with time format
                date = datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    # If that fails, try with just date
                    date = datetime.strptime(str(date_str), '%Y-%m-%d')
                except ValueError:
                    # If both fail, try to parse as datetime object directly
                    if isinstance(date_str, (datetime, date)):
                        date = date_str
                    else:
                        raise ValueError(f"Unsupported date format: {date_str}")
            return date.strftime('%d/%b/%Y')

        vectorized_format = np.vectorize(format_date)
        fecha_altas_str = vectorized_format(fecha_altas)
        fecha_bajas_str = vectorized_format(fecha_bajas)
        fechas_ultima_baja = format_date(fechas_ultima_baja)

        FechasGenerales = pd.DataFrame({
            'Fecha de alta': fecha_altas_str,
            'Fecha de baja': fecha_bajas_str,
            'Dias transcurridos cotizados': dias_transcurridos_cotizados,
            'Semanas transcurridas cotizadas': semanas_transcurridas_cotizadas,
            'Patrones': patrones,
            'Entidad federativa': entidad_federativa
        })
        return FechasGenerales, sigue_cotizando, fechas_ultima_baja

fechas_generales = FechasGenerales(texto=texto, FechaEmisionReporte=Usuario.fecha_emision_reporte)
fechasGenerales, tieneVigencia, fechasUltimaBaja = fechas_generales.tabla_fechas_generales()

st.markdown("## Fechas Generales")
st.dataframe(fechasGenerales, hide_index=True)

if tieneVigencia:
    st.markdown("## Vigencia")
    st.write("Tiene vigenciahasta  el día", fechasUltimaBaja)
else:
    st.markdown("## Vigencia")
    st.write("No tiene vigencia.")

st.markdown("## Fecha de ultima baja")
st.write("La fecha de última baja es:", fechasUltimaBaja)

# Historial Laboral Desglosado
@st.cache_resource
def HistorialLaboralTabla(texto):
    # Define the search string
    BloqueInicio = 'Nombre del patrón'
    BloqueFinal = '* Valor del último salario base de cotización diario en pesos.'
    # tieneVigencia = 0  # Placeholder; define as needed
    # FechasUltimaBaja = datetime(2023, 1, 1)  # Placeholder; replace with actual date if applicable

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
    HistoriaLaboralTable = pd.DataFrame()
    # target_strings = {'ALTA', 'REINGRESO', 'MODIFICACION DE SALARIO', 'BAJA'}
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
    Sueldo_formatted = [float(s) for s in Sueldo]
    HistoriaLaboralTable_str = pd.DataFrame({
        'Movimiento': Movimiento,
        'Fecha de Movimiento': FechaMovimiento,
        'Sueldo': Sueldo, #np.vectorize(lambda x: "${:,.2f}".format(x))(Sueldo_formatted),
        'Empleador': Empleador,
        'Entidad Federativa': EntidadFederativa
    })

    HistoriaLaboralTable_str['Entidad Federativa'] = HistoriaLaboralTable_str['Entidad Federativa'].apply(lambda x: " ".join(x))

    HistoriaLaboralTable_num = HistoriaLaboralTable_str.copy()
    HistoriaLaboralTable_num['Sueldo'] = Sueldo_formatted
    return HistoriaLaboralTable_str, HistoriaLaboralTable_num

HistoriaLaboralTable_str, HistoriaLaboralTable_num = HistorialLaboralTabla(texto)
@st.cache_resource
def HistorialLaboralDesglosada_fcn(texto, tieneVigencia, FechasUltimaBaja):
    # Define the search string
    HistoriaLaboralTable, _ = HistorialLaboralTabla(texto)

    from datetime import timedelta
    Bajas = np.where(HistoriaLaboralTable['Movimiento'] == 'BAJA')[0]
    FechaFinal = HistoriaLaboralTable['Fecha de Movimiento'].values

    for idx in range(len(HistoriaLaboralTable)):
        FechaFinal[idx] = datetime.strptime(FechaFinal[idx], '%d/%m/%Y').date()
        if idx not in Bajas:
            FechaFinal[idx] =  FechaFinal[idx] - timedelta(days=1)


    FechaFinal = np.roll(FechaFinal, 1)

    if tieneVigencia:
        FechaFinal[0] = FechasUltimaBaja

    HistoriaLaboralDesglosada = HistoriaLaboralTable.copy()
    HistoriaLaboralDesglosada['Fecha Final'] = FechaFinal
    HistoriaLaboralDesglosada.drop(Bajas, inplace=True)
    HistoriaLaboralDesglosada = HistoriaLaboralDesglosada.rename(columns={"Fecha de Movimiento": "Fecha Inicial"})

    HistoriaLaboralDesglosada["Fecha Inicial"] = pd.to_datetime(HistoriaLaboralDesglosada["Fecha Inicial"], format='%d/%m/%Y')

    HistoriaLaboralDesglosada["Fecha Inicial"] = HistoriaLaboralDesglosada["Fecha Inicial"] + timedelta(days = 1)
    # Move the column "FechaFinal" to be after "FechaInicial"
    cols = list(HistoriaLaboralDesglosada.columns)
    cols.insert(cols.index("Fecha Inicial") + 1, cols.pop(cols.index("Fecha Final")))
    HistoriaLaboralDesglosada = HistoriaLaboralDesglosada[cols]
    # We will change the date format for the column "Fecha Inicial"
    HistoriaLaboralDesglosada['Fecha Inicial'] = pd.to_datetime(HistoriaLaboralDesglosada['Fecha Inicial'],
                                                                format='%d/%m/%Y').dt.date
    return HistoriaLaboralDesglosada

HistoriaLaboralTable = HistorialLaboralDesglosada_fcn(texto, tieneVigencia, fechasUltimaBaja)
st.markdown('## Historial Laboral Desglosado')
st.write(HistoriaLaboralTable)

# Tabla de salarios
@st.cache_resource
def salario_promedio_250tabla(HistoriaLaboralDesglosada):
    salario_promedio_250 = HistoriaLaboralDesglosada[["Fecha Inicial", "Fecha Final", "Sueldo"]]
    salario_promedio_250 = salario_promedio_250.sort_values(by=["Fecha Inicial", "Fecha Final"], ascending=[False, False])
    # We will change the date format for the first column
    salario_promedio_250['Fecha Inicial'] = pd.to_datetime(salario_promedio_250['Fecha Inicial'], format='%d/%m/%Y').dt.date
    return salario_promedio_250

tabla_salarios = salario_promedio_250tabla(HistoriaLaboralTable)
st.markdown('## Tabla de Salarios')
st.write(tabla_salarios)

# Tabla de Salarios Promedio 250
SEMANAS_CONTAR = st.sidebar.slider(label='Número de semanas a contar', min_value=0, max_value=Usuario.semanas_cotizadas, value=250)
title_str = '## Tabla de Salarios Promedio para el cálculo de las últimas ' + str(SEMANAS_CONTAR) + ' semanas'
st.markdown(title_str)
@st.cache_resource
def salario_promedio_fcn(semanas_contar, semanas_reconocidas, salario_promedio_250):
    if semanas_contar == 0:
        return 0, pd.DataFrame()
  # Reset the index of salario_promedio_250 to ensure it starts from 0
    salario_promedio_250 = salario_promedio_250.reset_index(drop=True)
    # Convert Fecha Inicial and Fecha Final columns to datetime.date
    salario_promedio_250['Fecha Inicial'] = pd.to_datetime(salario_promedio_250['Fecha Inicial']).dt.date
    salario_promedio_250['Fecha Final'] = pd.to_datetime(salario_promedio_250['Fecha Final']).dt.date
    # Initialize necessary variables
    salario_acumulado_periodo = np.zeros(len(salario_promedio_250['Fecha Inicial']))
    fecha_superior = salario_promedio_250['Fecha Final']
    fecha_inferior = salario_promedio_250['Fecha Inicial']
    salario_diario =  np.array(salario_promedio_250['Sueldo']).astype(float)
    # semanas_cotizadas = np.full(len(salario_promedio_250['Fecha Inicial']), semanas_reconocidas)
    semanas_periodo = salario_acumulado_periodo.copy()
    fecha_corte = [None] * len(fecha_superior)
    semanas_acumuladas = salario_acumulado_periodo.copy()
    semanas_cuenta = salario_acumulado_periodo.copy()

    for idx in range(len(fecha_superior)):
        # Calculate weeks in each period
        semanas_periodo[idx] = (fecha_superior[idx] - fecha_inferior[idx]).days / 7 + 1 / 7
        if idx == 0:
            if semanas_periodo[idx] <= semanas_contar:
                fecha_corte[idx] = fecha_inferior[idx]
            else:
                fecha_corte[idx] = fecha_superior[idx] - timedelta(weeks=semanas_contar)

            semanas_cuenta[idx] = (fecha_superior[idx] - fecha_inferior[idx]).days / 7 + 1 / 7
            semanas_acumuladas[idx] = semanas_periodo[idx]
        else:
            semanas_acumuladas[idx] = semanas_periodo[idx]

            if semanas_acumuladas[idx - 1] < semanas_contar:
                if semanas_acumuladas[idx - 1] + semanas_periodo[idx] < semanas_contar:
                    if fecha_corte[idx - 1] is None:  # Check if previous fecha_corte is None
                        fecha_corte[idx] = fecha_inferior[idx]  # Use fecha_inferior if previous is None
                    else:
                        fecha_corte[idx] = min(fecha_corte[idx - 1], fecha_inferior[idx])  # Use min if previous is not None

                else:
                    fecha_corte[idx] = fecha_superior[idx] - timedelta(weeks=(semanas_contar - semanas_acumuladas[idx - 1]))
            else:
                fecha_corte[idx] = fecha_corte[idx - 1]

            if fecha_corte[idx] > fecha_superior[idx]:
                semanas_cuenta[idx] = 0
            else:
                semanas_cuenta[idx] = (fecha_superior[idx] - max(fecha_corte[idx], fecha_inferior[idx])).days / 7 + 1 / 7

            if semanas_acumuladas[idx - 1] == semanas_contar:
                semanas_acumuladas[idx] = semanas_contar
            else:
                if semanas_acumuladas[idx - 1] + semanas_cuenta[idx] > semanas_contar:
                    semanas_acumuladas[idx] = semanas_contar
                else:
                    if fecha_corte[idx] != fecha_inferior[idx]:
                        semanas_acumuladas[idx] = semanas_acumuladas[idx - 1] + (max(fecha_corte[idx - 1], fecha_superior[idx]) - fecha_corte[idx]).days / 7 + 1 / 7
                    else:
                        semanas_acumuladas[idx] = semanas_acumuladas[idx - 1] + (min(fecha_corte[idx - 1], fecha_superior[idx]) - fecha_corte[idx]).days / 7 + 1 / 7

        salario_acumulado_periodo[idx] = salario_diario[idx] * 7 * semanas_cuenta[idx] if semanas_cuenta[idx] > 0 else 0

    tabla_salario_promedio = pd.DataFrame({
        'Fecha Inicio': fecha_inferior,
        'Fecha Final': fecha_superior,
        # Convert to string with currency format
        'Salario Diario': np.vectorize(lambda x: "${:,.2f}".format(x))(salario_diario),
        # 'Semanas Cotizadas': np.round(semanas_cotizadas, 1),
        'Semanas totales en el periodo': np.round(semanas_periodo, 1),
        'Fecha de Corte': pd.to_datetime(fecha_corte),
        'Semanas tomadas en cuenta': np.round(semanas_cuenta, 1),
        'Salario Acumulado en el Periodo': np.vectorize(lambda x: "${:,.2f}".format(x))(np.round(salario_acumulado_periodo)),
        'Semanas Acumuladas Totales': np.round(semanas_acumuladas, 1)
    })
    tabla_salario_promedio['Fecha de Corte'] = tabla_salario_promedio['Fecha de Corte'].dt.date
    salario_acumulado = np.sum(salario_acumulado_periodo)

    if semanas_reconocidas < semanas_contar:
        salario_promedio_diario = salario_acumulado / (semanas_reconocidas * 7)
    else:
        salario_promedio_diario = salario_acumulado / (semanas_contar * 7)

    return salario_promedio_diario, tabla_salario_promedio

SemanasReconocidas = Usuario.semanas_totales
SALARIO_PROMEDIO_DIARIO, TABLA_SALARIO_PROMEDIO = salario_promedio_fcn(SEMANAS_CONTAR, SemanasReconocidas, tabla_salarios)

st.sidebar.markdown('## Salario Promedio Diario')
st.sidebar.metric(label='Salario Promedio Diario',
                  label_visibility='hidden',
                  border = True,
                  value=round(SALARIO_PROMEDIO_DIARIO, 2))
# st.sidebar.write(round(SALARIO_PROMEDIO_DIARIO, 2))

st.markdown('## Tabla de Salarios Promedio')
st.write(TABLA_SALARIO_PROMEDIO)

#%%
@st.cache_data
def fecha_pension_minima(fecha_nacimiento, fechasUltimaBaja):
    if isinstance(fecha_nacimiento, str):
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%b/%d/%Y')
    elif isinstance(fechasUltimaBaja, str):
        fechasUltimaBaja = datetime.strptime(fechasUltimaBaja, '%d/%b/%Y').date()

    # edad_actual = (datetime.today().date() - fecha_nacimiento.date()).days // 365
    edad_actual = round((datetime.today().date() - fecha_nacimiento).days / 365, 2)
    fecha_60 = fecha_nacimiento + relativedelta(years=60)
    print(f"Edad al dia de hoy: {edad_actual}")
    print(f"Fecha en que cumple 60 años: {fecha_60}")
    print(f"FECHA DE ULTIMA BAJA: {fechasUltimaBaja}")
    fecha_pension_minima = max(fecha_60, fechasUltimaBaja)
    return fecha_pension_minima

fecha_pension_minima = fecha_pension_minima(fecha_nacimiento=Usuario.fecha_nacimiento,
                                            fechasUltimaBaja=fechasUltimaBaja)

st.sidebar.markdown('## Selección de Fecha de Pensión')

fecha_pension = st.sidebar.date_input(label='Fecha de Pensión',
                                      value=fecha_pension_minima)