const API_URL = "/predict";

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
        resultBox.className = "result-box warning";

        // trigger shake
        resultBox.classList.remove('shake'); // reset in case it's already applied
        void resultBox.offsetWidth; // force reflow so animation replays
        resultBox.classList.add('shake');

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

        resultScore.textContent = `${data.safety_score}% — ${data.confidence_label}`;

    } catch (error) {
        resultLabel.textContent = "Error connecting to server.";
        resultScore.textContent = "";
        resultBox.className = "result-box";
    }
});