const { RandomForestClassifier } = require("ml-random-forest");

function trainModel(dataset) {
  try {
    const features = dataset.map((d) => [parseFloat(d.text) || 0]);
    const labels = dataset.map((d) =>
      isNaN(d.label) ? d.label : parseInt(d.label, 10)
    );

    if (!features.length || !labels.length) {
      throw new Error("Dataset is empty or improperly formatted.");
    }

    const model = new RandomForestClassifier({
      nEstimators: 10,
      maxDepth: 10,
      minSamplesSplit: 2,
      minSamplesLeaf: 1,
      maxFeatures: "sqrt",
      randomState: 42,
    });
    model.train(features, labels);

    return { message: "Random Forest model trained successfully!" };
  } catch (error) {
    console.error("Random Forest Training Error:", error.message);
    return { error: error.message };
  }
}
module.exports = { trainModel };
