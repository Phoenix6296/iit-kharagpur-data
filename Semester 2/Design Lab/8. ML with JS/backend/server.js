const express = require("express");
const cors = require("cors");

const uploadRoute = require("./routes/uploadRoute");
const predictRoute = require("./routes/predictRoute");

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// API Routes
app.use("/api/upload", uploadRoute);
app.use("/api/predict", predictRoute);

app.listen(PORT, () =>
  console.log(`Server running on http://localhost:${PORT}`)
);
