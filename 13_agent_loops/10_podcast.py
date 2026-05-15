import json
from datetime import date
from llm_tools import read_webpage, search_web, create_audio
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
language_model = OpenAI()

def llm_response(prompt_history, tools_definition):
  response = language_model.responses.create(
    model="gpt-5-mini",
    tools=tools_definition,
    input=prompt_history
  )
  return response

TOOLS = [
  {
    "type": "function",
    "name": "search_web",
    "description": """Searches the web based on a query and 
retrieves an array of relevant URLs.""",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The query of the web search",
        },
      },
      "required": ["query"],
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
  {
    "type": "function",
    "name": "create_audio",
    "description": """Uses speech-to-text technology to convert a 
podcast script (string) into an audio mp3 podcast 
named podcast.mp3.""",
    "parameters": {
      "type": "object",
      "properties": {
        "script": {
          "type": "string",
          "description": "A podcast script read by a single host",
        },
      },
      "required": ["script"],
    },
  },
]

TOOL_FUNCTIONS = {
  "search_web": search_web,
  "read_webpage": read_webpage,
  "create_audio": create_audio,
}

print(f"Assistant: How can I help you today?\n")
user_input = input("User: ")

conversation_history = [
  {
    "role": "developer",
    "content": f"""You are an AI assistant. Today's 
date is {date.today().strftime("%B %d, %Y")}.
You have access to several specialized tools. Here are your tools:
<tools>
* With the search_web tool, you have the ability to search the web based 
on a query and retrieve URLs of web pages relevant to that query.
* With the read_webpage tool, you have the ability to read the text from 
a web page of any given URL.
* With the create_audio tool, you can convert a podcast script text into 
an audio mp3 podcast.
</tools>"""
  },
  {"role": "assistant", "content": "How can I help you today?"}
]

while user_input != "exit":
  conversation_history += [{"role": "user", "content": user_input}]
  
  while True:
    current_response = llm_response(conversation_history, TOOLS)
    conversation_history += current_response.output
    
    tool_calls = [
      tool_object for tool_object in current_response.output 
      if getattr(tool_object, "type", None) == "function_call"
    ]
    
    if not tool_calls:
      break
    
    for tool_call in tool_calls:
      function_name = tool_call.name
      function_arguments = json.loads(tool_call.arguments)
      target_function = TOOL_FUNCTIONS.get(function_name)
      
      execution_result = {function_name: target_function(**function_arguments)}
      
      conversation_history += [{
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": json.dumps(execution_result)
      }]
      
  print(f"\nAssistant: {current_response.output_text}\n")
  conversation_history += [
    {"role": "assistant", "content": current_response.output_text},
  ]
  user_input = input("User: ")