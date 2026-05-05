from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()
llm = Groq()

def llm_response(prompt):
  response = llm.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0,
    messages=prompt
  )
  return response.choices[0].message.content

def extract_function(response):
  # Regex to detect <<function(arg1, arg2)>>
  pattern = r"<<\s*([a-zA-Z_]\w*)\s*\(([^)]+)\)\s*>>"
  match = re.search(pattern, response)
  if not match: # No matching brackets found
    return None
  function_name = match.group(1) ## extract function name
  args = match.group(2).split(",") ## extract array of function arguments
  if function_name == "multiply":
    return multiply(*args)
  else:
    return None

def multiply(first_number, second_number):
  product = int(first_number) * int(second_number)
  return product

# ============================================================================
#
# Main loop
#
if __name__ == "__main__":
  assistant_message = "¿Cómo puedo ayudarte?"
  history = [{"role": "assistant", "content": assistant_message}]
  print(f"Assistant: {assistant_message}\n")
  user_input = input("User: ")

  while user_input != "exit":
    history += [{"role": "user", "content": user_input}]
    response = llm_response(history)
    function_result = extract_function(response)
    if function_result:
      response_text = str(function_result)
    else:
      response_text = response
    print(f"\nAssistant: {response_text}\n")
    history += [
      {"role": "assistant", "content": response_text},
    ]
    user_input = input("User: ")