from dotenv import load_dotenv
from groq import Groq

load_dotenv()
llm = Groq()

user_input = input("Enter a phrase, and I'll translate it into Spanish!\n")

response = llm.chat.completions.create(
  model="llama-3.3-70b-versatile",
  temperature=0,
  # max_tokens=10,
  messages=[
    {
      "role": "user",
      "content": f"Translate the following phrase into Spanish: {user_input}"
    }
  ]
)

print(response.choices[0].message.content)

