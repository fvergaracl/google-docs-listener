import os
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from get_refresh_token import get_refresh_token
from dotenv import load_dotenv
from contribution_evaluation import evaluate_contributions
from utils import (print_debug, get_color_from_env,
                   compare_revisions, get_only_added_parts)

load_dotenv()

# Cargar variables de entorno


def get_credentials(attempts=1):
    """
    Retrieves OAuth2 credentials for Google APIs. Tries a specified number of
      attempts before failing.

    Args:
        attempts (int): Number of attempts to obtain credentials.

    Returns:
        Credentials: OAuth2 credentials object if successful, None otherwise.
    """
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
    """
    Fetches the content of a Google Docs document.

    Args:
        docs_service (Resource): Google Docs API service instance.
        document_id (str): The ID of the document to fetch content from.

    Returns:
        str: The plain text content of the document.
    """
    document = docs_service.documents().get(documentId=document_id).execute()
    content = ''
    for element in document.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for elem in element['paragraph'].get('elements', []):
                if 'textRun' in elem:
                    content += elem['textRun']['content']
    return content


def print_revision_info(revision_info):
    """
    Prints detailed information about a specific document revision.

    Args:
        revision_info (dict): Dictionary containing revision information.
    """
    print_debug(f"ID de revisión: {revision_info['id']}")
    modified_msg = (
        f"Modificado por: {revision_info['lastModifyingUser'].get('displayName', 'Desconocido')}"  # noqa
    )

    print_debug(modified_msg)
    print_debug(f"Fecha de modificación: {revision_info['modifiedTime']}")
    print_debug(
        f"Links de exportación: {revision_info.get('exportLinks', {})}")
    print_debug(f"Publicado: {revision_info.get('published', False)}")


def apply_markdown(text_run):
    """
    Applies Markdown formatting based on the text style attributes of a text
      run.

    Args:
        text_run (dict): The text run dictionary containing content and style.

    Returns:
        str: The formatted text content.
    """
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
    """
    Escapes special characters used in Markdown formatting.

    Args:
        content (str): The text content to escape.

    Returns:
        str: The escaped text content.
    """
    return content.replace('*', '\\*').replace('_', '\\_')


def extract_topics_and_answers(document):
    """
    Extracts topics and corresponding answers from a Google Docs document.

    Args:
        document (dict): The document data as retrieved from the Google Docs
          API.

    Returns:
        list: A list of dictionaries, each containing a topic, description,
          and answer.
    """
    topics_and_answers = []
    current_topic = None
    TOPIC_COLOR = get_color_from_env("TOPIC_COLOR")
    DESCRIPTION_COLOR = get_color_from_env("DESCRIPTION_COLOR")
    ANSWER_COLOR = get_color_from_env("ANSWER_COLOR")

    topics_and_answers = []
    current_topic = None

    # Iterate through the document body content
    for item in document.get("body", {}).get("content", []):
        paragraph = item.get("paragraph", {})
        paragraph_style = paragraph.get("paragraphStyle", {})
        named_style_type = paragraph_style.get("namedStyleType", "")

        # Check if the paragraph style is "HEADING_3"
        if named_style_type == "HEADING_3":
            for element in paragraph.get("elements", []):
                text_run = element.get("textRun", {})
                content = text_run.get("content", "")
                text_style = text_run.get("textStyle", {})
                background_color = text_style.get("backgroundColor", {}).get(
                    "color", {}).get("rgbColor", {})

                # Check if the background color matches the topic color
                if background_color == TOPIC_COLOR:
                    if current_topic:
                        topics_and_answers.append(current_topic)
                    current_topic = {
                        "topic": content.strip(), "description": "", "answer": ""}

        # Add content to the current topic's description or answer if it matches the conditions
        elif current_topic:
            for element in paragraph.get("elements", []):
                text_run = element.get("textRun", {})
                content = text_run.get("content", "")
                text_style = text_run.get("textStyle", {})
                background_color = text_style.get("backgroundColor", {}).get(
                    "color", {}).get("rgbColor", {})

                # Check if the background color matches the description color
                if content and background_color == DESCRIPTION_COLOR:
                    # Escape special Markdown characters
                    content = escape_markdown_special_chars(content.strip())

                    # Apply Markdown formatting if necessary
                    if text_style.get("bold"):
                        content = f"**{content}**"
                    if text_style.get("underline"):
                        content = f"_{content}_"
                    if text_style.get("italic"):
                        content = f"*{content}*"

                    current_topic["description"] += content + " "

                # Check if the background color matches the answer color
                elif content and background_color == ANSWER_COLOR:
                    # Escape special Markdown characters
                    content = escape_markdown_special_chars(content.strip())

                    # Apply Markdown formatting if necessary
                    if text_style.get("bold"):
                        content = f"**{content}**"
                    if text_style.get("underline"):
                        content = f"_{content}_"
                    if text_style.get("italic"):
                        content = f"*{content}*"

                    current_topic["answer"] += content + " "

    # Add the last topic to the result
    if current_topic:
        topics_and_answers.append(current_topic)

    # Clean up extra spaces at the end of each description and answer
    for item in topics_and_answers:
        item["description"] = item["description"].strip()
        item["answer"] = item["answer"].strip()

    return topics_and_answers


def listen_for_changes(document_id=os.getenv('GOOGLE_DOCUMENT_ID')):
    """
    Listens for changes in a Google Docs document and processes revisions
      accordingly.

    Args:
        document_id (str): The ID of the Google Docs document to monitor.
    """
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
            new_content = extract_topics_and_answers(document)
            print_debug(new_content, level=None, is_json=True)
            if last_revision is None:
                last_revision = latest_revision
                last_content = new_content

            if last_revision != latest_revision:
                print_debug(
                    f"Nuevo cambio detectado en el documento. ID de revisión: {latest_revision}")
                try:
                    revision_info = drive_service.revisions().get(
                        fileId=DOCUMENT_ID, revisionId=latest_revision, fields='*').execute()
                    print_revision_info(revision_info)
                except HttpError as error:
                    if error.resp.status == 404:
                        print_debug(
                            f"Revisión no encontrada: {latest_revision}")
                        continue
                    else:
                        raise
                # print clear terminal
                print("\033c")
                for new_item in new_content:
                    for old_item in last_content:
                        if new_item['topic'] == old_item['topic']:
                            if new_item['description'] != old_item['description']:
                                print_debug(
                                    f"Descripción actualizada para el tema: {new_item['topic']}")
                                print_debug(
                                    f"Descripción anterior: {old_item['description']}")
                                print_debug(
                                    f"Descripción actual: {new_item['description']}")
                            if new_item['answer'] != old_item['answer']:
                                print_debug(
                                    f"Respuesta actualizada para el tema: {new_item['topic']}")
                                print_debug(
                                    f"Respuesta anterior: {old_item['answer']}")
                                print_debug(
                                    f"Respuesta actual: {new_item['answer']}")
                                topic = new_item['topic']
                                task_description = new_item['description']
                                answer = get_only_added_parts(
                                    old_item['answer'], new_item['answer'])
                                evaluation = evaluate_contributions(
                                    topic,
                                    task_description, answer)
                                print_debug(f"Evaluación: {evaluation}")
                            break
                last_revision = latest_revision
                last_content = new_content

            time.sleep(10)

    except HttpError as error:
        print_debug(f"Ha ocurrido un error: {error}")


if __name__ == "__main__":
    listen_for_changes()
