def convert_double_currency(value):
    # We will receive a float value and return a string with $ and 2 decimals
    return "${:,.2f}".format(value)

def convert_string_currency(value):
    # We will receive a string value and return a float value
    return float(value.replace("$", "").replace(",", ""))