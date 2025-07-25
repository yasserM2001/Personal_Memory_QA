require("dotenv").config();
const express = require("express");
const app = express();
const connectDB = require("./config/dbConn");
const mongoose = require("mongoose");
const cookieParser = require("cookie-parser");
const cors = require("cors");
const path = require("path");
const corsOptions = require("./config/corsOptions");
const PORT = process.env.PORT || 5500;

connectDB();

app.use(cors(corsOptions));
app.use(cookieParser());
app.use(express.json());

app.use('/photos', express.static(path.join(__dirname, 'photos')));
// app.use('/', require('./routes/root'));
app.use('/auth', require('./routes/authRoutes'));
// app.use('/users', require('./routes/userRoutes'));
app.use("/model", require("./routes/modelRoutes"));

//--------------------------------> fee error 8areeb hna
// app.all('*', (req, res) => {
//   res.status(404);
//   if (req.accepts('html')) {
//     res.sendFile(path.join(__dirname, 'views', '404.html'));
//   } else if (req.accepts('json')) {
//     res.json({ message: '404 Not Found' });
//   } else {
//     res.type('txt').send('404 Not Found');
//   }
// });
mongoose.connection.once("open", () => {
  console.log("Connected to MongoDB");
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
});
mongoose.connection.on("error", (err) => {
  console.log(err);
});
