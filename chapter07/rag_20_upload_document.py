import os
import re
import sys
import time
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone

NAMESPACE_PINE = "phm"


def procesar_parrafos_validos(
    parrafos: List[str], 
    minimo_caracteres: int, 
    maximo_caracteres: int
) -> List[str]:
    """
    Procesa una lista de párrafos, filtrando por tamaño mínimo y cortando los largos.
    
    Args:
        parrafos: Lista de párrafos a procesar
        minimo_caracteres: Mínimo de caracteres para considerar válido
        maximo_caracteres: Máximo de caracteres antes de cortar
        
    Returns:
        Lista de fragmentos procesados
    """
    parrafos_validos = [
        parrafo for parrafo in parrafos 
        if len(parrafo) >= minimo_caracteres
    ]
    
    fragmentos_procesados = []
    for parrafo in parrafos_validos:
        if len(parrafo) <= maximo_caracteres:
            fragmentos_procesados.append(parrafo)
        else:
            fragmentos_cortados = [
                parrafo[indice : indice + maximo_caracteres] 
                for indice in range(0, len(parrafo), maximo_caracteres)
            ]
            fragmentos_procesados.extend(fragmentos_cortados)
    
    return fragmentos_procesados


def dividir_contenido_markdown(
    contenido_markdown: str, 
    maximo_caracteres: int = 25000,
    minimo_caracteres: int = 5
) -> List[str]:
    """
    Divide el contenido markdown por encabezados H1 y subdivide secciones extensas.
    Si un párrafo sigue siendo muy grande, lo corta por caracteres.
    
    Args:
        contenido_markdown: Contenido markdown a procesar
        maximo_caracteres: Límite máximo de caracteres por fragmento
        minimo_caracteres: Mínimo de caracteres para considerar un fragmento válido
        
    Returns:
        Lista de fragmentos de contenido
    """
    patron_h1 = r"(?m)^# .+?(?=^# |\Z)"
    
    # Separación inicial por encabezados H1
    secciones_iniciales = [
        seccion.strip() 
        for seccion in re.findall(patron_h1, contenido_markdown, re.DOTALL) 
        if seccion.strip()
    ]
    
    # Filtrar secciones que entran en el límite y tienen mínimo de caracteres
    secciones_pequenas = list(filter(
        lambda seccion: len(seccion) <= maximo_caracteres and len(seccion) >= minimo_caracteres, 
        secciones_iniciales
    ))
    
    # Procesar secciones grandes
    secciones_grandes = list(filter(
        lambda seccion: len(seccion) > maximo_caracteres, 
        secciones_iniciales
    ))
    
    fragmentos_adicionales = []
    for seccion in secciones_grandes:
        # Dividir por párrafos
        parrafos = [parrafo.strip() for parrafo in seccion.split("\n\n") if parrafo.strip()]
        
        # Procesar párrafos válidos
        fragmentos_procesados = procesar_parrafos_validos(parrafos, minimo_caracteres, maximo_caracteres)
        fragmentos_adicionales.extend(fragmentos_procesados)
        
    return secciones_pequenas + fragmentos_adicionales


def construir_registros_pinecone(
    ruta_archivo: str, 
    fragmentos_texto: List[str]
) -> List[Dict[str, Any]]:
    """
    Construye registros para Pinecone con IDs únicos basados en el archivo.
    
    Args:
        ruta_archivo: Ruta del archivo fuente
        fragmentos_texto: Lista de fragmentos de texto
        
    Returns:
        Lista de registros para Pinecone
    """
    return [
        {
            "id": f"{ruta_archivo.replace('.', '-')}-{indice}",
            "chunk_text": fragmento_texto,
            "source_file": ruta_archivo
        }
        for indice, fragmento_texto in enumerate(fragmentos_texto)
    ]


def subir_fragmentos_a_pinecone(
    registros: List[Dict[str, Any]], 
    nombre_indice: str = "phm",
    tamano_lote: int = 10
) -> None:
    """
    Sube fragmentos a Pinecone en lotes para evitar saturación.
    
    Args:
        registros: Lista de registros a subir
        nombre_indice: Nombre del índice en Pinecone
        tamano_lote: Tamaño de los lotes para subida
    """
    load_dotenv()
    cliente_pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    instancia_indice = cliente_pinecone.Index(nombre_indice)
    
    print(f"Subiendo {len(registros)} fragmentos a Pinecone...")
    
    for indice_lote in range(0, len(registros), tamano_lote):
        lote_actual = registros[indice_lote : indice_lote + tamano_lote]
        instancia_indice.upsert_records(records=lote_actual, namespace=NAMESPACE_PINE)
        # Esperar 3 segundos entre lotes para no exceder la quota de tokens por minuto
        time.sleep(3)
    
    print("¡Carga completada con éxito!")


def procesar_documento_markdown(ruta_archivo: str) -> None:
    """
    Procesa un documento markdown y lo sube a Pinecone.
    
    Args:
        ruta_archivo: Ruta del archivo markdown a procesar
    """
    if not Path(ruta_archivo).exists():
        print(f"Error: No se encontró el archivo '{ruta_archivo}'")
        sys.exit(1)
    
    contenido = Path(ruta_archivo).read_text(encoding="utf-8")
    fragmentos = dividir_contenido_markdown(contenido)
    registros = construir_registros_pinecone(ruta_archivo, fragmentos)
    subir_fragmentos_a_pinecone(registros)


def main():
    if len(sys.argv) < 2:
        print("Uso: uv run script.py <archivo_markdown>")
        sys.exit(1)
    
    ruta_archivo = sys.argv[1]
    procesar_documento_markdown(ruta_archivo)

if __name__ == "__main__":
  main()