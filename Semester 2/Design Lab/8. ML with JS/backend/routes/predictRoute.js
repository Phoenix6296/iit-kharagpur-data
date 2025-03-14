const express = require("express");
const { predictKNN } = require("../models/knnModel");

const router = express.Router();

router.post("/", (req, res) => {
    try {
        const { text } = req.body;
        const prediction = predictKNN(text);
        res.json({ prediction });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
