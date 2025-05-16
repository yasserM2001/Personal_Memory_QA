//Logic that interacts with Python, or external APIs
//Makes HTTP calls to your FastAPI model
// also this is for next phase after authentication and authorization is done
// services/pythonAPI.js
const axios = require("axios");
const FormData = require("form-data");
const { Readable } = require("stream");


const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || "http://localhost:8000";

// Upload images
async function uploadImages(userId, files) {
  const form = new FormData();
  form.append("user_id", userId);
  for (const file of files) {
    const stream = Readable.from(file.buffer);
    form.append("files", stream, file.originalname);
  }

  const response = await axios.post(`${FASTAPI_BASE_URL}/upload_images`, form, {
    headers: form.getHeaders(),
  });
  return response.data;
}

// Initialize memory
async function initializeMemory(userId, detectFaces = false) {
  const response = await axios.post(`${FASTAPI_BASE_URL}/initialize_user_memory`, {
    user_id: userId,
    detect_faces: detectFaces,
  }, {
    headers: { "Content-Type": "application/json" },
  });

  return response.data;
}

// Query memory
async function queryMemory(userId, query, method = "memory", detect_faces = false, topk = 5) {
  const response = await axios.post(`${FASTAPI_BASE_URL}/answer_query`, {
    user_id: userId,
    query: query,
    method: method,
    detect_faces: detect_faces,
    topk: topk,
  }, {
    headers: { "Content-Type": "application/json" },
  });
  if (response.status !== 200) {
    throw new Error(`Error querying memory: ${response.statusText}`);
  }
  return response.data;
}

// Change face tag
async function changeFaceTag(userId, faceTag, newFaceTag) {
  const response = await axios.post(`${FASTAPI_BASE_URL}/change_face_tag`, {
    user_id: userId,
    face_tag: faceTag,
    new_face_tag: newFaceTag,
  }, {
    headers: { "Content-Type": "application/json" },
  });
  if (response.status !== 200) {
    throw new Error(`Error changing face tag: ${response.statusText}`);
  }
  return response.data;
}

// Delete face tag
async function deleteFaceTag(userId, faceTag, detectFaces = false) {

  const response = await axios.post(`${FASTAPI_BASE_URL}/delete_face_tag`, {
    user_id: userId,
    face_tag: faceTag,
    detect_faces: detectFaces,
  }, {
    headers: { "Content-Type": "application/json" },
  });
  if (response.status !== 200) {
    throw new Error(`Error deleting face tag: ${response.statusText}`);
  }
  return response.data;
}

module.exports = {
  uploadImages,
  initializeMemory,
  queryMemory,
  changeFaceTag,
  deleteFaceTag,
};
