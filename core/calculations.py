from datetime import timedelta
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from utils import format_spanish_date, convert_double_currency

def salario_promedio_fcn(semanas_contar, semanas_reconocidas, tabla_salarios):
    if semanas_contar == 0:
        return 0, pd.DataFrame(), pd.DataFrame()
    # Reset the index of salario_promedio_250 to ensure it starts from 0
    tabla_salarios = tabla_salarios.reset_index(drop=True)
    # Convert Fecha Inicial and Fecha Final columns to datetime.date
    tabla_salarios['Fecha Inicial'] = pd.to_datetime(tabla_salarios['Fecha Inicial']).dt.date
    tabla_salarios['Fecha Final'] = pd.to_datetime(tabla_salarios['Fecha Final']).dt.date
    # Initialize necessary variables
    salario_acumulado_periodo = np.zeros(len(tabla_salarios['Fecha Inicial']))
    fecha_superior = tabla_salarios['Fecha Final']
    fecha_inferior = tabla_salarios['Fecha Inicial']
    salario_diario = np.array(tabla_salarios['Sueldo']).astype(float)
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
                        fecha_corte[idx] = min(fecha_corte[idx - 1],
                                             fecha_inferior[idx])  # Use min if previous is not None

                else:
                    fecha_corte[idx] = fecha_superior[idx] - timedelta(
                        weeks=(semanas_contar - semanas_acumuladas[idx - 1]))
            else:
                fecha_corte[idx] = fecha_corte[idx - 1]

            if fecha_corte[idx] > fecha_superior[idx]:
                semanas_cuenta[idx] = 0
            else:
                semanas_cuenta[idx] = (fecha_superior[idx] - max(fecha_corte[idx], fecha_inferior[idx])).days / 7 + 2 / 7

            if semanas_acumuladas[idx - 1] == semanas_contar:
                semanas_acumuladas[idx] = semanas_contar
            else:
                if semanas_acumuladas[idx - 1] + semanas_cuenta[idx] > semanas_contar:
                    semanas_acumuladas[idx] = semanas_contar
                else:
                    if fecha_corte[idx] != fecha_inferior[idx]:
                        semanas_acumuladas[idx] = semanas_acumuladas[idx - 1] + (
                                max(fecha_corte[idx - 1], fecha_superior[idx]) - fecha_corte[idx]).days / 7 + 1 / 7
                    else:
                        semanas_acumuladas[idx] = semanas_acumuladas[idx - 1] + (
                                min(fecha_corte[idx - 1], fecha_superior[idx]) - fecha_corte[idx]).days / 7 + 1 / 7

        salario_acumulado_periodo[idx] = salario_diario[idx] * 7 * semanas_cuenta[idx] if semanas_cuenta[idx] > 0 else 0

    tabla_salario_promedio = pd.DataFrame({
        'Fecha Inicio': fecha_inferior,
        'Fecha Final': fecha_superior,
        # Convert to string with currency format
        'Salario Diario': salario_diario,
        'Semanas totales en el periodo': np.round(semanas_periodo, 1),
        'Fecha de Corte': pd.to_datetime(fecha_corte),
        'Semanas tomadas en cuenta': np.round(semanas_cuenta, 1),
        'Salario Acumulado en el Periodo': salario_acumulado_periodo,
        'Semanas Acumuladas Totales': np.round(semanas_acumuladas, 1)
    })
    tabla_salario_promedio['Fecha de Corte'] = tabla_salario_promedio['Fecha de Corte'].dt.date
    salario_acumulado = np.sum(salario_acumulado_periodo)

    if semanas_reconocidas < semanas_contar:
        salario_promedio_diario = salario_acumulado / (semanas_reconocidas * 7)
    else:
        salario_promedio_diario = salario_acumulado / (semanas_contar * 7)

    tabla_salario_promedio_str = tabla_salario_promedio.copy()
    tabla_salario_promedio_str['Salario Diario'] = [convert_double_currency(value) for value in
                                                    tabla_salario_promedio_str['Salario Diario']]
    tabla_salario_promedio_str['Salario Acumulado en el Periodo'] = [convert_double_currency(value) for value in
                                                                    tabla_salario_promedio_str[
                                                                        'Salario Acumulado en el Periodo']]
    tabla_salario_promedio_str['Fecha Inicio'] = [format_spanish_date(str(date), date_type="format_string") for date in
                                                  tabla_salario_promedio_str['Fecha Inicio']]
    tabla_salario_promedio_str['Fecha Final'] = [format_spanish_date(str(date), date_type="format_string") for date in
                                                 tabla_salario_promedio_str['Fecha Final']]

    return salario_promedio_diario, tabla_salario_promedio, tabla_salario_promedio_str


