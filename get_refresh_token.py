import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow


def get_refresh_token():
    client_config = {
        "installed": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": ["http://localhost"],
        }
    }

    # Crear flujo de OAuth2
    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=[
            "https://www.googleapis.com/auth/documents.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/script.external_request",
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
        ],
    )
    creds = flow.run_local_server(port=0)

    # Imprimir el refresh token
    print("Refresh Token:", creds.refresh_token)

    # save refresh_token as temporal environment variable
    os.environ["GOOGLE_REFRESH_TOKEN"] = creds.refresh_token

    # Guardar las credenciales en un archivo
    with open("token.json", "w") as token_file:
        json.dump(
            {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
            },
            token_file,
        )
