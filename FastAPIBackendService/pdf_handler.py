import PyPDF2
import re
import os
import random
import string

def extract_and_clean_text_from_pdf(pdf_file_name: str) -> dict[str,str]:
    try:
        with open(pdf_file_name, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            cleaned_text = clean_text(text)
            return {'id':gen_id(), 'content': cleaned_text}
    except FileNotFoundError:
        return {'id':-1,'content':f"Error: The file '{pdf_file_name}' was not found."}
    except Exception as e:
        return {'id':-1, 'content':f"An error occurred: {e}"}

def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"(\n\s*)+", "\n", text)
    text = re.sub(r"(\n )|(\n)", " ", text)
    text = text.strip()
    return text

def gen_id() -> str:
    directory = "database"  # Directory where the file IDs are stored
    if not os.path.exists(directory):
        os.makedirs(directory)
    while True:
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        if not os.path.exists(os.path.join(directory, random_id)):
            return random_id