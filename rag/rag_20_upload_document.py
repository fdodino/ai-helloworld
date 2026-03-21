import os
import re
import sys
from typing import List
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

def get_semantic_markdown_chunks(markdown_content: str, max_characters: int = 25000) -> List[str]:
  """
  Divide el contenido por H1 y subdivide secciones extensas. 
  Si el párrafo sigue siendo muy grande, lo corta por caracteres.
  """
  h1_pattern = r"(?m)^# .+?(?=^# |\Z)"
  
  # 1. Separación inicial por H1
  initial_sections = [
    section.strip() 
    for section in re.findall(h1_pattern, markdown_content, re.DOTALL) 
    if section.strip()
  ]
  
  final_chunks = []
  for section in initial_sections:
    # Caso A: La sección entera entra en el límite
    if len(section) <= max_characters:
      final_chunks.append(section)
      continue
    
    # Caso B: Dividimos por párrafos (\n\n)
    paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
      if len(paragraph) <= max_characters:
        final_chunks.append(paragraph)
      else:
        # Caso C: El párrafo es un "monolito" (ej. código largo).
        # Lo cortamos por caracteres en bloques de max_characters.
        hard_splits = [
          paragraph[index : index + max_characters] 
          for index in range(0, len(paragraph), max_characters)
        ]
        final_chunks.extend(hard_splits)
      
  return final_chunks

def main():
  if len(sys.argv) < 2:
    print("Uso: uv run script.py <archivo_markdown>")
    sys.exit(1)

  file_path = sys.argv[1]
  
  if not os.path.exists(file_path):
    print(f"Error: No se encontró el archivo '{file_path}'")
    sys.exit(1)

  with open(file_path, "r", encoding="utf-8") as file_handle:
    content = file_handle.read()
    markdown_chunks = get_semantic_markdown_chunks(content)

  # Construcción de registros con ID único basado en el archivo
  pinecone_records = [
    {
      "id": f"{file_path.replace('.', '-')}-{index}",
      "chunk_text": chunk_text,
      "source_file": file_path
    }
    for index, chunk_text in enumerate(markdown_chunks)
  ]

  # Pinecone Client
  pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
  index_instance = pinecone_client.Index("phm")

  print(f"Subiendo {len(pinecone_records)} fragmentos a Pinecone...")
  
  # Subimos de a 50 para no saturar la conexión
  BATCH_SIZE = 50
  for i in range(0, len(pinecone_records), BATCH_SIZE):
    batch = pinecone_records[i : i + BATCH_SIZE]
    index_instance.upsert_records("phm", batch)
    
  print("¡Carga completada con éxito!")

if __name__ == "__main__":
  main()