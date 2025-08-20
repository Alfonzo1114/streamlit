import re
import streamlit as st
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pdfplumber

from utils import format_spanish_date, convert_double_currency

def pdf_a_texto(file_path):
    '''Convert PDF to text'''
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text


class DatosGenerales:
    """Extracts general data of the user from the text."""

    def __init__(self, texto):
        self.texto = texto

    def nombrefcn(self):
        # Extract the substring between the found positions, adjust indices for correct slicing
        try:
            InicioStr = re.search(r"20\d{2}\s{1}", self.texto)
            FinalStr = "DD MM YYYY"
            # Find the starting and ending positions of the target substrings
            Inicio = InicioStr.span()[0]
            Final = self.texto.find(FinalStr)
            # Extract the substring between the found positions, adjust indices for correct slicing
            if Inicio != -1 and Final != -1:
                # + 5 since InicioStr length = length(20) + 2 + 1 = 5
                Nombre = self.texto[Inicio + 5: Final].strip()
            else:
                Nombre = ""
        except AttributeError:
            Nombre = ""
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
        self.nss = nss

    def curpfcn(self):
        InicioStr = "CURP:"

        Inicio = self.texto.find(InicioStr)

        if Inicio != -1:
            curp = self.texto[Inicio + len(InicioStr): Inicio + 25].strip()
        else:
            curp = ''
        self.curp = curp

    def fecha_nacimiento_fcn(self):
        YEAR_BIRTH = "19" + self.curp[4:6]
        MONTH_BIRTH = self.curp[6:8]
        DAY_BIRTH = self.curp[8:10]
        FECHA_NACIMIENTO = DAY_BIRTH + '/' + MONTH_BIRTH + '/' + YEAR_BIRTH
        # Convert string to datetime object
        FECHA_NACIMIENTO_date = format_spanish_date(FECHA_NACIMIENTO, date_type="format_date")
        # Convert string to spanish date string
        FECHA_NACIMIENTO_string = format_spanish_date(FECHA_NACIMIENTO, date_type="format_string")
        self.fecha_nacimiento_string = FECHA_NACIMIENTO_string
        self.fecha_nacimiento_date = FECHA_NACIMIENTO_date

    def ano_inscripcionIMSS_fcn(self):
        TerminacionYear = self.nss[2:4]
        if int(TerminacionYear) < 50:
            AnoInicio = int('20' + TerminacionYear)
        else:
            AnoInicio = int('19' + TerminacionYear)
        self.AnoInicio = AnoInicio

    def regimen_pertenecefcn(self):
        if self.AnoInicio > 1997:
            Regimen = 'Régimen 97'
        elif self.AnoInicio == 1997:
            Regimen = "Determinar el mes que inició, si es a partir de julio, entra en régimen 97"
        else:
            Regimen = 'Régimen 73'

        self.Regimen = Regimen

    def semanas_cotizadas_descontadas_fcn(self):
        try:
            Iniciostr = re.search(r"\d{1,4}\s{1}\d{1,4}\s{1}\d{1,4}", self.texto)
            myrange = Iniciostr.span()
            risultati = self.texto[myrange[0]:myrange[1]]
            semanas_cotizadas = int(risultati.split()[0])
            semanas_descontadas = int(risultati.split()[1])
            semanas_reintegradas = int(risultati.split()[-1])
            semanas_totales = semanas_cotizadas - semanas_descontadas + semanas_reintegradas
        except AttributeError:
            semanas_cotizadas = 0
            semanas_descontadas = 0
            semanas_reintegradas = 0
            semanas_totales = 0

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
        self.fecha_emision_reporte_date = format_spanish_date(out, date_type="format_date")
        self.fecha_emision_reporte_string = format_spanish_date(out, date_type="format_string")

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
            'FECHA DE NACIMIENTO': [self.fecha_nacimiento_string],
            'AÑO DE INSCRIPCIÓN IMSS': [self.AnoInicio],
            'REGIMEN AL QUE PERTENECE': [self.Regimen],
            'SEMANAS COTIZADAS': [self.semanas_cotizadas],
            'SEMANAS DESCONTADAS': [self.semanas_descontadas],
            'SEMANAS REINTEGRADAS': [self.semanas_reintegradas],
            'SEMANAS TOTALES': [self.semanas_totales],
            'FECHA DE EMISIÓN DEL REPORTE': [self.fecha_emision_reporte_string]
        }
        )
        out = out.T
        out.columns = ['DATOS PERSONALES']
        return out


