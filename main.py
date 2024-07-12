from get_refresh_token import get_refresh_token
from listener import listen_for_changes
from colorama import init

init(autoreset=True)

if __name__ == "__main__":
    get_refresh_token()
    listen_for_changes()
