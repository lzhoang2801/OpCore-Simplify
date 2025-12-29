from typing import Dict, Callable

from Scripts.value_formatters import format_value, get_value_type


def get_tooltip(key_path, value, original_value = None, context = None):
    context = context or {}
    
    if key_path in TOOLTIP_GENERATORS:
        generator = TOOLTIP_GENERATORS[key_path]
        return generator(key_path, value, original_value, context)
    
    path_parts = key_path.split(".")
    for i in range(len(path_parts), 0, -1):
        parent_path = ".".join(path_parts[:i]) + ".*"
        if parent_path in TOOLTIP_GENERATORS:
            generator = TOOLTIP_GENERATORS[parent_path]
            return generator(key_path, value, original_value, context)
    
    return _default_tooltip(key_path, value, original_value, context)

def _default_tooltip(key_path, value, original_value, context):
    tooltip = f"<b>{key_path}</b><br><br>"
    
    if original_value is not None and original_value != value:
        tooltip += f"<b>Original:</b> {format_value(original_value)}<br>"
        original_type = get_value_type(original_value)
        if original_type:
            tooltip += f"<b>Type:</b> {original_type}<br>"
        tooltip += f"<b>Modified:</b> {format_value(value)}<br>"
        modified_type = get_value_type(value)
        if modified_type:
            tooltip += f"<b>Type:</b> {modified_type}<br>"
        tooltip += "<br>"
    else:
        tooltip += f"<b>Value:</b> {format_value(value)}<br>"
        value_type = get_value_type(value)
        if value_type:
            tooltip += f"<b>Type:</b> {value_type}<br>"
        tooltip += "<br>"
    
    return tooltip

TOOLTIP_GENERATORS: Dict[str, Callable] = {}

def _register_tooltip(path, generator):
    TOOLTIP_GENERATORS[path] = generator