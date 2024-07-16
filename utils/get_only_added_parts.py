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
    diff = ndiff(old_text.splitlines(keepends=True),
                 new_text.splitlines(keepends=True))
    added_parts = []
    current_part = []
    for line in diff:
        if line.startswith('- '):
            if current_part:
                added_parts.append(''.join(current_part).strip())
                current_part = []
        elif line.startswith('+ '):
            current_part.append(line[2:])
        else:
            if current_part:
                added_parts.append(''.join(current_part).strip())
                current_part = []

    if current_part:
        added_parts.append(''.join(current_part).strip())

    return added_parts
