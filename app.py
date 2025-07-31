import streamlit as st
import calendar
import warnings
import pdfplumber
import re
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

st.title("Reporte de Semanas Cotizadas")
st.sidebar.title("Parametros Generales del Usuario")
st.sidebar.radio("Salario Asignado", ('1000', '2000'))

# Get the file from Streamlit
uploaded_file = st.file_uploader(label="Sube un PDF",
                                 type=["pdf"])

def file_path_fcn(file_path=None):
    if file_path is None:
        file_path = '/home/carlos-alfonzo/PycharmProjects/streamlitapp/REPORTES/LUPITA.pdf'
    return file_path

# file_path ='/home/carlos-alfonzo/PycharmProjects/streamlitapp/REPORTES/GONZALO.pdf'

file_path = file_path_fcn(file_path=uploaded_file)


def pdf_a_texto(file_path):
    '''Conversion del pdf a texto'''
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

texto = pdf_a_texto(file_path)

@st.cache_resource # cache the function
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
        tiene_vigencia = "vigente" in texto.lower() #Check if tiene_vigencia is contained in the text
        # Initialize an array to store dates
        fecha_bajas = np.zeros(len(bajas), dtype=object)
        # Note: num2cell is not needed in Python, as numpy arrays can store objects

        for idx, baja in enumerate(bajas):
            if idx == 0:
                if not tiene_vigencia:
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
            date = datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
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
        return FechasGenerales, tiene_vigencia, fechas_ultima_baja

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