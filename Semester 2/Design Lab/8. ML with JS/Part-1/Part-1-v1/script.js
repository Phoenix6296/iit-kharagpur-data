document.getElementById("uploadForm").addEventListener("submit", function (e) {
  e.preventDefault();
  const formData = new FormData(this);
  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("accuracy").textContent = data.accuracy;
      document.getElementById("precision").textContent = data.precision;
      document.getElementById("recall").textContent = data.recall;
      document.getElementById("resultsContainer").style.display = "block";
    })
    .catch((error) => console.error("Error:", error));
});

document.getElementById("predictBtn").addEventListener("click", function () {
  const text = document.getElementById("predictionInput").value;
  if (!text) {
    alert("Please enter text to predict");
    return;
  }
  fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: text }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("predictionClass").textContent = data.label;
      document.getElementById("predictionResult").style.display = "block";
    })
    .catch((error) => console.error("Error:", error));
});
