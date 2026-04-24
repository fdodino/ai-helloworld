# /// script
# dependencies = [
#   "requests",
# ]
# ///

import sys
import json
import re
import requests
from pathlib import Path

def generate_code_with_ollama(user_prompt: str, output_file: str):
  """
  Consulta al modelo Qwen 2.5 Coder local y guarda el resultado en un archivo.
  """
  url = "http://localhost:11434/api/generate"
  model_name = "qwen2.5-coder:32b"
  
  # Le pedimos que sea purista: solo código, sin explicaciones.
  # Prompt augmentation
  full_prompt = (
    "Sos un experto en programación. Generá exclusivamente el código fuente "
    "para lo siguiente, sin explicaciones, sin texto introductorio y sin bloques de markdown: "
    f"{user_prompt}"
  )

  payload = {
    "model": model_name,
    "prompt": full_prompt,
    "stream": False,
    "options": {
      "temperature": 0
    }
  }

  print(f"Generando código con {model_name}...")

  try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    # Extraemos el texto de la respuesta de Ollama
    raw_content = response.json().get("response", "").strip()
    
    # Limpieza de seguridad por si el modelo ignora la instrucción y pone ```kotlin
    clean_code = re.sub(r"```[a-z]*\n|```", "", raw_content)

    # Guardado del archivo usando Pathlib
    file_path = Path(output_file)
    file_path.write_text(clean_code, encoding="utf-8")
    
    print(f"¡Listo! El código de '{user_prompt[:30]}...' se guardó en {file_path.absolute()}")

  except requests.exceptions.RequestException as error:
    print(f"Error al conectar con Ollama: {error}")
    sys.exit(1)

def main():
  # Uso: uv run script.py "Clase Pedido con Strategy para descuentos" "Pedido.kt"
  if len(sys.argv) < 3:
    print("Uso: uv run script.py '<instruccion>' '<nombre_archivo>'")
    sys.exit(1)

  instruccion = sys.argv[1]
  archivo_destino = sys.argv[2]

  generate_code_with_ollama(instruccion, archivo_destino)

if __name__ == "__main__":
  main()