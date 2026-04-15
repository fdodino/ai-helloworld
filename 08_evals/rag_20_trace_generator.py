import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, TextIO

from rag_10_chatbot_enhanced import (
    inicializar_clientes,
    buscar_documentos_relevantes,
    extraer_documentacion_de_resultados,
    construir_prompt_sistema,
    construir_prompt_usuario,
    generar_respuesta_llm,
    MENSAJE_ASISTENTE
)

DIRECTORIO_SCRIPT = Path(__file__).parent
ARCHIVO_ENTRADA = DIRECTORIO_SCRIPT / "orm_queries.csv"
ARCHIVO_SALIDA = DIRECTORIO_SCRIPT / "orm_traces.csv"
COLUMNAS_SALIDA = ["Query Topic", "User Query", "History", "AI Response"]


def verificar_archivo_entrada(ruta_archivo: Path) -> None:
    """Verifica que el archivo de entrada exista, terminando si no se encuentra.
    
    Args:
        ruta_archivo: Ruta del archivo CSV de consultas
    """
    if not ruta_archivo.exists():
        print(f"❌ Error: Archivo de entrada no encontrado en '{ruta_archivo.absolute()}'", file=sys.stderr)
        sys.exit(1)


def abrir_archivos_csv(
    ruta_entrada: Path, 
    ruta_salida: Path
) -> tuple[TextIO, TextIO]:
    """Abre los archivos CSV de entrada y salida.
    
    Args:
        ruta_entrada: Ruta del archivo CSV de consultas
        ruta_salida: Ruta del archivo CSV de salida
        
    Returns:
        Tupla con los objetos de archivo (lectura, escritura)
    """
    try:
        archivo_lectura = ruta_entrada.open("r")
        archivo_escritura = ruta_salida.open("w", newline="", encoding="utf-8")
        return archivo_lectura, archivo_escritura
    except FileNotFoundError as error:
        print(f"❌ Error: No se pudo abrir el archivo - {error}", file=sys.stderr)
        sys.exit(1)


def limpiar_saltos_de_linea(texto: str) -> str:
    """Reemplaza saltos de línea por espacios para compatibilidad con Google Sheets.
    
    Args:
        texto: Texto a limpiar
        
    Returns:
        Texto con saltos de línea reemplazados por espacios
    """
    if isinstance(texto, str):
        return texto.replace("\n", " ").replace("\r", " ")
    return texto


def construir_historial_inicial() -> List[Dict[str, str]]:
    """Construye el historial de conversación inicial con prompt de sistema y saludo.
    
    Returns:
        Lista con los mensajes iniciales del historial
    """
    return [
        construir_prompt_sistema(),
        {"role": "assistant", "content": MENSAJE_ASISTENTE}
    ]


def procesar_consulta(
    indice_pinecone: Any,
    cliente_llm: Any,
    fila: Dict[str, str]
) -> Dict[str, str]:
    """Procesa una consulta individual generando la respuesta del LLM.
    
    Args:
        indice_pinecone: Cliente del índice de Pinecone
        cliente_llm: Cliente de Groq
        fila: Fila del CSV con 'Query Topic' y 'User Query'
        
    Returns:
        Diccionario con los datos para escribir en el CSV de salida
    """
    historial = construir_historial_inicial()
    
    resultados = buscar_documentos_relevantes(indice_pinecone, fila["User Query"])
    documentacion = extraer_documentacion_de_resultados(resultados)
    historial.append(construir_prompt_usuario(documentacion, fila["User Query"]))
    
    respuesta = generar_respuesta_llm(cliente_llm, historial)
    contenido_respuesta = respuesta.choices[0].message.content
    contenido_limpio = limpiar_saltos_de_linea(contenido_respuesta)
    
    return {
        "Query Topic": fila["Query Topic"],
        "User Query": fila["User Query"],
        "History": json.dumps(historial),
        "AI Response": contenido_limpio
    }


def generar_trazas() -> None:
    """Función principal que genera las trazas de conversación desde el CSV de consultas."""
    verificar_archivo_entrada(ARCHIVO_ENTRADA)
    
    indice_pinecone, cliente_llm = inicializar_clientes()
    archivo_lectura, archivo_escritura = abrir_archivos_csv(ARCHIVO_ENTRADA, ARCHIVO_SALIDA)
    
    with archivo_lectura, archivo_escritura:
        lector_csv = csv.DictReader(archivo_lectura)
        escritor_csv = csv.DictWriter(archivo_escritura, fieldnames=COLUMNAS_SALIDA)
        escritor_csv.writeheader()
        
        for indice_fila, fila in enumerate(lector_csv, 1):
            resultado = procesar_consulta(indice_pinecone, cliente_llm, fila)
            escritor_csv.writerow(resultado)
            print(f"Consulta {indice_fila} completada")


if __name__ == "__main__":
    generar_trazas()