def salario_promedio_250tabla(HistoriaLaboralDesglosada):
    salario_promedio_250 = HistoriaLaboralDesglosada[["Fecha Inicial", "Fecha Final", "Sueldo"]]
    salario_promedio_250 = salario_promedio_250.sort_values(by=["Fecha Inicial", "Fecha Final"], ascending=[False, False])

    salario_promedio_250_str = salario_promedio_250.copy()
    salario_promedio_250_str['Fecha Inicial'] = [format_spanish_date(str(date), date_type="format_string") for date in
                                                 salario_promedio_250['Fecha Inicial']]
    salario_promedio_250_str['Fecha Final'] = [format_spanish_date(str(date), date_type="format_string") for date in
                                               salario_promedio_250['Fecha Final']]
    salario_promedio_250_str['Sueldo'] = [convert_double_currency(float(valor)) for valor in
                                          salario_promedio_250['Sueldo']]

    return salario_promedio_250, salario_promedio_250_str

def pagos40(salario, start_date, duration):
    tabla_uma = pd.read_csv('TABLAS/TABLA_UMA.txt', sep='\t')
    TABLA_AUMENTO_PAGOMOD40 = pd.read_csv('TABLAS/TABLA_AUMENTOPAGO40.txt', sep='\t')
    TABLA_SALARIOSMINIMOS = pd.read_csv('TABLAS/TABLA_SALARIOSMINIMOS.txt', sep='\t')
    CUOTA_OBRERA = 6.925 / 1e2;

    salario_array = np.full(duration + 1, salario)  # Creates an array with the same value
    second_date = start_date + relativedelta(months=1)
    second_date = second_date.replace(day=1)

    monthly_series = pd.date_range(start=second_date, periods=duration, freq='MS')  # MS: Month Start
    time_series_df = pd.concat([pd.Series(start_date), pd.Series(monthly_series)])
    time_series_df = pd.to_datetime(time_series_df)

    salarios_minimos_array = list()
    salarios_maximos_array = list()
    salario_uma40_array = list()
    DiasCubiertosMensuales_array = list()
    PORCENTAJE_PAGO_array = list()

    def money_to_float(input_str: str, *args):
        for chars in args:
            input_str = input_str.replace(chars, '')
        return float(input_str.strip())

    # Wtih applymap we apply our custom function to each element specified in the iloc
    # indexation, we remove the '%' with the replace function and divide by 1e2
    TABLA_AUMENTO_PAGOMOD40.iloc[:, 1:] = TABLA_AUMENTO_PAGOMOD40.iloc[:, 1:].map(
        lambda x: money_to_float(x, '%') / 1e2)
    TABLA_AUMENTO_PAGOMOD40 = TABLA_AUMENTO_PAGOMOD40.set_index('AÑO')
    salarios_minimos = TABLA_SALARIOSMINIMOS.loc[:, 'SM DIARIO ($)'].map(lambda x: money_to_float(x, '$'))
    salarios_maximos = TABLA_SALARIOSMINIMOS.iloc[:, 6].map(lambda x: money_to_float(x, '$', ','))

    for i in range(duration + 1):
        if time_series_df.iloc[i].month == 1:
            year_considered = time_series_df.iloc[i].year - 1
        else:
            year_considered = time_series_df.iloc[i].year
        # Find the index of rows where the 'AÑO' column equals 'year_considered'

        row = tabla_uma[tabla_uma['AÑO'] == year_considered].index
        row = row.tolist()[0]
        perc_row = tabla_uma.index[tabla_uma['AÑO'] == time_series_df.iloc[i].year].tolist()[0]
        salarios_minimos_array.append(salarios_minimos[tabla_uma['AÑO'] == time_series_df.iloc[i].year].tolist()[0])
        salarios_maximos_array.append(salarios_maximos[tabla_uma['AÑO'] == time_series_df.iloc[i].year].tolist()[0])
        salario_array[i] = min(salarios_maximos_array[i], max(salarios_minimos_array[i], salario_array[i]))

        uma_row = tabla_uma.iloc[perc_row, 1]
        uma_row = uma_row.replace('$', '')
        uma_row = float(uma_row)
        salario_uma40_array.append(round(salario_array[i] / uma_row, 1))

        #Find the last day of the current month
        lastDayOfMonth = time_series_df.iloc[i].replace(day=1) + relativedelta(
            day=31)  # Even if the month does not have 31 days, the relative delta manages
        # Calculate the number of remaining days
        DiasCubiertosMensuales_array.append((lastDayOfMonth - time_series_df.iloc[i]).days + 1)

        if salario_uma40_array[i] >= 4.01:
            CUOTA_PATRONAL = TABLA_AUMENTO_PAGOMOD40.iloc[perc_row, -2]
        elif salario_uma40_array[i] >= 3.51:
            CUOTA_PATRONAL = TABLA_AUMENTO_PAGOMOD40.iloc[perc_row, -3]
        elif salario_uma40_array[i] >= 3:
            CUOTA_PATRONAL = TABLA_AUMENTO_PAGOMOD40.iloc[perc_row, -4]
        elif salario_uma40_array[i] >= 2.51:
            CUOTA_PATRONAL = TABLA_AUMENTO_PAGOMOD40.iloc[perc_row, -5]
        elif salario_uma40_array[i] >= 2:
            CUOTA_PATRONAL = TABLA_AUMENTO_PAGOMOD40.iloc[perc_row, -6]
        elif salario_uma40_array[i] >= 1.51:
            CUOTA_PATRONAL = TABLA_AUMENTO_PAGOMOD40.iloc[perc_row, -7]
        elif salario_uma40_array[i] >= 1:
            CUOTA_PATRONAL = TABLA_AUMENTO_PAGOMOD40.iloc[perc_row, -8]
        else:
            CUOTA_PATRONAL = TABLA_AUMENTO_PAGOMOD40.iloc[perc_row, -9]
        PORCENTAJE_PAGO_array.append(CUOTA_PATRONAL + CUOTA_OBRERA)

    PORCENTAJE_PAGO_array_string = map(lambda x: round(x * 1e2, 2) / 1e2, PORCENTAJE_PAGO_array)
    # Wtih map we apply our custom function to each element specified in the iloc
    # indexation, we remove the '%' with the replace function and divide by 1e2
    time_series_df = time_series_df.map(lambda x: x.strftime('%Y-%m-%d'))
    salario_asignado_mensual = salario_array * DiasCubiertosMensuales_array
    mes_de_pago = time_series_df.map(lambda x: pd.to_datetime(x).month)
    mes_de_pago.replace(
        {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
         9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}, inplace=True)

    # # Pago Mensual
    PAGO_MENSUAL_array = (salario_asignado_mensual * PORCENTAJE_PAGO_array).round(2)
    pago_acumulado = np.cumsum(PAGO_MENSUAL_array)
    tabla_pago40 = pd.DataFrame({'Número de Pago': np.arange(1, duration + 2),
                                 'Fechas de Pago': time_series_df,
                                 'Día de Inicio de Cobertura': time_series_df.map(lambda x: pd.to_datetime(x).day),
                                 'Mes de Pago': mes_de_pago,
                                 'Año de Pago': time_series_df.map(lambda x: pd.to_datetime(x).year),
                                 'Salario Diario Asignado': salario_array,
                                 'Relación Salario/UMA': salario_uma40_array,
                                 'Días cubiertos': DiasCubiertosMensuales_array,
                                 'Salario Asignado Mensual': salario_asignado_mensual,
                                 '% de pago respecto del salario asignado': PORCENTAJE_PAGO_array_string,
                                 'Pago Mensual': PAGO_MENSUAL_array,
                                 'Pago Acumulado': pago_acumulado,
                                 'Salario Mínimo del año en curso': salarios_minimos_array,
                                 'Salario Máximo del año en curso': salarios_maximos_array})

    tabla_pago40.set_index(np.arange(1, duration + 2), inplace=True)
    tabla_pago40_string = tabla_pago40.copy()
    tabla_pago40_string[['Salario Diario Asignado', 'Salario Asignado Mensual', 'Pago Mensual', 'Pago Acumulado',
                         'Salario Mínimo del año en curso', 'Salario Máximo del año en curso']] = tabla_pago40[
        ['Salario Diario Asignado', 'Salario Asignado Mensual', 'Pago Mensual', 'Pago Acumulado',
         'Salario Mínimo del año en curso', 'Salario Máximo del año en curso']].map("${:,.2f}".format)
    tabla_pago40_string['% de pago respecto del salario asignado'] = (
    tabla_pago40['% de pago respecto del salario asignado']).map("{:.2%}".format)
    tabla_pago40_string['Fechas de Pago'] = [format_spanish_date(date, date_type="format_string") for date in tabla_pago40['Fechas de Pago']]

    return tabla_pago40, tabla_pago40_string

