// the routes for the authentication controller
const express = require("express");
const router = express.Router();
const authController = require("../controllers/authController");


router.post("/register", authController.register);
router.post("/login", authController.login);
// router.get("/refresh", authController.refresh);
router.post("/logout", authController.logout);

module.exports = router;

