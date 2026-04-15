import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone
from groq import Groq

NAMESPACE_PINE = "phm"
NOMBRE_INDICE = "phm"
MENSAJE_ASISTENTE = "¿Cómo puedo ayudarte?"

def inicializar_clientes() -> tuple[Pinecone.Index, Groq]:
    """Inicializa y retorna los clientes de Pinecone y Groq."""
    load_dotenv()
    cliente_pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    indice_pinecone = cliente_pinecone.Index(NOMBRE_INDICE)
    cliente_llm = Groq()
    return indice_pinecone, cliente_llm

def construir_prompt_sistema() -> Dict[str, str]:
    """Construye el prompt del sistema con el rol del profesor."""
    return {
        "role": "developer",
        "content": "You are an AI teacher who is knowledgeable about software object/relational mapping"
    }

def construir_prompt_asistente() -> Dict[str, str]:
    """Construye el prompt del asistente inicial."""
    return {
        "role": "assistant",
        "content": MENSAJE_ASISTENTE
    }

def extraer_documentacion_de_resultados(resultados: Dict[str, Any]) -> str:
    """Extrae y concatena los fragmentos de texto de los resultados de Pinecone.
    
    Args:
        resultados: Respuesta de Pinecone con los hits
        
    Returns:
        Texto concatenado de todos los fragmentos
    """
    fragmentos = [
        hit.get("fields", {}).get("chunk_text", "")
        for hit in resultados.get("result", {}).get("hits", [])
    ]
    return "".join(fragmentos)

def buscar_documentos_relevantes(
    indice_pinecone: Pinecone.Index, 
    consulta_usuario: str
) -> Dict[str, Any]:
    """Busca documentos relevantes en Pinecone para la consulta del usuario.
    
    Args:
        indice_pinecone: Cliente de índice de Pinecone
        consulta_usuario: Texto de la consulta
        
    Returns:
        Resultados de la búsqueda vectorial
    """
    return indice_pinecone.search(
        namespace=NAMESPACE_PINE,
        query={
            "top_k": 5,
            "inputs": {"text": consulta_usuario}
        }
    )

def construir_prompt_usuario(documentacion: str, consulta: str) -> Dict[str, str]:
    """Construye el prompt del usuario con la documentación RAG.
    
    Args:
        documentacion: Fragmentos de documentación recuperados
        consulta: Pregunta del usuario
        
    Returns:
        Diccionario del mensaje de usuario
    """
    return {
        "role": "user",
        "content": (
            f"Here are excerpts from the O/R mapping documentation: {documentacion}. "
            f"Use whatever info from the above documentation excerpts (and no other info) "
            f"to answer the following query: {consulta}"
        )
    }

def generar_respuesta_llm(cliente_llm: Groq, mensajes: List[Dict[str, str]]) -> Any:
    """Genera una respuesta usando el LLM de Groq.
    
    Args:
        cliente_llm: Cliente de Groq
        mensajes: Lista de mensajes para el contexto
        
    Returns:
        Respuesta del modelo
    """
    return cliente_llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=mensajes
    )

def ejecutar_chatbot() -> None:
    """Ejecuta el loop principal del chatbot RAG con manejo de historial optimizado."""
    indice_pinecone, cliente_llm = inicializar_clientes()
    
    print(f"Assistant: {MENSAJE_ASISTENTE}\n")
    entrada_usuario = input("User: ")
    
    # El historial solo guarda la esencia de la charla, sin documentación pesada
    historial_conversacion = [
        construir_prompt_sistema(),
        construir_prompt_asistente()
    ]
    
    while entrada_usuario != "exit":
        # RAG: Recuperar fragmentos relevantes
        resultados = buscar_documentos_relevantes(indice_pinecone, entrada_usuario)
        documentacion = extraer_documentacion_de_resultados(resultados)
        
        # Prompt para esta llamada con documentación RAG
        prompt_con_documentacion = construir_prompt_usuario(documentacion, entrada_usuario)
        
        # Combinar historial + prompt con RAG (sin guardar docs en historial)
        mensajes_llamada = historial_conversacion + [prompt_con_documentacion]
        
        # Generar respuesta
        respuesta = generar_respuesta_llm(cliente_llm, mensajes_llamada)
        contenido_respuesta = respuesta.choices[0].message.content
        
        print(f"\nAssistant: {contenido_respuesta}\n")
        
        # Guardar solo pregunta y respuesta (sin documentación) en historial
        historial_conversacion.append({"role": "user", "content": entrada_usuario})
        historial_conversacion.append({"role": "assistant", "content": contenido_respuesta})
        
        entrada_usuario = input("User: ")


if __name__ == "__main__":
    ejecutar_chatbot()