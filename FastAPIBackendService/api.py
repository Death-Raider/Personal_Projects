from werkzeug.utils import secure_filename
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import uvicorn

class URLRequest(BaseModel):
    url: str

UPLOAD_DIRECTORY = "files"

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def main():
    content = """
    <html>
    <body>
    <form action="/process_pdf/" enctype="multipart/form-data" method="post">
        <input name="files" type="file" multiple>
        <input type="submit">
    </form>
    </body>
    </html>
    """
    return content

@app.post("/process_pdf/")
async def upload_file(file: UploadFile = File(...)):
    # Save each file to the specified directory
    clean_file_name = secure_filename(file.filename)
    file_location = os.path.join(UPLOAD_DIRECTORY, clean_file_name)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    #TODO: Process PDF
    return {"file_names": clean_file_name, "message": "Files uploaded successfully"}

@app.post("/process_url")
async def process_url(request: URLRequest):
    url_received = request.url

    # TODO: Process URL
    return {"message": "URL processed successfully", "url": url_received}


@app.post("/process_query")
async def process_query(json_data: str = Query(..., description="JSON object as a query parameter")):
    import json
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in query parameter"}

    #TODO: Process JSON data
    return {"message": "JSON query processed successfully", "data": data}

if __name__ == '__main__':
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
