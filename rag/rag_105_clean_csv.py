import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / 'orm_traces.csv'
OUTPUT_FILE = SCRIPT_DIR / 'orm_traces_clean.csv'

def clean_newlines(text):
    """Reemplaza saltos de línea por espacios para que Google Sheets los interprete correctamente"""
    if isinstance(text, str):
        return text.replace('\n', ' ').replace('\r', ' ')
    return text

try:
    with INPUT_FILE.open('r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        with OUTPUT_FILE.open('w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                # Limpiar saltos de línea en todos los campos
                cleaned_row = {k: clean_newlines(v) for k, v in row.items()}
                writer.writerow(cleaned_row)
    
    print(f"✅ CSV limpiado exitosamente")
    print(f"📁 Archivo guardado en: {OUTPUT_FILE.absolute()}")
    
except FileNotFoundError as e:
    print(f"❌ Error: {e}", file=__import__('sys').stderr)
    __import__('sys').exit(1)
