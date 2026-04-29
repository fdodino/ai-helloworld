from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
llm = OpenAI()

user_input = input("Vamo' a jugar\n")
response = llm.responses.create(
    model="gpt-4.1-mini",temperature=0,
    input=f"Respond to the following like an argentinian soccer player: {user_input}"
)
print(response.output_text)