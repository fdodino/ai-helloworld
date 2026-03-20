from dotenv import load_dotenv
from groq import Groq

load_dotenv()
llm = Groq()
response = llm.chat.completions.create(
  model="llama-3.3-70b-versatile",
  temperature=0,
  # max_tokens=10,
  messages=[
    {
      "role": "user",
      "content": "No por mucho madrugar..."
    }
  ]
)

print(response.choices[0].message.content)

# Preguntas
# - Por qué las ballenas no consiguen trabajo de programador? temperatura 0 = +determinístico, 2 = +creativo
# - Límite de tokens? max_tokens=10