class PensionManual:
    def __init__(self, edad_pension, year, semanas_reconocidas, salario_promedio, porcentaje_asignaciones):
        self.edad_pension = edad_pension
        self.year = year
        self.semanas_reconocidas = semanas_reconocidas
        self.salario_promedio = salario_promedio
        self.porcentaje_asignaciones = porcentaje_asignaciones
        self.porcentaje_asignaciones_string = f"{round(porcentaje_asignaciones * 100, 1)}%"
        self.tabla_salarios_minimos = pd.read_csv('TABLAS/TABLA_SALARIOSMINIMOS.txt', sep='\t')
        self.tabla_porcentaje_edad = pd.read_csv('TABLAS/TABLA_PORCENTAJE_EDAD.txt', sep='\t')
        self.tabla_uma = pd.read_csv('TABLAS/TABLA_UMA.txt', sep='\t')
        self.tabla_relacion_umas = pd.read_csv('TABLAS/TABLA_RELACION_UMAS_SALARIO_MINIMO.txt', sep='\t')

    def salario_minimo_garantizado_fcn(self):
            tabla = self.tabla_salarios_minimos
            out = tabla[tabla.iloc[:, 0] == self.year]
            salario_minimo_ano_actual = out.iloc[0, 1]#.strip("$")
            salario_minimo_mensual = out.iloc[0, 4]
            pension_minima_garantizada = out.iloc[0, -1]
            salario_maximo_asignado_diario = out.iloc[0, 6]

            print(f"Los siguientes datos son para el año: {self.year}")

            # We will also create a pandas dataframe
            df = pd.DataFrame({
                # 'Año': year,
                'Salario Minimo Diario': salario_minimo_ano_actual,
                'Salario Minimo Mensual': salario_minimo_mensual,
                'Pension Mínima Garantizada': pension_minima_garantizada,
                'Salario Máximo Asignado Diario': salario_maximo_asignado_diario
            }, index=[self.year])
            self.salario_minimo_ano_actual = salario_minimo_ano_actual
            self.salario_minimo_mensual = salario_minimo_mensual
            self.pension_minima_garantizada = pension_minima_garantizada
            self.salario_maximo_asignado_diario = salario_maximo_asignado_diario

            return salario_minimo_ano_actual, salario_minimo_mensual, pension_minima_garantizada, salario_maximo_asignado_diario, df

    def porcentaje_vejez_fcn(self):
        tabla = self.tabla_porcentaje_edad
        idx = tabla[tabla['EDAD'] == min(self.edad_pension, 65)]['% PENSIÓN'] # Finds the position of the table with the target age
        perc_string = idx.iloc[0] # Obtain the percentage by multiplying by 100%
        porcentaje_vejez =float( perc_string.strip('%')) / 1e2
        self.porcentaje_vejez = porcentaje_vejez
        self.porcentaje_vejez_string = perc_string

    def valor_uma_actual_year_fcn(self):
        tabla = self.tabla_uma
        idx = tabla[tabla['AÑO'] == self.year]['VALOR $'] # Finds the position of the table with the target year
        valor_uma_string = idx.iloc[0]
        valor_uma_numerico =float( valor_uma_string.strip('$'))
        self.valor_uma_numerico = valor_uma_numerico
        self.valor_uma_string = valor_uma_string

    def relacion_uma_salario_fcn(self):
        relacion_salario_uma = round(self.salario_promedio / self.valor_uma_numerico, 2)
        self.relacion_uma_salario = relacion_salario_uma

    def porcentaje_cuantia_fcn(self):
        tabla = self.tabla_relacion_umas
        #subs substracts the variable from all values and then we take only those values inferior, finally we take the pos. of the largest value
        closest_idx = tabla[tabla["Inferior"].sub(self.relacion_uma_salario) < 0]['Inferior'].idxmax()
        out_string = tabla.iloc[closest_idx, 2] # Pos. 2 relates to Porcentaje cuantía básica [%]
        porcentaje_cuantia = float(out_string.strip(('%')))/1e2
        self.porcentaje_cuantia = porcentaje_cuantia
        # self.porcentaje_cuantia_string = out_string

    def semanas_equivalentes_year_fcn(self):
        semanas_despues500 = self.semanas_reconocidas - 500
        upper_bound = 0.5
        lower_bound = 0.25
        if lower_bound < abs(semanas_despues500/52 - np.fix(semanas_despues500/52)) <= upper_bound:
            SEMANAS_EQUIVALENTES = np.fix(semanas_despues500 / 52) + 0.5
        else:
            SEMANAS_EQUIVALENTES = np.round(semanas_despues500/52, decimals=0)
        self.semanas_equivalentes = SEMANAS_EQUIVALENTES

    def salario_incremento_anual_perc_fcn(self):
        tabla = self.tabla_relacion_umas
        closest_idx = (tabla['Porcentaje cuantía básica \r\n[%]'].str.replace('%', '', regex=True)).astype(float)
        closest_idx = closest_idx.sub(self.porcentaje_cuantia*1e2) <= 0
        closest_idx = tabla[closest_idx]['Salario incremento anual [%]'].idxmax()
        salario_incremento_anual_perc = tabla.loc[closest_idx, 'Salario incremento anual [%]']
        salario_incremento_anual_perc = float(salario_incremento_anual_perc.strip('%')) / 1e2
        self.salario_incremento_anual_perc = salario_incremento_anual_perc

    def incremento_perc_fcn(self):
        incremento_perc = round(self.salario_incremento_anual_perc * self.semanas_equivalentes, 4)
        self.incremento_perc = incremento_perc
        self.incremento_perc_string = f'{incremento_perc*1e2:.2f}%'
        return incremento_perc

    def incremento_dinero_fcn(self):
        incremento_dinero = round(self.incremento_perc * self.salario_promedio * 1.11 * 365, 2)
        self.incremento_dinero = incremento_dinero

        # return incremento_dinero

    def cuantia_basica_anual_fcn(self):
        cuantia_basica_anual = round(self.porcentaje_cuantia * self.salario_promedio * 365 * 1.11, 2)
        self.cuantia_basica_anual = cuantia_basica_anual
        # return cuantia_basica_anual

    def cuantia_vejez_fcn(self):
        cuantia_vejez = self.cuantia_basica_anual + self.incremento_dinero
        self.cuantia_vejez = cuantia_vejez

    def pension_cesantia_edad_avanzada_fcn(self):
        pension_cesantia_edad_avanzada = round(self.cuantia_vejez * self.porcentaje_vejez, 2)
        self.pension_cesantia_edad_avanzada = pension_cesantia_edad_avanzada

    def importe_asignaciones_familiares_fcn(self):
        importe_asignaciones_familiares = round(self.porcentaje_asignaciones * self.pension_cesantia_edad_avanzada, 2)
        self.importe_asignaciones_familiares = importe_asignaciones_familiares

    def importe_anual_cesantia_fcn(self):
        importe_anual_cesantia = round(self.importe_asignaciones_familiares + self.pension_cesantia_edad_avanzada, 2)
        self.importe_anual_cesantia = importe_anual_cesantia

    def importe_mensual_calculado_fcn(self):
        importe_mensual_calculado = round(self.importe_anual_cesantia / 12, 1)
        self.importe_mensual_calculado = importe_mensual_calculado

    def pension_minima_garantizada_fcn(self):
        pension_minima_garantizada = self.pension_minima_garantizada.replace('$', '').replace(',', '')
        pension_minima_garantizada = float(pension_minima_garantizada)
        self.pension_minima_garantizada = pension_minima_garantizada

    def pension_final_fcn(self):
        pension_final = round(max(self.importe_mensual_calculado, self.pension_minima_garantizada), 2)
        self.pension_final = pension_final

    def calculo_pension(self):
        self.salario_minimo_garantizado_fcn()
        self.porcentaje_vejez_fcn()
        self.valor_uma_actual_year_fcn()
        self.relacion_uma_salario_fcn()
        self.porcentaje_cuantia_fcn()
        self.semanas_equivalentes_year_fcn()
        self.salario_incremento_anual_perc_fcn()
        self.incremento_perc_fcn()
        self.incremento_dinero_fcn()
        self.cuantia_basica_anual_fcn()
        self.cuantia_vejez_fcn()
        self.pension_cesantia_edad_avanzada_fcn()
        self.importe_asignaciones_familiares_fcn()
        self.importe_anual_cesantia_fcn()
        self.importe_mensual_calculado_fcn()
        self.pension_minima_garantizada_fcn()
        self.pension_final_fcn()

        pension_df = pd.DataFrame({'Pensión Final': [convert_double_currency(self.pension_final)],
                                   'Semanas Reconocidas': [self.semanas_reconocidas],
                                   'Salario Promedio': [convert_double_currency(self.salario_promedio)]
                                   })

        detalles_df = pd.DataFrame({
            'Porcentaje Asignaciones Familiares': [self.porcentaje_asignaciones_string],
            'Porcentaje Vejez': [self.porcentaje_vejez_string],
            'Valor UMA Actual Year': [self.valor_uma_string],
            'Incremento %': [self.incremento_perc_string],
            'Incremento Dinero': [convert_double_currency(self.incremento_dinero)],
            'Cuantia Basica Anual': [convert_double_currency(self.cuantia_basica_anual)],
            'Cuantia Vejez': [self.cuantia_vejez],
            'Pension Cesantia Edad Avanzada': [convert_double_currency(self.pension_cesantia_edad_avanzada)],
            'Importe Asignaciones Familiares': [convert_double_currency(self.importe_asignaciones_familiares)],
            'Importe Anual Cesantia': [convert_double_currency(self.importe_anual_cesantia)],
            'Importe Mensual Calculado': [convert_double_currency(self.importe_mensual_calculado)],
            'Pension Minima Garantizada': [convert_double_currency(self.pension_minima_garantizada)],
            'Pension Final': [convert_double_currency(self.pension_final)]
        })

        detalles_df = round(detalles_df.T, 2)
        # We will rename the column
        detalles_df.columns = ['Valores']

        return pension_df, detalles_df
    
