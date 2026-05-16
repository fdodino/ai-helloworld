import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from llm_tools import read_webpage, search_web, create_audio
import requests
from bs4 import BeautifulSoup

load_dotenv()
language_model = OpenAI()
google_api_key = os.getenv("GOOGLE_API_KEY")
search_engine_id = os.getenv("SEARCH_ENGINE_ID")
research_data = []
previous_web_queries = []

class AgentIterator:
  def __init__(self, history, tools):
    self.history = history
    self.tools = tools
    self._active = True

  def has_next(self):
    return self._active

  def next(self):
    print("[Agent] Thinking (calling LLM)...")
    response = llm_response(self.history, self.tools)
    self.history += response.output
    
    tool_calls = [
      output_item for output_item in response.output 
      if getattr(output_item, "type", None) == "function_call"
    ]
    
    execute_tool_calls(tool_calls, self.history)
    self._active = len(tool_calls) > 0
      
    return response

def llm_response(prompt_history, tools_definition):
  print("[LLM] Sending request to OpenAI (gpt-5-mini)...")
  response = language_model.responses.create(
    model="gpt-5-mini",
    tools=tools_definition,
    input=prompt_history
  )
  print("[LLM] Received response.")
  return response

def generate_web_query(podcast_description):
  print("[Research] Generating search query...")
  web_query = language_model.responses.create(
    model="gpt-5-mini",
    input=f"""You are doing research for a podcast, whose details are:
<details>{podcast_description}</details> Generate a Google web
search query to help do research for this podcast.
<instructions>
Ensure that your web search query is different than any of the past
queries made: <old_query_list>{previous_web_queries}</old_query_list>.
The web search query should be specific and succinct, no more than 6
words. For example, if the podcast topic is about the public
reception of ChatGPT 5, your query would be simply: public reception
of ChatGPT 5
</instructions>
Generate the web query now:"""
  )
  previous_web_queries.append(web_query.output_text)
  print(f"[Research] Generated query: '{web_query.output_text}'")
  return web_query.output_text

def extract_text(urls, podcast_description):
  print(f"[Research] Extracting text from {len(urls)} URLs...")
  for webpage_url in urls:
    webpage_text = read_webpage(webpage_url)
    extracted_text = language_model.responses.create(
      model="gpt-5-mini",
      input=f"""You are doing research for a podcast, whose details
are: <details>{podcast_description}</details>
Extract whatever relevant information you can from this info
you've found on the web: <webpage>{webpage_text}</webpage>.
Just include the extracted text and nothing else in your
response. Generate the extracted text now:"""
    )
    research_data.append(extracted_text.output_text)
  print("[Research] Done extracting text.")

def has_sufficient_research(podcast_description):
  print("[Research] Evaluating if gathered information is sufficient...")
  sufficient_research = language_model.responses.create(
    model="gpt-5-mini",
    input=f"""You are doing research for a podcast, whose details are:
<details>{podcast_description}</details>. Here is the research you
have from the web so far: <research>{research_data}</research>. Do you
feel that you have enough info to create a fact-based podcast
based on this research with the information you have so far?
Keep in mind the desired length of the podcast.
Respond with either: True/False
"""
  )
  is_sufficient = sufficient_research.output_text.strip().lower() == "true"
  print(f"[Research] Sufficient information gathered: {is_sufficient}")
  return is_sufficient

def write_podcast_script(podcast_description):
  print("[Writer] Drafting the podcast script...")
  script = language_model.responses.create(
    model="gpt-5-mini",
    input=f"""You are a podcast scriptwriter, creating scripts for
news-based and explainer podcasts. The podcast should be based on
real facts and web research. As such, do not create any fictional
information for the podcast. Only use what you find based on your
web research.
Here are the details of what the podcast should be:
<details>{podcast_description}</details> Here is the research you
should use to produce the script: <research>{research_data}</research>
The script is read by a single host in a news-like style. Do not
create music or the like. Only create the words to be spoken by
the host. Create the script now:"""
  )
  print("[Writer] Script generated successfully.")
  return script.output_text

def initiate_podcast(podcast_description):
  print(f"[Workflow] Initiating podcast generator for description: '{podcast_description}'")
  needs_more_research = True
  iteration = 1
  while needs_more_research:
    print(f"[Workflow] Research iteration #{iteration}...")
    web_query = generate_web_query(podcast_description)
    search_results = search_web(web_query)
    extract_text(search_results, podcast_description)
    needs_more_research = not has_sufficient_research(podcast_description)
    iteration += 1
    
  podcast_script = write_podcast_script(podcast_description)
  create_audio(podcast_script)
  print("[Workflow] Podcast creation complete!")

TOOLS = [
  {
    "type": "function",
    "name": "initiate_podcast",
    "description": """Generates an audio podcast as a file
called podcast.mp3""",
    "parameters": {
      "type": "object",
      "properties": {
        "podcast_description": {
          "type": "string",
          "description": """A description of what type of podcast
the user wishes to create, including
topic and length""",
        }
      },
      "required": ["podcast_description"],
    },
  },
]

TOOL_FUNCTIONS = {"initiate_podcast": initiate_podcast}

print(f"Assistant: What podcast would you like me to create?\n")
user_input = input("User: ")

conversation_history = [
  {
    "role": "developer", 
    "content": """You are a podcast producer, creating
news-based and explainer podcasts for people on any topic they choose.
Here is the plan you should follow step by step to create a podcast:
<plan>
1. When the user describes the podcast they want, do not proceed to the
next step until you've obtained the following information:
* The topic of the podcast.
* How long the podcast should be. (For example, five minutes long.)
However, do not ask the user about the podcast style. Assume that the
podcast style is a single host reporting news and insight.
2. Next, create a simple summary describing the type of podcast the user
wants. Ensure that this summary includes the desired time length of the
podcast. For example, the summary might be: "A 3-minute podcast on the
latest news, insights, and updates in the field of quantum physics"
3. You have access to an initiate_podcast tool. Your next step is
to call the initiate_podcast tool, passing along your summary to it.
</plan>
"""
  },
  {"role": "assistant", "content": "How can I help you today?"}
]

def execute_tool_calls(tool_calls, history):
  if tool_calls:
    print(f"[Tools] Executing tool calls: {[tc.name for tc in tool_calls]}...")
  new_entries = [
    {
      "type": "function_call_output",
      "call_id": tool_call.call_id,
      "output": json.dumps({
        tool_call.name: TOOL_FUNCTIONS.get(tool_call.name)(**json.loads(tool_call.arguments))
      })
    }
    for tool_call in tool_calls
  ]
  history.extend(new_entries)

while user_input != "exit":
  conversation_history.append({"role": "user", "content": user_input})
  
  agent_iterator = AgentIterator(conversation_history, TOOLS)
  while agent_iterator.has_next():
    current_response = agent_iterator.next()
      
  print(f"\nAssistant: {current_response.output_text}\n")
  conversation_history.append({"role": "assistant", "content": current_response.output_text})
  user_input = input("User: ")