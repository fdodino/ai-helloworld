import os
from dotenv import load_dotenv
from pinecone import Pinecone
from groq import Groq

load_dotenv()
llm = Groq()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("phm")

def system_prompt():
  return {
    "role": "developer",
    "content": """You are an AI teacher who is knowledgeable about software object/relational mapping"""
  }

assistant_message = "¿Cómo puedo ayudarte?"
def assistant_prompt():
  return {
    "role": "assistant",
    "content": assistant_message
  }

def rag_results_to_documentation(results):
  chunks = [hit.get('fields', {}).get('chunk_text', '') for hit in results['result']['hits']]
  return "".join(chunks)

def search_all_docs(user_query):
  return dense_index.search(
    namespace="orm",
    query={
      "top_k": 3,
      "inputs": {
          'text': user_query
        }
      }
    )

def user_prompt(documentation, user_input):
  return {
    "role": "user",
    "content": f"""Here are excerpts from the O/R mapping documentation: {documentation}. Use whatever
    info from the above documentation excerpts (and no other info)
    to answer the following query: {user_input}"""
  }

def llm_response(prompt):
  return llm.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0,
    messages=prompt
  )

def expand_query(conversation):
response = llm.responses.create(
    model="gpt-4.1-nano",
    temperature=0,
    input=f"Rewrite, in an expanded way, what the user means to say
in their final prompt of the following conversation: {conversation}"
)
return response.output_text

# ============================================================================
#
# Main loop
#
if __name__ == "__main__":
  print(f"Assistant: {assistant_message}\n")
  user_input = input("User: ")
  
  # El historial real solo debería guardar la esencia de la charla
  conversacion_history = [
    system_prompt(),
    assistant_prompt()
  ]

  while user_input != "exit":
    results = search_all_docs(user_input)
    documentation = rag_results_to_documentation(results)
    
    # Creamos el prompt para ESTA llamada, pero no lo guardamos eterno con la doc
    prompt_con_documentacion = user_prompt(documentation, user_input)
    
    # Para la llamada al LLM, combinamos el historial previo + el prompt con RAG
    # pero NO guardamos la documentación pesada en el historial de la próxima vuelta
    llamada_mensajes = conversacion_history + [prompt_con_documentacion]
    
    response = llm_response(llamada_mensajes)

    answer = response.choices[0].message.content
    print(f"\nAssistant: {answer}\n")
    
    # Guardamos en el historial solo la pregunta limpia y la respuesta
    # así evitamos saturar el contexto con fragmentos de docs viejos
    conversacion_history.append({"role": "user", "content": user_input})
    conversacion_history.append({"role": "assistant", "content": answer})
    
    user_input = input("User: ")