def tabla_salarios_modificada(tabla_salarios_original,fecha_inicio, fecha_final, salario):
    nueva_fila = {'Fecha Inicial': fecha_inicio, 'Fecha Final': fecha_final, 'Sueldo': salario}
    nueva_tabla = pd.concat([tabla_salarios_original, pd.DataFrame([nueva_fila])], ignore_index=True)
    # We will sort by the column "Fecha Inicial"
    nueva_tabla = nueva_tabla.sort_values(by=["Fecha Inicial"], ascending=[False])
    # We will change the date format for the first column
    nueva_tabla['Fecha Inicial'] = pd.to_datetime(nueva_tabla['Fecha Inicial'], format='%d/%m/%Y').dt.date
    # we will change the date format for the second column, from day/month/year to year-month-day
    nueva_tabla['Fecha Final'] = pd.to_datetime(nueva_tabla['Fecha Final'], format='%d/%b/%Y').dt.date

    nueva_tabla_str = nueva_tabla.copy()
    nueva_tabla_str['Fecha Inicial'] = [format_spanish_date(str(date), date_type="format_string") for date in nueva_tabla['Fecha Inicial']]
    nueva_tabla_str['Fecha Final'] = [format_spanish_date(str(date), date_type="format_string") for date in nueva_tabla['Fecha Final']]
    nueva_tabla_str['Sueldo'] = [convert_double_currency(float(valor)) for valor in nueva_tabla['Sueldo']]
    return nueva_tabla, nueva_tabla_str