from difflib import ndiff


def get_only_added_parts(old_text, new_text):
    """
    Extracts only the added parts from a diff string.

    Args:
        old_text (str): The old text.
        new_text (str): The new text.

    Returns:
        list: A list of strings representing the added parts.

    Example:
    old_text = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxESTOES"
    new_text = "yESTOESUNA PRUEBA"
    return ["y", "UNA PRUEBA"]
    """
    diff = ndiff(old_text, new_text)
    added = []
    current_addition = []
    
    for x in diff:
        if x.startswith('+ '):
            current_addition.append(x[2:])
        elif current_addition:
            added.append(''.join(current_addition))
            current_addition = []
    
    if current_addition:
        added.append(''.join(current_addition))
    
    return added
