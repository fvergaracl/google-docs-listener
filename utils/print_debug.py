from colorama import Fore, Style

def print_debug(message, level="info", is_json=False):
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
