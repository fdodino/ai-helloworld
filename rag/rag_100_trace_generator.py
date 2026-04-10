import csv
import json
import sys
from pathlib import Path
from rag_40_chatbot_enhanced import search_all_docs, rag_results_to_documentation, system_prompt, user_prompt, llm_response

# Resolve paths relative to script location
SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / 'orm_queries.csv'
OUTPUT_FILE = SCRIPT_DIR / 'orm_traces.csv'
ASSISTANT_GREETING = "¿Cómo puedo ayudarte?"

# Check if input file exists
if not INPUT_FILE.exists():
    print(f"❌ Error: Input file not found at '{INPUT_FILE.absolute()}'", file=sys.stderr)
    sys.exit(1)

try:
    infile = INPUT_FILE.open('r')
    outfile = OUTPUT_FILE.open('w', newline='', encoding='utf-8')
except FileNotFoundError as e:
    print(f"❌ Error: Failed to open file - {e}", file=sys.stderr)
    sys.exit(1)

with infile, outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=["Query Topic", "User Query", "History", "AI Response"])
    writer.writeheader()

    for row_index, row in enumerate(reader, 1):
        history = [
            system_prompt(),
            {"role": "assistant", "content": ASSISTANT_GREETING}
        ]
        results = search_all_docs(row['User Query'])
        documentation = rag_results_to_documentation(results)
        history.append(user_prompt(documentation, row['User Query']))
        response = llm_response(history)

        writer.writerow({
            "Query Topic": row['Query Topic'],
            "User Query": row['User Query'],
            "History": json.dumps(history),
            "AI Response": response.choices[0].message.content
        })
        print(f"Query {row_index} completed")