from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from Preprocess.memory import Memory
from Query.query import QueryHandler
import shutil
import os
from pathlib import Path
from typing import List


DATA_FOLDER = "data"
PROCESSED_FOLDER = os.path.join(DATA_FOLDER, "processed")
VECTOR_DB_FOLDER = os.path.join(DATA_FOLDER, "vector_db")
UPLOAD_FOLDER = "uploaded_images"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_FOLDER, exist_ok=True)

IMG_EXT_LIST = {"jpg", "jpeg", "png", "heic"}
VIDEO_EXT_LIST = {"mp4", "mov", "avi"}

app = FastAPI()

@app.post("/upload_images")
async def upload_images(user_id: str = Form(...), files: List[UploadFile] = File(...)):
    """Handles multiple image uploads and saves them to the system."""
    user_folder = os.path.join(UPLOAD_FOLDER, user_id)
    Path(user_folder).mkdir(parents=True, exist_ok=True)

    uploaded_files = []

    for file in files:
        ext = file.filename.split(".")[-1].lower()

        # Validate file type
        if ext not in IMG_EXT_LIST and ext not in VIDEO_EXT_LIST:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type {file.filename}. Allowed: jpg, jpeg, png, heic, mp4, mov, avi."
            )

        file_path = os.path.join(user_folder, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append({"filename": file.filename, "filepath": file_path})

    return {
        "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
        "user_folder": user_folder,
        "uploaded_files": uploaded_files
        }

@app.post("/initialize_user_memory")
async def initialize_user_memory(user_id: str = Form(...)):
    """Initializes user memory and processes their uploaded images."""
    uploaded_folder = os.path.join(UPLOAD_FOLDER, user_id)
    processed_folder = os.path.join(PROCESSED_FOLDER, user_id)
    vector_db_folder = os.path.join(VECTOR_DB_FOLDER, user_id)

    # Check if the user has uploaded any images
    if not os.path.exists(uploaded_folder) or not os.listdir(uploaded_folder):
        raise HTTPException(status_code=400, detail="No images found for this user.")

    # Ensure processed folder exists
    Path(processed_folder).mkdir(parents=True, exist_ok=True)
    Path(vector_db_folder).mkdir(parents=True, exist_ok=True)

    # Initialize Memory and Process Data
    memory = Memory(raw_folder=uploaded_folder,
                    processed_folder=processed_folder, 
                    vector_db_folder=vector_db_folder)
    memory.preprocess()
    memory.augment()

    return {
        "message": "User memory initialized successfully.",
        "processed_folder": processed_folder,
        "vector_db_folder": vector_db_folder,
        "memory": memory.memory_content_processed
        }

@app.post("/answer_query")
async def answer_query(user_id: str, query: str, method: str = "memory"):
    """
    Answers user queries based on their processed memory.
    method: "memory" -> Uses query_memory (default)
            "rag" -> Uses query_rag
    """
    user_processed_folder = os.path.join(PROCESSED_FOLDER, user_id)
    user_vector_db_folder = os.path.join(VECTOR_DB_FOLDER, user_id)
    
    # Check if the user has initialized memory
    if not os.path.exists(user_processed_folder) or not os.path.exists(user_vector_db_folder):
        raise HTTPException(status_code=400, detail="User memory not found. Please initialize first.")

    # Load the user's memory without reprocessing
    memory = Memory(raw_folder=os.path.join(UPLOAD_FOLDER, user_id), 
                    processed_folder=user_processed_folder,
                    vector_db_folder=user_vector_db_folder
                    )
    try:
        memory.load_processed_memory()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Initialize QueryHandler
    query_handler = QueryHandler(memory)

    # Use the appropriate query method
    if method == "memory":
        result = query_handler.query_memory(query)
    elif method == "rag":
        result = query_handler.query_rag(query)
    else:
        raise HTTPException(status_code=400, detail="Invalid query method. Use 'memory' or 'rag'.")

    return {
        "user_id": user_id,
        "query": query,
        "method": method,
        "response": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
