import os
from typing import Optional
from dotenv import load_dotenv
from pinecone import Pinecone


def crear_indice_pinecone(
    nombre_indice: str = "phm",
    modelo_embedding: str = "llama-text-embed-v2",
    campo_mapeo: dict = {"text": "chunk_text"},
    nube: str = "aws",
    region: str = "us-east-1"
) -> Optional[Pinecone]:
    """
    Crea un índice denso en Pinecone con embedding integrado.
    
    Args:
        nombre_indice: Nombre del índice a crear
        modelo_embedding: Modelo de embedding a utilizar
        campo_mapeo: Mapeo de campos para el embedding
        nube: Proveedor de cloud
        region: Región del cloud
        
    Returns:
        Cliente Pinecone configurado o None si el índice ya existe
    """
    load_dotenv()
    cliente_pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    
    if not cliente_pinecone.has_index(nombre_indice):
        cliente_pinecone.create_index_for_model(
            name=nombre_indice,
            cloud=nube,
            region=region,
            embed={
                "model": modelo_embedding,
                "field_map": campo_mapeo
            }
        )
        print(f"Índice '{nombre_indice}' creado exitosamente")
    else:
        print(f"Índice '{nombre_indice}' ya existe")
        
    return cliente_pinecone


if __name__ == "__main__":
    crear_indice_pinecone()
