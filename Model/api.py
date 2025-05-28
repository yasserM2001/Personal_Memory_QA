from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body
from Preprocess.memory import Memory
from Query.query import QueryHandler
import shutil
import os
from pathlib import Path
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64
from pydantic import BaseModel
import json


DATA_FOLDER = "data"
EXTRACTED_FACES = "extracted_faces"
PROCESSED_FOLDER = os.path.join(DATA_FOLDER, "processed")
VECTOR_DB_FOLDER = os.path.join(DATA_FOLDER, "vector_db")
UPLOAD_FOLDER = "uploaded_images"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_FOLDER, exist_ok=True)

IMG_EXT_LIST = {"jpg", "jpeg", "png", "heic"}
VIDEO_EXT_LIST = {"mp4", "mov", "avi"}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InitMemoryRequest(BaseModel):
    user_id: str
    detect_faces: bool = False

class AnswerQueryRequest(BaseModel):
    user_id: str
    query: str
    method: str = "memory"
    detect_faces: bool = False
    topk: int = 5

class ChangeFaceTagRequest(BaseModel):
    user_id: str
    face_tag: str
    new_face_tag: str

class DeleteFaceTagRequest(BaseModel):
    user_id: str
    face_tag: str

@app.post("/upload_images")
async def upload_images(user_id: str = Form(...), files: List[UploadFile] = File(...)):
    user_folder = os.path.join(UPLOAD_FOLDER, user_id)
    Path(user_folder).mkdir(parents=True, exist_ok=True)

    uploaded_files = []

    for file in files:
        ext = file.filename.split(".")[-1].lower()

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
async def initialize_user_memory(payload: InitMemoryRequest):
    user_id = payload.user_id
    detect_faces = payload.detect_faces

    uploaded_folder = os.path.join(UPLOAD_FOLDER, user_id)
    processed_folder = os.path.join(PROCESSED_FOLDER, user_id)
    vector_db_folder = os.path.join(VECTOR_DB_FOLDER, user_id)

    if not os.path.exists(uploaded_folder) or not os.listdir(uploaded_folder):
        raise HTTPException(status_code=400, detail="No images found for this user.")

    Path(processed_folder).mkdir(parents=True, exist_ok=True)
    Path(vector_db_folder).mkdir(parents=True, exist_ok=True)

    memory = Memory(raw_folder=uploaded_folder,
                    processed_folder=processed_folder,
                    vector_db_folder=vector_db_folder,
                    detect_faces=detect_faces)
    memory.preprocess()
    memory.augment()

    extracted_faces_folder = os.path.join(processed_folder, "extracted_faces")
    grouped_faces_file = os.path.join(processed_folder, "grouped_faces", "grouped_faces.json") 

    extracted_faces = []
    if detect_faces and os.path.exists(extracted_faces_folder):
        # read grouped faces from JSON file
        if os.path.exists(grouped_faces_file):
            with open(grouped_faces_file, "r") as f:
                grouped_faces = json.load(f)
            for face_tag, face_files in grouped_faces.items():
                face_file = face_files[0]
                face_path = os.path.join(extracted_faces_folder, face_file)
                if os.path.exists(face_path):
                    with open(face_path, "rb") as f:
                        encoded_image = base64.b64encode(f.read()).decode("utf-8")
                        extracted_faces.append({
                            "filename": face_file,
                            "face_tag": face_tag,
                            "base64_image": encoded_image
                        })

    return JSONResponse(content={
        "message": "User memory initialized successfully.",
        "processed_folder": processed_folder,
        "vector_db_folder": vector_db_folder,
        "memory": memory.memory_content_processed,
        "extracted_faces": extracted_faces
    })

@app.post("/answer_query")
async def answer_query(payload: AnswerQueryRequest):
    user_id = payload.user_id
    query = payload.query
    method = payload.method
    detect_faces = payload.detect_faces
    topk = payload.topk

    user_processed_folder = os.path.join(PROCESSED_FOLDER, user_id)
    user_vector_db_folder = os.path.join(VECTOR_DB_FOLDER, user_id)

    if not os.path.exists(user_processed_folder) or not os.path.exists(user_vector_db_folder):
        raise HTTPException(status_code=400, detail="User memory not found. Please initialize first.")

    memory = Memory(raw_folder=os.path.join(UPLOAD_FOLDER, user_id),
                    processed_folder=user_processed_folder,
                    vector_db_folder=user_vector_db_folder,
                    detect_faces=detect_faces)
    try:
        memory.load_processed_memory()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    query_handler = QueryHandler(memory, detect_faces=detect_faces)

    if method == "memory":
        result = query_handler.query_memory(query, topk=topk, llm="gemini")
    elif method == "rag":
        result = query_handler.query_rag(query, topk=topk, llm="gemini")
    else:
        raise HTTPException(status_code=400, detail="Invalid query method. Use 'memory' or 'rag'.")

    return {
        "user_id": user_id,
        "query": query,
        "method": method,
        "response": result
    }

@app.post("/change_face_tag")
async def change_face_tag(payload: ChangeFaceTagRequest):
    user_id = payload.user_id
    face_tag = payload.face_tag
    new_face_tag = payload.new_face_tag

    user_processed_folder = os.path.join(PROCESSED_FOLDER, user_id)
    user_vector_db_folder = os.path.join(VECTOR_DB_FOLDER, user_id)

    if not os.path.exists(user_processed_folder):
        raise HTTPException(status_code=400, detail="User memory not found. Please initialize first.")

    memory = Memory(raw_folder=os.path.join(UPLOAD_FOLDER, user_id),
                    processed_folder=user_processed_folder,
                    vector_db_folder=user_vector_db_folder,
                    detect_faces=True)
    try:
        memory.load_processed_memory()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    done = memory.change_face_tag(face_tag, new_face_tag)

    if done:
        return {"message": f"Face tag '{face_tag}' changed to '{new_face_tag}' successfully."}
    else:
        return {"message": f"Failed to change the face tag [{face_tag}]"}

@app.post("/delete_face_tag")
async def delete_face_tag(payload: DeleteFaceTagRequest):
    user_id = payload.user_id
    face_tag = payload.face_tag

    user_processed_folder = os.path.join(PROCESSED_FOLDER, user_id)
    user_vector_db_folder = os.path.join(VECTOR_DB_FOLDER, user_id)

    if not os.path.exists(user_processed_folder):
        raise HTTPException(status_code=400, detail="User memory not found. Please initialize first.")

    memory = Memory(raw_folder=os.path.join(UPLOAD_FOLDER, user_id),
                    processed_folder=user_processed_folder,
                    vector_db_folder=user_vector_db_folder,
                    detect_faces=True)
    try:
        memory.load_processed_memory()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    done = memory.delete_face_tag(face_tag)
    if done:
        return {"message": f"Face tag '{face_tag}' deleted successfully."}
    else:
        return {"message": f"Failed to delete the face tag [{face_tag}]"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
