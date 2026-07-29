const API_URL = "/predict";

const checkBtn = document.getElementById('checkBtn');
const messageInput = document.getElementById('messageInput');
const resultBox = document.getElementById('resultBox');
const resultLabel = document.getElementById('resultLabel');
const resultScore = document.getElementById('resultScore');

// Maps 0-100 safety score to hue: 0 (red) → 120 (green)
// Each of the 20 bands (5% wide) gets a proportional hue step
function applyScoreColor(safetyScore) {
    const hue = Math.round(safetyScore * 1.2); // 0→0 (red), 100→120 (green)
    resultBox.style.setProperty('--result-hue', hue);
}

function resetBox() {
    resultBox.className = 'result-box';
    resultBox.style.removeProperty('--result-hue');
}

checkBtn.addEventListener('click', async () => {
    const message = messageInput.value.trim();

    if (!message) {
        resultLabel.textContent = "Please enter a message first.";
        resultScore.textContent = "";
        resultBox.className = "result-box warning";

        resultBox.classList.remove('shake');
        void resultBox.offsetWidth; // force reflow so animation replays
        resultBox.classList.add('shake');

        return;
    }

    resultLabel.textContent = "Checking...";
    resultScore.textContent = "";
    resetBox();

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Apply gradual hue based on safety score across 20 bands
        applyScoreColor(data.safety_score);

        resultLabel.textContent = data.prediction === 1 ? "🚨 SPAM" : "✅ NOT SPAM";
        resultScore.textContent = `${data.safety_score}% — ${data.confidence_label}`;

    } catch (error) {
        resultLabel.textContent = "Error connecting to server.";
        resultScore.textContent = "";
        resetBox();
    }
});