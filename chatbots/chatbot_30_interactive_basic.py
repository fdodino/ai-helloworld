from dotenv import load_dotenv
from groq import Groq

load_dotenv()
llm = Groq()

user_input = input("Assistant: How can I help you today? (Exit to quit)\n\nUser: ")

while (user_input.lower() != "exit"):
    response = llm.chat.completions.create(
      model="llama-3.3-70b-versatile",
      temperature=0,
      # max_tokens=10,
      messages=[
        {
          "role": "user",
          "content": user_input
        }
      ]
    )

    print(f"Assistant: {response.choices[0].message.content}")
    user_input = input("User: ")

