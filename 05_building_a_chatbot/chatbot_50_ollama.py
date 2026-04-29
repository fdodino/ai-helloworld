import requests
import json
import sys
from pathlib import Path

def ask_ollama_to_write_file(prompt: str, output_file: str, model: str = "qwen2.5-coder:32b"):
  """
  Envía un prompt a Ollama y guarda la respuesta directamente en un archivo.
  """
  url = "http://localhost:11434/api/generate"
  payload = {
    "model": model,
    "prompt": f"Generá exclusivamente el código para lo siguiente, sin explicaciones ni markdown: {prompt}",
    "stream": False
  }

  print(f"Consultando a {model}...")
  response = requests.post(url, json=payload)
  
  if response.status_code == 200:
    code_content = response.json().get("response", "").strip()
    
    # Limpiamos posibles backticks de markdown si el modelo los incluyó
    code_content = re.sub(r"```[a-z]*\n|```", "", code_content)
    
    Path(output_file).write_text(code_content, encoding="utf-8")
    print(f"¡Archivo '{output_file}' guardado con éxito!")
  else:
    print(f"Error al conectar con Ollama: {response.status_code}")

if __name__ == "__main__":
  # Uso: python escribir.py "Clase Persona en Kotlin con herencia" "Persona.kt"
  if len(sys.argv) < 3:
    print("Uso: python script.py '<prompt>' '<nombre_archivo>'")
  else:
    import re # Import tardío para limpieza
    ask_ollama_to_write_file(sys.argv[1], sys.argv[2])