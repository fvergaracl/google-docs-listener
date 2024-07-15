def get_only_added_lines(diff):
    """
    Extracts only the added lines from a diff string.

    Args:
        diff (str): The diff string to process.

    Returns:
        list: A list of strings representing the added lines.
    """
    return [line[2:] for line in diff if line.startswith('+ ')]
