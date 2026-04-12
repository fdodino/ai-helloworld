import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone
from groq import Groq


NAMESPACE_PINE = "phm"
NOMBRE_INDICE = "phm"


def inicializar_clientes() -> tuple[Pinecone.Index, Groq]:
    """
    Inicializa los clientes de Pinecone y Groq.
    
    Returns:
        Tupla con (indice_pinecone, cliente_groq)
    """
    load_dotenv()
    cliente_pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    indice = cliente_pinecone.Index(NOMBRE_INDICE)
    cliente_llm = Groq()
    return indice, cliente_llm


def buscar_fragmentos_relevantes(
    indice_pinecone: Pinecone.Index,
    consulta_usuario: str
) -> List[Dict[str, Any]]:
    """
    Busca fragmentos relevantes en Pinecone para la consulta del usuario.
    
    Args:
        indice_pinecone: Índice de Pinecone para buscar
        consulta_usuario: Consulta del usuario
        
    Returns:
        Lista de hits encontrados
    """
    resultados = indice_pinecone.search(
        namespace=NAMESPACE_PINE,
        query={
            "top_k": 3,
            "inputs": {"text": consulta_usuario}
        }
    )
    
    hits = resultados.get("result", {}).get("hits", [])
    
    # Si no hay resultados, intentar con término alternativo
    if len(hits) == 0:
        terminos_alternativos = ["herencia", "mapeo", "jerarquia", "clases", "polimorfismo", "inheritance"]
        for termino in terminos_alternativos:
            resultados_alt = indice_pinecone.search(
                namespace=NAMESPACE_PINE,
                query={
                    "top_k": 3,
                    "inputs": {"text": termino}
                }
            )
            hits_alt = resultados_alt.get("result", {}).get("hits", [])
            if len(hits_alt) > 0:
                return hits_alt
    
    return hits


def extraer_texto_documentacion(hits: List[Dict[str, Any]]) -> str:
    """
    Extrae y concatena el texto de los fragmentos encontrados.
    
    Args:
        hits: Lista de hits de Pinecone
        
    Returns:
        Texto de documentación concatenado
    """
    fragmentos_texto = [
        hit.get("fields", {}).get("chunk_text", "")
        for hit in hits
        if hit.get("fields", {}).get("chunk_text")
    ]
    return "".join(fragmentos_texto)


def generar_respuesta(
    cliente_llm: Groq,
    consulta_usuario: str,
    documentacion: str
) -> str:
    """
    Genera una respuesta usando el LLM basada en la documentación.
    
    Args:
        cliente_llm: Cliente de Groq
        consulta_usuario: Consulta del usuario
        documentacion: Documentación relevante
        
    Returns:
        Respuesta generada por el LLM
    """
    mensaje_sistema = (
        "You are an AI teacher who is knowledgeable about software object/relational mapping. "
        f"Here are excerpts from the O/R mapping documentation: {documentacion}. "
        "Use whatever info from the above documentation excerpts (and no other info) "
        f"to answer the following query: {consulta_usuario}"
    )
    
    respuesta = cliente_llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[{"role": "user", "content": mensaje_sistema}]
    )
    
    return respuesta.choices[0].message.content


def ejecutar_chatbot() -> None:
    """Ejecuta el loop principal del chatbot RAG."""
    indice_pinecone, cliente_llm = inicializar_clientes()
    
    mensaje_bienvenida = "¿Cómo puedo ayudarte hoy?"
    print(f"Assistant: {mensaje_bienvenida}\n")
    
    entrada_usuario = input("User: ")
    
    while entrada_usuario != "exit":
        # RAG: Recuperar fragmentos relevantes
        hits = buscar_fragmentos_relevantes(indice_pinecone, entrada_usuario)
        
        # RAG: Extraer documentación
        documentacion = extraer_texto_documentacion(hits)
        
        # RAG: Generar respuesta
        respuesta = generar_respuesta(cliente_llm, entrada_usuario, documentacion)
        
        print(f"\nAssistant: {respuesta}\n")
        
        entrada_usuario = input("User: ")


if __name__ == "__main__":
    ejecutar_chatbot()