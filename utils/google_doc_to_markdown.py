from pathlib import Path
from typing import Optional
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scope de solo lectura para mayor seguridad
REQUIRED_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_google_credentials() -> Credentials:
  """
  Maneja el flujo de autenticación expandiendo la ruta del home correctamente.
  """
  token_cache_path = Path("token.json")
  google_credentials = None
  
  # 1. Intentamos cargar el token guardado
  if token_cache_path.exists():
    google_credentials = Credentials.from_authorized_user_file(
      str(token_cache_path), 
      REQUIRED_SCOPES
    )
  
  # 2. Si no es válido, renovamos o iniciamos sesión
  if not google_credentials or not google_credentials.valid:
    if google_credentials and google_credentials.expired and google_credentials.refresh_token:
      google_credentials.refresh(Request())
    else:
      # Expandimos la ruta de gspread usando Path.home()
      config_path = Path.home() / ".config" / "gspread" / "credentials.json"
      
      if not config_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de credenciales en {config_path}")

      auth_flow = InstalledAppFlow.from_client_secrets_file(
        str(config_path), 
        REQUIRED_SCOPES
      )
      google_credentials = auth_flow.run_local_server(port=0)
      
    # 3. Guardamos para la próxima vez
    with open(token_cache_path, "w", encoding="utf-8") as token_file:
      token_file.write(google_credentials.to_json())
      
  return google_credentials

def export_google_document_to_markdown(document_identifier: str, google_credentials: Credentials) -> Optional[str]:
  """
  Llama a la API de Drive para realizar la conversión a Markdown.
  """
  try:
    drive_service = build("drive", "v3", credentials=google_credentials)
    
    export_request = drive_service.files().export_media(
      fileId=document_identifier,
      mimeType="text/markdown"
    )
    
    markdown_content_bytes = export_request.execute()
    return markdown_content_bytes.decode("utf-8")
    
  except HttpError as google_api_error:
    print(f"Error en la API de Google: {google_api_error}")
    return None

def extract_document_id(google_docs_url: str) -> str:
  """
  Extrae el ID alfanumérico de una URL de Google Docs.
  """
  match_pattern = re.search(r"/d/([^/]+)", google_docs_url)
  if match_pattern:
    return match_pattern.group(1)
  return google_docs_url # Si no hay match, asumimos que ya era un ID

def main():
  # URL completa del documento que pasaste
  document_url = "https://docs.google.com/document/d/13vAmPKbWfWpRWze3AhLwnCHfWktfIIXnju3PD_tzyW4/edit?tab=t.0"
  document_identifier = extract_document_id(document_url)
  
  print("Obteniendo credenciales...")
  google_credentials = get_google_credentials()
  
  print(f"Exportando documento (ID: {document_identifier})...")
  markdown_content = export_google_document_to_markdown(document_identifier, google_credentials)
  
  if markdown_content:
    with open("documento_exportado.md", "w", encoding="utf-8") as output_file:
      output_file.write(markdown_content)
    print("¡Exportación exitosa! Archivo guardado como 'documento_exportado.md'")

if __name__ == "__main__":
  main()