from dotenv import load_dotenv
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import json

load_dotenv()
llm = OpenAI()

def llm_response(prompt, tools):
  return llm.responses.create(
    model="gpt-5-mini",
    tools=tools,
    input=prompt
  )

def multiply(first_number, second_number):
  print(f"Multipltying {first_number} by {second_number}")
  product = int(first_number) * int(second_number)
  return product

def read_webpage(url):
  print(f"Leyendo {url}")
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  text = soup.get_text() ## obtain text from the webpage
  return text

TOOLS = [
  {
    "type": "function",
    "name": "multiply",
    "description": "Multiply two numbers to get a product.",
    "parameters": {
      "type": "object",
      "properties": {
        "first_number": {"type": "integer"},
        "second_number": {"type": "integer"},
      },
      "required": ["first_number", "second_number"],
    },
  },
  {
    "type": "function",
    "name": "read_webpage",
    "description": "Accesses a webpage and obtains its text.",
    "parameters": {
      "type": "object",
      "properties": {
        "url": {
          "type": "string",
          "description": "The URL of the webpage",
        }
      },
      "required": ["url"],
    },
  },
]

# ============================================================================
#
# Main loop
#
if __name__ == "__main__":
  assistant_message = "¿Cómo puedo ayudarte?"
  history = [
    {"role": "developer", "content": """You are a helpful AI assistant. If you
    ever need to multiply two numbers, DO NOT attempt to answer with your
    internal knowledge. Instead, use your multiply tool."""},
    {"role": "assistant", "content": "How can I help you today?"}
  ]
  print(f"Assistant: {assistant_message}\n")
  user_input = input("User: ")

while user_input != "exit":
  history += [{"role": "user", "content": user_input}]
  response = llm_response(history, TOOLS)
  history += response.output
  for item in response.output:
    if item.type == "function_call":
      function_call = item
      function_name = item.name
      args = json.loads(item.arguments)
      if function_name == "multiply":
        result = {"multiply": multiply(**args)}
      elif function_name == "read_webpage":
        result = {"read_webpage": read_webpage(**args)}
      
      history += [{"type": "function_call_output",
        "call_id": function_call.call_id,
        "output": json.dumps(result)}]
      response = llm_response(history, TOOLS)
  
    print(f"\nAssistant: {response.output}\n")
    history += [
      {"role": "assistant", "content": response.output},
    ]
    user_input = input("User: ")