//handles calls to Python model API
// is connected with pythonAPI.js then and it will be done after the authentication and authorization is done
const path = require("path");
const pythonApi = require("../services/pythonAPI");
const fs = require('fs');

const saveFacesToDisk = (faces, userId) => {
  const folderPath = path.join('saved_faces', userId);
  const savedPaths = [];
  
  if (!fs.existsSync(folderPath)) {
    fs.mkdirSync(folderPath, { recursive: true });
  }

  faces.forEach(face => {
    const filePath = path.join(folderPath, face.filename);
    const base64Data = face.base64_image.replace(/^data:image\/\w+;base64,/, "");
    fs.writeFileSync(filePath, Buffer.from(base64Data, 'base64'));
   const relativePath = path.join('saved_faces', userId, face.filename);
    savedPaths.push(relativePath);
  });

  return savedPaths;
};

const uploadHandler = async (req, res) => {
  try {
    const userId = req.body.user_id;
    if (!userId) return res.status(400).json({ error: "Missing user_id" });

    const files = req.files;
    console.log("Files received:", files);
    if (!files || files.length === 0) {
      return res.status(400).json({ error: "No files uploaded" });
    }

    // Call the function from pythonAPI.js
    const result = await pythonApi.uploadImages(userId, files);

    res.json(result);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
};

const initializeHandler = async (req, res) => {
  try {
    const { user_id, detect_faces } = req.body;

    if (!user_id) {
      return res.status(400).json({ error: "Missing user_id" });
    }

    // Call the function from pythonAPI.js
    const result = await pythonApi.initializeMemory(user_id, detect_faces);
    if (result.extracted_faces && result.extracted_faces.length > 0) {
      savedImagePaths = saveFacesToDisk(result.extracted_faces, user_id);      
    }
    res.json({
      ...result,
      saved_image_paths: savedImagePaths
    });    
  } catch (error) {
    console.error("Error in initializeHandler:", error);
    res.status(500).json({ error: error.message });
  }
};

const queryHandler = async (req, res) => {
  try {
    // Add validation for req.body
    if (!req.body) {
      return res.status(400).json({ error: "Request body is missing" });
      
    }

    const { user_id, query, method, detect_faces, topk } = req.body;

    // Add validation for required fields
    if (!user_id || !query) {
      return res
        .status(400)
        .json({
          error: "Missing required fields (user_id and query are required)",
        });
    }

    const result = await pythonApi.queryMemory(
      user_id,
      query,
      method || "memory",
      detect_faces || false,
      topk || 5
    );
    res.json(result);
  } catch (error) {
    console.error("Error in queryHandler:", error);
    res.status(500).json({ error: error.message });
  }
};

const changeFaceTagHandler = async (req, res) => {
  try {
    const { user_id, face_tag, new_face_tag } = req.body;

    if (!user_id || !face_tag || !new_face_tag) {
      return res
        .status(400)
        .json({ error: "Missing required fields (user_id, face_tag, new_face_tag)" });
    }

    const result = await pythonApi.changeFaceTag(
      user_id,
      face_tag,
      new_face_tag
    );
    res.json(result);
  } catch (error) {
    console.error("Error in changeFaceTagHandler:", error);
    res.status(500).json({ error: error.message });
  }
};

const deleteFaceTagHandler = async (req, res) => {
  try {
    const { user_id, face_tag } = req.body;

    if (!user_id || !face_tag) {
      return res
        .status(400)
        .json({ error: "Missing required fields (user_id and face_tag)" });
    }

    const result = await pythonApi.deleteFaceTag(
      user_id,
      face_tag,
    );
    res.json(result);
  } catch (error) {
    console.error("Error in deleteFaceTagHandler:", error);
    res.status(500).json({ error: error.message });
  }
}
module.exports = {
  uploadHandler,
  initializeHandler,
  queryHandler,
  changeFaceTagHandler,
  deleteFaceTagHandler,
};