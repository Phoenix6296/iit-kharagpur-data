const { DecisionTreeClassifier } = require("ml-cart");

function trainModel(dataset) {
  try {
    // Ensure all feature values are numbers and filter invalid data
    const filteredDataset = dataset.filter(
      (d) => !isNaN(parseFloat(d.text)) && !isNaN(parseInt(d.label, 10))
    );

    if (filteredDataset.length === 0) {
      throw new Error("Dataset is empty or contains only invalid entries.");
    }

    const features = filteredDataset.map((d) => [parseFloat(d.text)]);
    const labels = filteredDataset.map((d) => parseInt(d.label, 10));

    if (features.length !== labels.length) {
      throw new Error("Mismatch between feature and label counts.");
    }

    const model = new DecisionTreeClassifier({
      maxDepth: 10,
      minSamplesSplit: 2,
      minSamplesLeaf: 1,
      maxFeatures: "sqrt",
      randomState: 42,
    });

    model.train(features, labels);

    return { message: "Decision Tree model trained successfully!" };
  } catch (error) {
    console.error("Decision Tree Training Error:", error.message);
    return { error: error.message };
  }
}

module.exports = { trainModel };
