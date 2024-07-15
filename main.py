"""
Start the application
"""

import os
import json
from get_refresh_token import get_refresh_token
from listener import listen_for_changes
from colorama import init

init(autoreset=True)

if __name__ == "__main__":
    DOCUMENT_ID = os.getenv('GOOGLE_DOCUMENT_ID')
    if DOCUMENT_ID is None:
        raise ValueError(
            'GOOGLE_DOCUMENT_ID is not set in environment variables')
    if os.path.exists('token.json'):
        with open('token.json', 'r', encoding='utf-8') as token_file:
            token = json.load(token_file)
            os.environ['GOOGLE_REFRESH_TOKEN'] = token['refresh_token']
    else:
        get_refresh_token()
    listen_for_changes(document_id=DOCUMENT_ID)
