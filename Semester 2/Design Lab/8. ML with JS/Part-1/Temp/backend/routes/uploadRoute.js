const express = require("express");
const multer = require("multer");
const csv = require("csvtojson");
const { trainKNN } = require("../models/knnModel");

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() });

router.post("/", upload.single("dataset"), async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: "No file uploaded" });

    const fileContent = req.file.buffer.toString("utf-8");
    const dataset = await csv().fromString(fileContent);

    if (!dataset.length) {
      return res
        .status(400)
        .json({ error: "CSV file is empty or not formatted correctly." });
    }

    // Dynamically detect columns
    const headers = Object.keys(dataset[0]);
    if (headers.length < 2) {
      return res
        .status(400)
        .json({ error: "CSV must have at least two columns." });
    }

    // Assume first column is feature (X) and last column is label (Y)
    const featureColumn = headers[0]; // Example: "tweet"
    const labelColumn = headers[headers.length - 1]; // Example: "label"

    console.log(
      `Detected feature column: ${featureColumn}, label column: ${labelColumn}`
    );

    const texts = dataset.map((d) => String(d[featureColumn]).trim()); // Ensure features are strings
    const labels = dataset.map((d) => d[labelColumn]?.trim()); // Labels can be numbers or strings

    // Validate features
    if (!texts.every((t) => typeof t === "string" && t.length > 0)) {
      return res
        .status(400)
        .json({
          error:
            "Invalid feature data. Ensure feature column contains valid text.",
        });
    }

    // Train the model
    trainKNN(texts, labels);
    res.json({
      message: "Model trained successfully!",
      featureColumn,
      labelColumn,
    });
  } catch (error) {
    console.error("Training Error:", error.message);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
