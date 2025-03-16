const KNN = require("ml-knn");

function trainModel(dataset) {
  const features = dataset.map((d) => [parseFloat(d.text) || 0]); // Convert to number array
  const labels = dataset.map((d) =>
    isNaN(d.label) ? d.label : parseInt(d.label, 10)
  );

  if (!features.length || !labels.length) {
    throw new Error("Dataset is empty or improperly formatted.");
  }

  const knn = new KNN(features, labels, { k: 3 });
  return { message: "KNN model trained successfully!" };
}

module.exports = { trainModel };
