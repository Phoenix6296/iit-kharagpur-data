document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("file_input").files[0];
  const modelSelect = document.getElementById("model_select");
  const selectedModel = modelSelect.value;

  if (!fileInput) {
    alert("Please select a CSV file.");
    return;
  }

  if (!selectedModel) {
    alert("Please select a model before training.");
    return;
  }

  const formData = new FormData();
  formData.append("dataset", fileInput);

  try {
    let response = await fetch("http://localhost:3000/upload", {
      method: "POST",
      body: formData,
    });

    let data = await response.json();
    if (!response.ok) {
      alert("Error: " + data.error);
      return;
    }
    console.log("Upload successful:", data.message);

    response = await fetch(`http://localhost:3000/train/${selectedModel}`, {
      method: "POST",
    });

    data = await response.json();
    if (!response.ok) {
      alert("Training Error: " + data.error);
      return;
    }

    console.log("Training response:", data);
  } catch (error) {
    console.error("Error:", error);
    alert(error);
  }
});

// Prediction function (To be implemented)
async function predictText() {
  const inputText = document.getElementById("input_text").value.trim();
  const modelSelect = document.getElementById("model_select");
  const selectedModel = modelSelect.value;

  if (!inputText) {
    alert("Please enter text for prediction.");
    return;
  }

  if (!selectedModel) {
    alert("Please select a model before predicting.");
    return;
  }

  try {
    let response = await fetch(
      `http://localhost:3000/predict/${selectedModel}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: inputText }),
      }
    );

    let data = await response.json();
    if (!response.ok) {
      alert("Prediction Error: " + data.error);
      return;
    }

    document.getElementById(
      "output"
    ).innerText = `Prediction: ${data.prediction}`;
  } catch (error) {
    console.error("Error:", error);
    alert(error);
  }
}
