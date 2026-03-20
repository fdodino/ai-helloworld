from dotenv import load_dotenv
from groq import Groq

load_dotenv()
llm = Groq()

developer_role = {
  "role": "developer",
  "content": "You are a fan of conspiracy theories assistant."
}
assistant_message = {
  "role": "assistant",
  "content": "Assistant: How can I help you today? (Exit to quit)"
}
print(f"Assistant: {assistant_message['content']}")
history = [developer_role, assistant_message]
user_input = input("User: ")

while (user_input.lower() != "exit"):
    history += [{
      "role": "user", 
      "content": user_input
    }]
    response = llm.chat.completions.create(
      model="llama-3.3-70b-versatile",
      temperature=0,
      # max_tokens=10,
      messages=history
    )

    last_response = response.choices[0].message.content
    print(f"Assistant: {last_response}")
    print("------------------------------------------------------------------")
    history += [{"role": "assistant", "content": last_response}]
    user_input = input("User: ")

