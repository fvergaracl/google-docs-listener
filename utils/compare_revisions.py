from difflib import ndiff


def compare_revisions(old_content, new_content):
    """
    Compares two versions of document content and returns the differences.

    Args:
        old_content (str): The original document content.
        new_content (str): The new document content.

    Returns:
        str: A string showing the differences between the old and new content.
    """
    diff = ndiff(old_content.splitlines(keepends=True),
                 new_content.splitlines(keepends=True))
    return ''.join(diff)
