def format_value(value):
    if value is None:
        return "None"
    elif isinstance(value, bool):
        return "True" if value else "False"
    elif isinstance(value, (bytes, bytearray)):
        return value.hex().upper()
    elif isinstance(value, str):
        return value
    
    return str(value)

def get_value_type(value):
    if value is None:
        return None
    elif isinstance(value, dict):
        return "Dictionary"
    elif isinstance(value, list):
        return "Array"
    elif isinstance(value, (bytes, bytearray)):
        return "Data"
    elif isinstance(value, bool):
        return "Boolean"
    elif isinstance(value, (int, float)):
        return "Number"
    elif isinstance(value, str):
        return "String"
    
    return "String"