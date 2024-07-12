import os
import time
from utils.print_debug import print_debug
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from get_refresh_token import get_refresh_token
from dotenv import load_dotenv
from difflib import ndiff
from contribution_evaluation import evaluate_contributions  # Import the function
load_dotenv()

# Cargar variables de entorno


def get_credentials(attempts=1):
    if attempts >= 3:
        message = (
            f"Se ha excedido el número máximo de intentos para obtener "
            f"credenciales."
        )
        print_debug(message, level="error")
        return None
    try:
        CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
        REFRESH_TOKEN = os.getenv('GOOGLE_REFRESH_TOKEN')
        creds_data = {
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "token_uri": "https://oauth2.googleapis.com/token",
            "scopes": ["https://www.googleapis.com/auth/documents.readonly",
                       "https://www.googleapis.com/auth/drive.readonly",
                       "https://www.googleapis.com/auth/script.external_request",
                       "https://www.googleapis.com/auth/documents",
                       "https://www.googleapis.com/auth/drive",
                       "https://www.googleapis.com/auth/drive.metadata.readonly"]
        }
        return Credentials.from_authorized_user_info(info=creds_data)
    except Exception as e:
        print_debug(f"Ha ocurrido un error: {e}", level="error")
        get_refresh_token()
        get_credentials(attempts + 1)


def get_document_content(docs_service, document_id):
    document = docs_service.documents().get(documentId=document_id).execute()
    content = ''
    for element in document.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for elem in element['paragraph'].get('elements', []):
                if 'textRun' in elem:
                    content += elem['textRun']['content']
    return content


def print_revision_info(revision_info):
    print(f"ID de revisión: {revision_info['id']}")
    print(
        f"Modificado por: {revision_info['lastModifyingUser'].get('displayName', 'Desconocido')}")
    print(f"Fecha de modificación: {revision_info['modifiedTime']}")
    print(f"Links de exportación: {revision_info.get('exportLinks', {})}")
    print(f"Publicado: {revision_info.get('published', False)}")


def compare_revisions(old_content, new_content):
    diff = ndiff(old_content.splitlines(keepends=True),
                 new_content.splitlines(keepends=True))
    return ''.join(diff)


def apply_markdown(text_run):
    content = text_run.get("content", "")
    text_style = text_run.get("textStyle", {})

    if text_style.get("bold"):
        content = f"**{content.strip()}**"
    if text_style.get("underline"):
        content = f"_{content.strip()}_"
    if text_style.get("italic"):
        content = f"*{content.strip()}*"

    return content


def escape_markdown_special_chars(content):
    return content.replace('*', '\\*').replace('_', '\\_')


