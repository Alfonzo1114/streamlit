def convert_double_currency(value):
    # We will receive a float value and return a string with $ and 2 decimals
    return "${:,.2f}".format(value)

# Example usage:
value = 1234.56
formatted_value = convert_double_currency(value)
print(formatted_value)