from datetime import datetime, date as _date

def format_spanish_date(date_str):
    days = ["Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"]
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
              "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    if isinstance(date_str, (datetime, _date)):
        date_obj = datetime.combine(date_str, datetime.min.time()) if isinstance(date_str, _date) else date_str
    else:
        s = str(date_str).strip()
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                date_obj = datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Fecha inválida '{date_str}'. Formatos soportados: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, YYYY/MM/DD")

    return f"{days[date_obj.weekday()]}, {date_obj.day} de {months[date_obj.month - 1]} de {date_obj.year}"



def convertir_a_fecha(fecha_str, formato: str | None = None):
    """
    Convert a date string to a date object.

    Args:
        fecha_str (str | datetime.date): Date string to convert (or a date already).
        formato (str | None): Optional explicit format to use. If provided, only that
            format will be tried. If None, multiple common formats are tried in order:
            'DD/MM/YYYY', 'DD-MM-YYYY', 'YYYY-MM-DD', 'YYYY/MM/DD'.

    Returns:
        datetime.date: The converted date object
    """
    if isinstance(fecha_str, _date):
        return fecha_str

    s = str(fecha_str).strip()

    # If caller provided a specific format, try it first and raise if it fails
    if formato:
        return datetime.strptime(s, formato).date()

    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Fecha inválida '{fecha_str}'. Formatos soportados: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, YYYY/MM/DD")