class FechasGenerales:
    def __init__(self, texto, FechaEmisionReporte):
        self.texto = texto
        self.FechaEmisionReporte = FechaEmisionReporte

    def tabla_fechas_generales(self):
        texto = self.texto
        FechaEmisionReporte = self.FechaEmisionReporte
        # Define the search string
        bajas_string = 'Fecha de baja'
        value_added = 12  # Assuming 12 characters for the date
        # Find the indices of the search string
        bajas = [m.start() for m in re.finditer(bajas_string, texto)]
        # Get the index of the first occurrence
        ultima_baja = bajas[0]
        # Calculate the end index
        ultima_final = ultima_baja + len(bajas_string) + value_added
        # Extract the desired substring
        sigue_cotizando = "vigente" in texto.lower()  # Check if sigue_cotizando is contained in the text
        # Initialize an array to store dates
        fecha_bajas = np.zeros(len(bajas), dtype=object)
        fecha_bajas_string = np.zeros(len(bajas), dtype=object)

        for idx, baja in enumerate(bajas):
            if idx == 0:
                if not sigue_cotizando:
                    fecha_unstructured = texto[ultima_baja + len(bajas_string):ultima_final].strip()
                    fechas_ultima_baja = format_spanish_date(fecha_unstructured, date_type="format_date")
                    fecha_bajas[idx] = fechas_ultima_baja
                    fecha_bajas_string[idx] = format_spanish_date(fecha_unstructured, date_type="format_string")
                else:
                    fecha_bajas[idx] = FechaEmisionReporte
                    fecha_bajas_string[idx] = format_spanish_date(str(fecha_bajas[idx]), date_type="format_string")
                    fechas_ultima_baja = fecha_bajas[idx]

                if not isinstance(fechas_ultima_baja, date):
                    fechas_ultima_baja = fechas_ultima_baja.date()
            else:
                start_idx = baja + len(bajas_string)
                end_idx = start_idx + value_added  # Assuming 12 characters for the date
                fecha = texto[start_idx:end_idx].strip()
                fecha_bajas[idx] = format_spanish_date(fecha, date_type="format_date")
                fecha_bajas_string[idx] = format_spanish_date(fecha, date_type="format_string")

        altas_string = 'Fecha de alta'
        altas = [m.start() for m in re.finditer(altas_string, texto)]

        fecha_altas = np.zeros(len(altas), dtype=object)
        fecha_altas_string = np.zeros(len(altas), dtype=object)
        dias_transcurridos_cotizados = np.zeros(len(altas), dtype=object)
        semanas_transcurridas_cotizadas = np.zeros(len(altas), dtype=object)

        for idx, alta in enumerate(altas):
            start_idx = alta + len(altas_string)
            end_idx = start_idx + value_added

            fecha = texto[start_idx:end_idx].strip()
            fecha_altas[idx] = format_spanish_date(fecha, date_type="format_date")
            fecha_altas_string[idx] = format_spanish_date(fecha, date_type="format_string")

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
            FechasGenerales_string = pd.DataFrame({
                'Fecha de alta': fecha_altas_string,
                'Fecha de baja': fecha_bajas_string,
                'Dias transcurridos cotizados': dias_transcurridos_cotizados,
                'Semanas transcurridas cotizadas': semanas_transcurridas_cotizadas,
                'Patrones': patrones,
                'Entidad federativa': entidad_federativa
            })
        return FechasGenerales_num, FechasGenerales_string, sigue_cotizando, fechas_ultima_baja


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
        'Fecha de Movimiento': FechaMovimiento,
        'Sueldo': Sueldo_str,
        'Empleador': Empleador,
        'Entidad Federativa': EntidadFederativa
    })

    HistoriaLaboralTable_str['Entidad Federativa'] = HistoriaLaboralTable_str['Entidad Federativa'].apply(
        lambda x: " ".join(x))

    HistoriaLaboralTable_num = HistoriaLaboralTable_str.copy()

    HistoriaLaboralTable_str['Fecha de Movimiento'] = [format_spanish_date(date, date_type="format_string") for date in
                                                      FechaMovimiento]
    HistoriaLaboralTable_num['Sueldo'] = Sueldo
    return HistoriaLaboralTable_str, HistoriaLaboralTable_num


def HistorialLaboralDesglosada_fcn(HistoriaLaboralTable, sigueCotizando, FechasUltimaBaja):
    Bajas = np.where(HistoriaLaboralTable['Movimiento'] == 'BAJA')[0]
    FechaFinal = HistoriaLaboralTable['Fecha de Movimiento'].values
    # We will apply the convertir_a_fecha function to the list FechaFinal
    FechaFinal = [format_spanish_date(fecha, date_type="format_date") for fecha in FechaFinal]

    for idx in range(len(HistoriaLaboralTable)):
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

    HistoriaLaboralDesglosada["Fecha Inicial"] = [format_spanish_date(fecha, date_type="format_date") for fecha in HistoriaLaboralDesglosada["Fecha Inicial"]]
    HistoriaLaboralDesglosada["Fecha Inicial"] = HistoriaLaboralDesglosada["Fecha Inicial"] + timedelta(days = 1)

#     # Move the column "FechaFinal" to be after "FechaInicial"
    cols = list(HistoriaLaboralDesglosada.columns)
    cols.insert(cols.index("Fecha Inicial") + 1, cols.pop(cols.index("Fecha Final")))
    HistoriaLaboralDesglosada = HistoriaLaboralDesglosada[cols]

    HistoriaLaboralDesglosada_str = HistoriaLaboralDesglosada.copy()
    HistoriaLaboralDesglosada_str['Fecha Inicial'] = [format_spanish_date(str(date), date_type="format_string") for date in HistoriaLaboralDesglosada['Fecha Inicial']]
    HistoriaLaboralDesglosada_str['Fecha Final'] = [format_spanish_date(str(date), date_type="format_string") for date in HistoriaLaboralDesglosada['Fecha Final']]
    HistoriaLaboralDesglosada_str['Sueldo'] = [convert_double_currency(float(valor)) for valor in HistoriaLaboralDesglosada['Sueldo']]

    return HistoriaLaboralDesglosada, HistoriaLaboralDesglosada_str

class SessionVars:
    """A class to manage session variables in Streamlit."""
    def __init__(self):
        """Initialize the session variables dictionary."""
        if "session_vars" not in st.session_state:
            st.session_state.session_vars = {}

    def set(self, key, value):
        """Set a session variable."""
        st.session_state.session_vars[key] = value

    def get(self, key, default=None):
        """Get a session variable."""
        return st.session_state.session_vars.get(key, default)

    def get_all(self):
        """Get all session variables."""
        return st.session_state.session_vars

    def clear(self):
        """Clear all session variables."""
        st.session_state.session_vars = {}

    def update(self, new_vars):
        """Update multiple session variables at once."""
        st.session_state.session_vars.update(new_vars)
