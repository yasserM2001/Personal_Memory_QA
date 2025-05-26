// here we are going to verify the JWT token
const jwt = require("jsonwebtoken");


const verifyJWT = (req, res, next) => {
  const token = req.cookies.accessToken;

  if (!token) {
    return res.status(401).json({ message: "No token. Authorization denied." });
  }

  try {
    const decoded = jwt.verify(token, process.env.ACCESS_TOKEN_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(403).json({ message: "Unauthorized: Invalid or expired token." });
  }
};
module.exports = verifyJWT;
