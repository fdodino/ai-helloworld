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

assistant_message = "How can I help you today?"
def assistant_prompt():
  return {
    "role": "assistant",
    "content": assistant_message
  }

def rag_results_to_documentation(results):
  chunks = [hit.get('fields', {}).get('chunk_text', '') for hit in results['result']['hits']]
  return "".join(chunks)

def search_all_docs():
  return dense_index.search(
    namespace="orm",
    query={
      "top_k": 3,
      "inputs": {
          'text': user_input
        }
      }
    )

def user_prompt(documentation, user_input):
  return [
    {"role": "user",
    "content": f"""Here are excerpts from the O/R mapping documentation: {documentation}. Use whatever
    info from the above documentation excerpts (and no other info)
    to answer the following query: {user_input}"""}
  ]

def llm_response(prompt):
  return llm.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0,
    messages=prompt
  )

# ============================================================================
#
# Main loop
#
print(f"Assistant: {assistant_message}\n")
user_input = input("User: ")
history = [
  system_prompt(),
  assistant_prompt()
]

while user_input != "exit":
  results = search_all_docs()
  documentation = rag_results_to_documentation(results)
  current_prompt = user_prompt(documentation, user_input)
  history += current_prompt
  response = llm_response(current_prompt)

  answer = response.choices[0].message.content
  print(f"\nAssistant: {answer}\n")
  history += [
    {"role": "assistant", "content": answer},
  ]
  user_input = input("User: ")