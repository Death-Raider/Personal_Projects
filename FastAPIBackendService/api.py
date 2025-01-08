from werkzeug.utils import secure_filename
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import uvicorn
import numpy as np
import json

from pdf_handler import extract_and_clean_text_from_pdf, clean_text, gen_id
from url_handler import extract_text_from_url, start_browser
from vec_embedding_transformer import Model
from chat_handler import vectorize_database, vectorize_database_search, sample_dataset_for_db

class URLRequest(BaseModel):
    url: str

app = FastAPI()
model = Model()
model.loadModel("paraphrase-MiniLM-L3-v2")

@app.get("/", response_class=HTMLResponse)
async def main():
    content = """
    <html>
    <body>
    <form action="/process_pdf/" enctype="multipart/form-data" method="post">
        <input name="file" type="file" multiple>
        <input type="submit">
    </form>
    </body>
    </html>
    """
    return content

@app.post("/process_pdf/")
async def upload_file(file: UploadFile = File(...)):
    UPLOAD_DIRECTORY = "incoming_files"
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    clean_file_name = secure_filename(file.filename)
    file_location = UPLOAD_DIRECTORY+"/"+clean_file_name
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    out = extract_and_clean_text_from_pdf(file_location)

    if isinstance(out['id'], str):
        with open(f"database/{out['id']}.txt",'w') as f:
            f.write(out['content'])
        return {"chat_id": out['id'], "message": "PDF content processed and stored successfully"}
    else:
        return {"chat_id": out['id'], "message": "An error occured" }

@app.post("/process_url")
async def process_url(request: Request):
    data = await request.json()
    print(data)
    url_received = data['url']
    print(url_received)

    brow = start_browser()
    text = extract_text_from_url(brow,url_received)
    # text = clean_text(dirty_text)

    ID = gen_id()
    with open(f"database/{ID}.txt",'w', encoding='utf-8') as f:
        f.write(text)

    return {"chat_id": ID, "message": "URL content processed and stored successfully"}


@app.post("/process_query")
async def process_query(request: Request):
    try:
        data:dict = await request.json()
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in query parameter"}

    data_val = list(data.values())
    print(data_val)
    with open(f"database/{data_val[0]}.txt",'r',encoding='utf-8') as f:
        text = f.read()
    chunked_sentence_db = sample_dataset_for_db(text)

    database = np.array(chunked_sentence_db)
    print("db created")
    vector_db = vectorize_database(model, database)
    print("vectorized db")
    index = vectorize_database_search(model,data_val[1],vector_db)
    print(index)
    response = database[index].tolist()
    print(response)
    return {"response": response[0]}

if __name__ == '__main__':
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
