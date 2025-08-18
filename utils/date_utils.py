from datetime import datetime

def format_spanish_date(my_date, date_type="format_string"):
    days = ["Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"]
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
              "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        # here we will check if date_type is "format_string" or "date"
        if date_type == "format_string":
            try:
                date_obj = datetime.strptime(my_date, fmt)
                break
            except ValueError:
                continue
        elif date_type == "format_date":
            try:
                date_obj = datetime.strptime(my_date, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError("Invalid date_type. It should be 'format_string' or 'date'.")

    day_name = days[date_obj.weekday()]
    month_name = months[date_obj.month - 1]
    day_number = date_obj.day
    year = date_obj.year

    if date_type == "format_string":
        return f"{day_name}, {day_number} de {month_name} de {year}"
    elif date_type == "format_date":
        return date_obj.date()


# Example usage:
date_str = "17/02/1992"
# date_str = '2024-09-19'
# date_str = '1964/10/13'
formatted_date = format_spanish_date(date_str, date_type="format_date")
# formatted_date = format_spanish_date(date_str, date_type="format_string")
print(formatted_date)