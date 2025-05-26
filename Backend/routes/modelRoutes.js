// // the routes for the model controller
const express = require("express");
const router = express.Router();
const multer = require("multer");
const upload = multer({ storage: multer.memoryStorage() });
const verfyToken = require("../middleware/verifyJWT");
const modelController = require("../controllers/modelController");


// Accept multiple files with the form key name 'files'
router.post("/upload", upload.array("files"),verfyToken,modelController.uploadHandler);
router.post("/initialize",verfyToken,modelController.initializeHandler);
router.post("/query",verfyToken,modelController.queryHandler);
router.post("/change_face_tag",verfyToken,modelController.changeFaceTagHandler);
router.post("/delete_face_tag",verfyToken,modelController.deleteFaceTagHandler);

module.exports = router;
