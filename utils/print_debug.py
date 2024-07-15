from colorama import Fore
import json


def print_debug(message, level="info", is_json=False):
    """
    Print a message with a specific level

    Args:
        message (str): The message to print.
        level (str): The level of the message. Default is "info".
        is_json (bool): If True, the message will be pretty printed as JSON. Default is False.

    Returns:
        None

    """
    if is_json:
        message = json.dumps(message, indent=4, ensure_ascii=False)

    if level == "info":
        print(f"{Fore.BLUE}[INFO] {message}")
    elif level == "success":
        print(f"{Fore.GREEN}[+] {message}")
    elif level == "warning":
        print(f"{Fore.YELLOW}[!] {message}")
    elif level == "error":
        print(f"{Fore.RED}[-] {message}")
    else:
        print(message)
