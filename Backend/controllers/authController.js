// functions for authintication ex: login, register, logout
const User = require("../models/User");
const bcrypt = require("bcrypt");
const generateToken = require("../utils/generateToken");
const jwt = require("jsonwebtoken");

const register = async (req, res) => {
  try {
    const { first_name, last_name, email, password, confirm_password } =
      req.body;

    // Check all fields are present
    if (!first_name || !last_name || !email || !password || !confirm_password) {
      return res.status(400).json({ message: "All fields are required" });
    }

    // Check password match
    if (password !== confirm_password) {
      return res.status(400).json({ message: "Passwords do not match" });
    }

    // Check for existing user
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(409).json({ message: "User already exists" });
    }

    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create new user
    const newUser = await User.create({
      first_name,
      last_name,
      email,
      password: hashedPassword,
    });

    // Respond with created user info
    return res.status(201).json({
      message: "User registered successfully",
      user_num: newUser.user_num,
      email: newUser.email,
      first_name: newUser.first_name,
      last_name: newUser.last_name,
    });
  } catch (error) {
    console.error("Registration error:", error);
    return res.status(500).json({ message: "Server error" });
  }
};

const login = async (req, res) => {
  const { email, password } = req.body;

  // Check for missing fields
  if (!email || !password) {
    return res.status(400).json({ message: "Email and password required" });
  }

  try {
    // Find user by email
    const user = await User.findOne({ email }).exec();
    if (!user) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    // Compare password
    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    // Generate access token
    const accessToken = generateToken.generateToken(user._id);

    // // Optional: Generate refresh token
   //const refreshToken = generateToken.generateRefreshToken(user._id);

    // Optional: Set refresh token in secure cookie
    res.cookie("accessToken", accessToken, {
      httpOnly: true,
      secure: true, // only true in production with HTTPS
      sameSite: "Strict",
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    // Return token to frontend
    return res.json({
      message: "Logged in successfully",
      token: accessToken,
      user: {
        user_num: user.user_num,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
      },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Server error" });
  }
};


const logout = async (req, res) => {
  try {
    const cookies = req.cookies;

    if (!cookies?.accessToken)
      return res.sendStatus(204);

    // Clear the access token cookie
    res.clearCookie("accessToken", {
      httpOnly: true,
      secure: true, // set to true in production with HTTPS
      sameSite: "Strict",
      path: "/",
    });

    return res.status(200).json({ message: "Logged out successfully" });
  } catch (error) {
    console.error("Logout error:", error);
    return res.status(500).json({ message: "Server error" });
  }
};

const refresh = (req, res) => {
  const cookies = req.cookies;

  if (!cookies?.refreshToken) {
    return res.status(401).json({ message: 'Unauthorized' });
  }

  const refreshToken = cookies.refreshToken;

  jwt.verify(
    refreshToken,
    process.env.REFRESH_TOKEN_SECRET,
    async (err, decoded) => {
      if (err) {
        return res.status(403).json({ message: 'Forbidden' });
      }

      try {
        const foundUser = await User.findById(decoded.id).exec();

        if (!foundUser) {
          return res.status(401).json({ message: 'Unauthorized' });
        }

        const accessToken = generateToken.generateToken(foundUser._id);
        return res.json({ accessToken });
      } catch (error) {
        console.error("Refresh token error:", error);
        return res.status(500).json({ message: "Server error" });
      }
    }
  );
};


module.exports = {
  register,
  login,
  refresh,
  logout,
};
