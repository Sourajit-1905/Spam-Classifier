# SMS Spam Detector

A production-ready, full-stack machine learning web application that classifies SMS messages as **Spam** or **Not Spam** in real time using Natural Language Processing and an ensemble Machine Learning model — deployed on Render.

---

## Live Demo

[I will add live URL here]

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [The Problem](#the-problem)
3. [Dataset](#dataset)
4. [Project Journey](#project-journey)
   - [Phase 1: Exploratory Data Analysis](#phase-1-exploratory-data-analysis)
   - [Phase 2: Text Preprocessing](#phase-2-text-preprocessing)
   - [Phase 3: Feature Engineering](#phase-3-feature-engineering)
   - [Phase 4: Model Building & Evaluation](#phase-4-model-building--evaluation)
   - [Phase 5: Threshold Tuning](#phase-5-threshold-tuning)
   - [Phase 6: Model Serialization](#phase-6-model-serialization)
   - [Phase 7: Backend Development](#phase-7-backend-development)
   - [Phase 8: Frontend Development](#phase-8-frontend-development)
   - [Phase 9: Testing](#phase-9-testing)
   - [Phase 10: Deployment](#phase-10-deployment)
5. [Tech Stack](#tech-stack)
6. [Project Structure](#project-structure)
7. [Local Setup](#local-setup)
8. [API Reference](#api-reference)
9. [Confidence Score System](#confidence-score-system)
10. [Running Tests](#running-tests)
11. [Model Performance](#model-performance)
12. [Author](#author)
13. [License](#license)

---

## Project Overview

SMS Spam Detector is a complete end-to-end machine learning project that takes raw SMS text as input, processes it through a trained NLP pipeline, and returns a real-time spam/not-spam classification — along with a 20-band safety confidence score that explains *how confident* the model is in its prediction.

The project covers the complete ML lifecycle: raw data → EDA → preprocessing → feature engineering → model training → evaluation → serialization → API development → frontend design → testing → cloud deployment.

---

## The Problem

SMS spam is a persistent global problem. Unsolicited messages range from annoying promotional content to dangerous phishing attempts designed to steal personal and financial information. An automated, reliable classifier that runs in real time can protect users from these threats without requiring manual filtering.

The challenge in this domain is that:
- Spam messages are deliberately crafted to look legitimate
- The dataset is **imbalanced** (far more ham than spam)
- A high **false negative rate** (missing real spam) is more dangerous than a high false positive rate
- The model must generalize to previously unseen message styles

---

## Dataset

- **Source:** SMS Spam Collection Dataset (via Kaggle / UCI Machine Learning Repository)
- **Size:** 5,572 SMS messages
- **Classes:** Binary — `spam` and `ham` (not spam)
- **Class Distribution:** ~87% ham, ~13% spam (imbalanced)
- **Columns used:** `label` (target), `message` (raw SMS text)

---

## Project Journey

### Phase 1: Exploratory Data Analysis

The first step was understanding the data before applying any model.

**Key findings from EDA:**
- Spam messages are significantly **longer** than ham messages on average
- Spam messages use far more **special characters** (`$`, `!`, `%`) and **capital letters**
- Spam messages have a higher average **word count** and **unique character count**
- Common spam keywords: `free`, `win`, `winner`, `prize`, `cash`, `claim`, `urgent`, `call now`
- Common ham keywords: everyday conversational words like `going`, `ok`, `tomorrow`, `know`
- Visualizations used: word clouds, histograms of character/word counts, correlation heatmaps, pair plots

These findings directly informed the preprocessing and feature engineering strategy.

---

### Phase 2: Text Preprocessing

Raw SMS text is noisy and inconsistent. A `transform_message()` pipeline was built to clean and normalize text before feeding it to the model:

**Steps applied in order:**
1. **Lowercase conversion** — removes case sensitivity (`FREE` → `free`)
2. **Tokenization** — splits text into individual tokens using NLTK's `word_tokenize()`
3. **Alphanumeric filtering** — removes punctuation and special characters
4. **Stopword removal** — removes common English words (`the`, `is`, `at`) that carry no predictive value
5. **Stemming** — reduces words to their root form using the Porter Stemmer (`claiming` → `claim`, `prizes` → `prize`)

**Example:**
```
Input:  "WINNER!! You've been selected to receive a FREE prize. Call NOW!"
Output: "winner select receiv free prize call"
```

This function is extracted into `backend/utils/preprocess.py` and reused identically at training time and inference time — ensuring there's no train/serve skew.

---

### Phase 3: Feature Engineering

After cleaning, the text was converted into a numerical format the model could learn from.

**Method: TF-IDF Vectorization (Term Frequency–Inverse Document Frequency)**

- TF-IDF assigns a score to each word based on how frequently it appears in a message *and* how rare it is across the entire corpus
- Common words across all messages (e.g., `ok`, `lol`) get low scores; rare but important words (e.g., `prize`, `claim`) get high scores
- The fitted vectorizer was saved as `vectorizer.pkl` and is loaded at inference time to ensure the exact same vocabulary and IDF weights are used

**Why not Bag of Words?**
TF-IDF was preferred over simple Bag of Words because it penalizes words that appear too frequently across all documents (which are uninformative), giving more weight to discriminative terms.

---

### Phase 4: Model Building & Evaluation

Multiple classifiers were trained and evaluated individually before combining them:

**Individual models tested:**
| Model | Notes |
|---|---|
| MultinomialNB | Strong baseline for text classification; fast and interpretable |
| SVC (Support Vector Classifier) | Strong on high-dimensional sparse data; kernel-based boundary |
| ExtraTreesClassifier | Ensemble tree model; robust to noise and overfitting |

**Why a Voting Classifier?**
Each individual model has different strengths and weaknesses. A `VotingClassifier` with `voting='soft'` combines the probability outputs of all three, averaging them to produce a more stable and reliable final probability — reducing the impact of any one model being wrong.

**Evaluation metrics focused on:**
- **Precision** — of all messages flagged as spam, how many were actually spam? (Critical — we don't want to wrongly block legitimate messages)
- **Recall** — of all actual spam, how many did we catch?
- **F1 Score** — harmonic mean of precision and recall
- **ROC-AUC** — overall discriminative ability of the model

---

### Phase 5: Threshold Tuning

By default, classifiers use a `0.5` probability threshold to decide spam vs. not-spam. This was replaced with a **custom threshold** tuned specifically to maximize precision.

**Why?**
In this domain, a false positive (marking a legitimate message as spam) is worse than a false negative (missing spam). Raising the threshold means the model only calls something spam when it is very confident — reducing false positives at the cost of slightly lower recall.

A `find_threshold_for_precision()` function was used in the notebook to sweep threshold values and find the optimal cutoff. This value was saved in `threshold.json` and is loaded by the API at inference time.

---

### Phase 6: Model Serialization

After training and evaluation, three artifacts were saved using Python's `pickle` module:

| File | Contents |
|---|---|
| `model.pkl` | Trained `VotingClassifier` (SVC + MultinomialNB + ExtraTreesClassifier) |
| `vectorizer.pkl` | Fitted `TfidfVectorizer` (vocabulary + IDF weights) |
| `threshold.json` | Optimal decision threshold (float between 0 and 1) |

**Important note on scikit-learn versions:**
The model was trained using scikit-learn `1.6.1` in Google Colab. The local and deployment environments must use the same version to avoid `InconsistentVersionWarning` on unpickling. This is pinned in `requirements.txt`.

**Important note on sparse vs. dense arrays:**
The `SVC` component of the `VotingClassifier` was trained on **dense** arrays (`.toarray()` was called during training). At inference time, `vectorizer.transform()` returns a sparse matrix by default — this caused a `ValueError: cannot use sparse input in 'SVC' trained on dense data`. The fix applied in `app.py`:
```python
vector = vectorizer.transform([cleaned]).toarray()  # sparse → dense
```

---

### Phase 7: Backend Development

A RESTful API was built using **Flask** to serve the model and the frontend.

**Architecture:**
- `app.py` — main Flask application; loads model artifacts at startup; defines all routes
- `utils/preprocess.py` — text cleaning pipeline (identical to what was used during training)
- `utils/confidence.py` — 20-band safety score label mapper
- Flask serves both the API (`/predict`) and the static frontend files from a single process — no separate frontend server needed

**Key design decisions:**
- Model artifacts are loaded **once at startup** (not on every request) — fast inference
- Input validation returns `400` errors before reaching the model
- CORS is enabled via `flask-cors` to allow cross-origin requests during development
- A `/health` endpoint is provided for monitoring and Render health checks
- `gunicorn` is used as the production WSGI server instead of Flask's built-in development server

---

### Phase 8: Frontend Development

A two-page frontend was built using plain HTML5, CSS3, and Vanilla JavaScript — no frameworks required.

**Landing Page (`landing.html`):**
- Full-bleed background image with a glassmorphism-style dark header/footer
- Animated hero text (fade + slide-up entrance animation)
- "LAUNCH SPAM CHECKER" CTA button with hover zoom effect and violet-to-gold gradient

**Main App Page (`index.html`):**
- Side-by-side layout: message input (left) and result (right)
- Dark translucent textarea with focus glow, custom scrollbar, and gold border on focus
- Result box with gradient top accent bar that changes color (red for spam, green for safe)
- 20-band confidence label displayed as a pill badge
- Shake animation on the result box when no message is entered
- Responsive layout that stacks vertically on mobile

**Design system:**
- Color palette pulled directly from the background image: deep navy `#0b0a14`, violet `#7c3aed`, gold `#fbbf24`, soft lavender `#c4b5fd`
- All header/footer elements use `rgba` + `backdrop-filter: blur()` for consistent glassmorphism
- Animations use CSS `@keyframes` with `animation-fill-mode: forwards` to avoid flash-of-invisible-content

---

### Phase 9: Testing

Two test files cover the project:

**`tests/test_app.py`** — Flask API integration tests:
- Health check endpoint
- Empty and missing message input validation
- End-to-end prediction on real spam and ham messages
- Response structure consistency check

**`tests/test_confidence.py`** — Confidence pipeline tests:
- 20 real SMS messages sent through the full live prediction pipeline
- For each message, the returned `safety_score` is independently re-mapped using `get_confidence_label()` and compared against the API's returned `confidence_label`
- Proves the score-to-label mapping is internally consistent for real model output

---

### Phase 10: Deployment

The application is deployed on **Render** as a single Web Service:

- `Procfile` instructs Render to start the app with `gunicorn`
- `runtime.txt` pins the Python version for reproducibility
- `requirements.txt` pins all dependency versions including scikit-learn `1.6.1`
- The Flask app serves both the API and the frontend static files from one process — no separate static hosting needed

---

## Tech Stack

**Backend**
- Python 3.11
- Flask 3.0.3
- Flask-CORS 4.0.1
- scikit-learn 1.6.1
- NLTK 3.8.1
- Gunicorn 22.0.0
- NumPy 1.26.4

**Frontend**
- HTML5, CSS3, Vanilla JavaScript
- CSS animations, glassmorphism, custom scrollbars
- Fully responsive (mobile-first breakpoints)

**ML Pipeline**
- NLTK (tokenization, stopwords, Porter Stemmer)
- TF-IDF Vectorization (scikit-learn)
- Voting Classifier (SVC + MultinomialNB + ExtraTreesClassifier)
- Custom precision-tuned decision threshold

**Deployment**
- Render (Web Service)
- Gunicorn (WSGI production server)

---

## Project Structure

```
sms-spam-detector/
│
├── backend/
│   ├── app.py                      # Main Flask API + frontend serving
│   ├── model/
│   │   ├── model.pkl               # Trained VotingClassifier
│   │   ├── vectorizer.pkl          # Fitted TF-IDF vectorizer
│   │   └── threshold.json          # Custom decision threshold
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── preprocess.py           # transform_message() pipeline
│   │   └── confidence.py           # 20-band safety score mapper
│   ├── tests/
│   │   ├── test_app.py             # Flask API integration tests
│   │   └── test_confidence.py      # Confidence label pipeline tests
│   ├── requirements.txt
│   └── runtime.txt
│
├── frontend/
│   ├── landing.html                # Landing page
│   ├── index.html                  # Main spam checker page
│   ├── css/
│   │   ├── landing.css
│   │   └── style.css
│   ├── js/
│   │   ├── landing.js
│   │   └── script.js
│   └── assets/
│       └── background.jpg
│
├── notebooks/
│   └── Sms_Spam_Working.ipynb      # Full EDA + training notebook
│
├── data/
│   └── spam.csv
│
├── scripts/
│   └── train.py
│
├── .gitignore
├── .env.example
├── Procfile
├── README.md
└── LICENSE
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- pip

### 1. Clone the repository
```bash
git clone https://github.com/Sourajit-1905/Spam-Classifier
cd sms-spam-detector
```

### 2. Install dependencies
```bash
cd backend
pip install -r requirements.txt --break-system-packages
```

### 3. Add model files
Place these three files inside `backend/model/`:
- `model.pkl`
- `vectorizer.pkl`
- `threshold.json`

(Generate them by running the last cell of `notebooks/Working.ipynb` in Google Colab)

### 4. Start the server
```bash
python app.py
```

### 5. Open the app
```
http://127.0.0.1:5000/
```

---

## API Reference

### GET `/health`
Health check endpoint.

**Response:**
```json
{"status": "SMS Spam Detector API is running"}
```

### GET `/`
Serves `landing.html`.

### POST `/predict`
Classifies an SMS message.

**Request body:**
```json
{"message": "WINNER!! You've been selected for a FREE prize!"}
```

**Response:**
```json
{
  "prediction": 1,
  "probability": 0.9421,
  "safety_score": 5.79,
  "confidence_label": "Extremely likely spam"
}
```

| Field | Type | Description |
|---|---|---|
| `prediction` | int | `1` = spam, `0` = not spam |
| `probability` | float | Raw spam probability from the model (0–1) |
| `safety_score` | float | `(1 - probability) * 100` — higher is safer |
| `confidence_label` | string | Human-readable band label from the 20-band scale |

---

## Confidence Score System

The safety score converts the model's raw spam probability into a 0–100% scale where **lower = more spam-like** and **higher = more safe**:

```
safety_score = (1 - spam_probability) * 100
```

This score is then mapped into 20 bands of 5% each:

| Range | Label |
|---|---|
| 0–5% | Extremely likely spam |
| 5–10% | Very highly likely spam |
| 10–15% | Highly likely spam |
| 15–20% | Strongly likely spam |
| 20–25% | Likely spam |
| 25–30% | Probably spam |
| 30–35% | Somewhat likely spam |
| 35–40% | Slightly leaning spam |
| 40–45% | Borderline, leaning spam |
| 45–50% | Borderline, uncertain |
| 50–55% | Borderline, leaning safe |
| 55–60% | Slightly leaning safe |
| 60–65% | Somewhat likely safe |
| 65–70% | Probably safe |
| 70–75% | Likely safe |
| 75–80% | Strongly likely safe |
| 80–85% | Highly likely safe |
| 85–90% | Very highly likely safe |
| 90–95% | Extremely likely safe |
| 95–100% | Highly likely not spam |

---

## Running Tests

**Confidence pipeline tests (20 real messages):**
```bash
cd tests
python test_confidence.py
```

---

## Model Performance

| Metric | Score |
|---|---|
| Precision | High (threshold-tuned) |
| Recall | Balanced |
| F1 Score | Strong |
| ROC-AUC | High |

> Exact metrics available in `notebooks/Working.ipynb`

---

## Author

Built by Sourajit Paul — Institute of Engineering and Management, Kolkata (IEMK)

[GitHub](https://github.com/Sourajit-1905) · [LinkedIn](https://www.linkedin.com/in/sourajit-paul-347351322/)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.