def extract_topics_and_answers(document):
    topics_and_answers = []
    current_topic = None

    # Iterar a través del contenido del cuerpo del documento
    for item in document.get("body", {}).get("content", []):
        paragraph = item.get("paragraph", {})
        paragraph_style = paragraph.get("paragraphStyle", {})
        named_style_type = paragraph_style.get("namedStyleType", "")

        # Verificar si el estilo del párrafo es "HEADING_3"
        if named_style_type == "HEADING_3":
            for element in paragraph.get("elements", []):
                text_run = element.get("textRun", {})
                content = text_run.get("content", "")
                text_style = text_run.get("textStyle", {})
                background_color = text_style.get("backgroundColor", {}).get(
                    "color", {}).get("rgbColor", {})

                # Verificar si el color de fondo coincide con las condiciones dadas para "topic"
                if background_color.get("red") == .05882353 and background_color.get("green") == 1 and background_color.get("blue") == .05882353:
                    if current_topic:
                        topics_and_answers.append(current_topic)
                    current_topic = {
                        "topic": content.strip(), "description": "", "answer": ""}

        # Agregar contenido a la respuesta o descripción del último topic si cumple las condiciones
        elif current_topic:
            for element in paragraph.get("elements", []):
                text_run = element.get("textRun", {})
                content = text_run.get("content", "")
                text_style = text_run.get("textStyle", {})
                background_color = text_style.get("backgroundColor", {}).get(
                    "color", {}).get("rgbColor", {})

                # Verificar si el color de fondo coincide con las condiciones dadas para "description"
                if content and background_color.get("red") == .3019608 and background_color.get("green") == .9137255 and background_color.get("blue") == .9411765:
                    # Escapar caracteres especiales de Markdown
                    content = escape_markdown_special_chars(content.strip())

                    # Aplicar formato Markdown si es necesario
                    if text_style.get("bold"):
                        content = f"**{content}**"
                    if text_style.get("underline"):
                        content = f"_{content}_"
                    if text_style.get("italic"):
                        content = f"*{content}*"

                    current_topic["description"] += content + " "

                # Verificar si el color de fondo coincide con las condiciones dadas para "answer"
                elif content and background_color.get("red") == 1 and background_color.get("green") == 1 and background_color.get("blue") == .47058824:
                    # Escapar caracteres especiales de Markdown
                    content = escape_markdown_special_chars(content.strip())

                    # Aplicar formato Markdown si es necesario
                    if text_style.get("bold"):
                        content = f"**{content}**"
                    if text_style.get("underline"):
                        content = f"_{content}_"
                    if text_style.get("italic"):
                        content = f"*{content}*"

                    current_topic["answer"] += content + " "

    # Añadir el último tópico al resultado
    if current_topic:
        topics_and_answers.append(current_topic)

    # Limpiar espacios extras al final de cada respuesta y descripción
    for item in topics_and_answers:
        item["description"] = item["description"].strip()
        item["answer"] = item["answer"].strip()

    return topics_and_answers


def listen_for_changes(document_id=os.getenv('GOOGLE_DOCUMENT_ID')):
    # save DOCUMENT_ID as global variable
    global DOCUMENT_ID
    DOCUMENT_ID = document_id

    creds = get_credentials()
    if not creds:
        exit(1)
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    try:
        last_revision = None
        last_content = ''

        while True:
            document = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
            revisions = drive_service.revisions().list(fileId=DOCUMENT_ID).execute()
            latest_revision = revisions['revisions'][-1]['id']
            print_debug(f"Última revisión: {latest_revision}", level=None)
            print_debug(" ", level=None)
            tasks_and_responses = extract_topics_and_answers(document)
            print_debug(tasks_and_responses, level=None, is_json=True)

            if last_revision is None:
                last_revision = latest_revision
                last_content = get_document_content(docs_service, DOCUMENT_ID)

            if last_revision != latest_revision:
                print(
                    f"Nuevo cambio detectado en el documento. ID de revisión: {latest_revision}")
                try:
                    revision_info = drive_service.revisions().get(
                        fileId=DOCUMENT_ID, revisionId=latest_revision, fields='*').execute()
                    print_revision_info(revision_info)
                except HttpError as error:
                    if error.resp.status == 404:
                        print(f"Revisión no encontrada: {latest_revision}")
                        continue
                    else:
                        raise

                new_content = get_document_content(docs_service, DOCUMENT_ID)
                delta = compare_revisions(last_content, new_content)

                print("Cambios realizados:")
                print(delta)

                # Evaluar la contribución delta
                task_description = """Create a detailed action plan for the prevention, detection, and mitigation of fires in a specific region.
                The plan should include preventive measures, detection systems, mitigation strategies, resource identification, and risk assessment."""
                contributions = [delta]
                evaluation_results = evaluate_contributions(
                    task_description, contributions)
                print(
                    f"Evaluación de la contribución: {evaluation_results[0][1]:.2f}")

                last_revision = latest_revision
                last_content = new_content

            time.sleep(10)

    except HttpError as error:
        print(f"Ha ocurrido un error: {error}")


if __name__ == "__main__":
    listen_for_changes()
