// // the routes for the model controller
const express = require("express");
const router = express.Router();
const multer = require("multer");
const upload = multer({ storage: multer.memoryStorage() });

const modelController = require("../controllers/modelController");


// Accept multiple files with the form key name 'files'
router.post("/upload", upload.array("files"), modelController.uploadHandler);
router.post("/initialize", modelController.initializeHandler);
router.post("/query", modelController.queryHandler);
router.post("/change_face_tag", modelController.changeFaceTagHandler);
router.post("/delete_face_tag", modelController.deleteFaceTagHandler);

module.exports = router;
