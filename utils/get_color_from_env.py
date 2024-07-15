import os


def get_color_from_env(prefix):
    """
    Get the color from the environment variables

    Args:
        prefix (str): The prefix for the environment variables

    Returns:
        dict: The color values
    """
    return {
        "red": float(os.getenv(f"{prefix}_RED")),
        "green": float(os.getenv(f"{prefix}_GREEN")),
        "blue": float(os.getenv(f"{prefix}_BLUE"))
    }
