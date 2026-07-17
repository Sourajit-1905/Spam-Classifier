const API_URL = "https://your-backend-service.onrender.com/predict"; // update after backend deploy

const checkBtn = document.getElementById('checkBtn');
const messageInput = document.getElementById('messageInput');
const resultBox = document.getElementById('resultBox');
const resultLabel = document.getElementById('resultLabel');
const resultScore = document.getElementById('resultScore');

checkBtn.addEventListener('click', async () => {
    const message = messageInput.value.trim();

    if (!message) {
        resultLabel.textContent = "Please enter a message first.";
        resultScore.textContent = "";
        resultBox.className = "result-box";
        return;
    }

    resultLabel.textContent = "Checking...";
    resultScore.textContent = "";
    resultBox.className = "result-box";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        if (data.prediction === 1) {
            resultLabel.textContent = "🚨 SPAM";
            resultBox.className = "result-box spam";
        } else {
            resultLabel.textContent = "✅ NOT SPAM";
            resultBox.className = "result-box not-spam";
        }

        resultScore.textContent = `Confidence: ${(data.probability * 100).toFixed(2)}%`;

    } catch (error) {
        resultLabel.textContent = "Error connecting to server.";
        resultScore.textContent = "";
        resultBox.className = "result-box";
    }
});