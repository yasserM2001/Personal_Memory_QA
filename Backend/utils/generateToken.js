// extra for now can be removed later
// here we can create jwt token for user
const jwt = require("jsonwebtoken");

const generateToken = (user_id) => {
  return jwt.sign(
    {
      id: user_id,
    },
    process.env.ACCESS_TOKEN_SECRET,
    { expiresIn: "1h" }
  );
};


module.exports = { generateToken }; 