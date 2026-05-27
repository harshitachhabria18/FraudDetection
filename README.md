# 🔒 AI RiskRadar

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-FF6600?style=for-the-badge)](https://xgboost.readthedocs.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-F55036?style=for-the-badge)](https://groq.com)
[![Gemini](https://img.shields.io/badge/Gemini-Vision-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)

**AI-powered platform to detect risk of potentially fraudulent financial transactions**

---

## 🔗 Live Demo
[https://ai-riskradar.onrender.com/](https://ai-riskradar.onrender.com/)

---

## 📌 About The Project
AI RiskRadar is an end-to-end AI-powered fraud detection platform built for Indian financial transactions. It combines a trained XGBoost machine learning model with rule-based logic and AI-generated explanations to detect suspicious transactions in real time.

The platform goes beyond traditional fraud detection — it includes receipt verification using Google Gemini AI, a fraud awareness chatbot powered by LLaMA 3, and bulk CSV transaction analysis, making it a complete fraud intelligence system.

### Why this project?
Financial fraud costs Indian consumers thousands of crores every year. Most fraud detection tools are either too technical for everyday users or too simplistic to catch real patterns. AI RiskRadar bridges this gap by providing instant, explainable fraud analysis in plain language — no technical knowledge required.

---

## ✨ Features
- **Transaction Analysis** — Enter transaction details in INR and get instant fraud risk prediction using the XGBoost ML model
- **Receipt Analysis** — Upload payment receipts for Gemini Vision OCR extraction and AI-based fraud scoring
- **Fraud Chatbot** — Ask questions about UPI fraud, phishing attacks, and cyber fraud prevention
- **Batch Processing** — Upload CSV files with multiple transactions and download analyzed results
- **CSV Export Support** — Download CSV templates and export processed fraud analysis reports
- **AI Explanations** — Groq LLaMA 3.3 explains fraud predictions in simple, human-readable language
- **Rule Engine** — Detect suspicious patterns using amount anomaly, tax inconsistency, and unusual timing analysis
- **Risk Visualization** — Dynamic fraud probability scoring with risk-level indicators
- **Print & Copy Support** — Export or copy fraud detection reports instantly
- **Responsive Design** — Optimized for both desktop and mobile devices
- **India Focused** — Designed for Indian financial transactions in INR (₹), suitable for individuals, banks, and financial institutions

---

## 🛠️ Tech Stack
### Backend
| Technology | Purpose |
|---|---|
| Python 3.12 | Core programming language |
| Flask | Backend web framework |
| Gunicorn | Production WSGI server 
| Pandas | Data processing and analysis |
| NumPy | Numerical computations |

### Machine Learning
| Technology | Purpose |
|---|---|
| XGBoost | Fraud prediction model |
| Scikit-learn | Preprocessing and evaluation |
| PaySim Dataset | Model training dataset (6.3M transactions) |

### Generative AI & Vision APIs
| API | Purpose |
|---|---|
| Groq (LLaMA 3.3 70B) | AI-generated explanations, chatbot, and batch analysis |
| Gemini 2.5 Flash | Receipt understanding and transaction detail extraction |

### Frontend
| Technology | Purpose |
|---|---|
| HTML5 | Application structure |
| CSS3 | Styling and glassmorphism UI |
| Vanilla JavaScript | Client-side interactivity |
| Fetch API | Frontend-backend communication |

---

## 🧠 Machine Learning Model 
### Dataset — PaySim
| Property | Value |
|---|---|
| Source | [PaySim — Kaggle](https://www.kaggle.com/datasets/ealaxi/paysim1) |
| Total transactions | 6,362,620 |
| Fraud cases | 8,213 (0.13%) |
| Filtered dataset | 2,770,409 (TRANSFER + CASH_OUT only) |
| Training scale | INR (×96.31 conversion applied) |

### Why PaySim?
- Human-readable financial features without hidden PCA transformations
- Simulates realistic mobile money transactions
- Suitable for fraud behavior analysis and explainable predictions
- Allows users to enter meaningful transaction details such as balances and amounts

### Preprocessing
- Filtered to **TRANSFER** and **CASH_OUT** transaction types
- Converted monetary values to INR (₹) before training
- Handled class imbalance using `scale_pos_weight = 336`
- Stratified 80/20 train-test split

### Model Comparison
| Model | Recall | Precision | F1 | ROC-AUC |
|---|---|---|---|---|
| Logistic Regression | 0.97 | 0.02 | 0.05 | 0.97 |
| Decision Tree | 0.84 | 0.88 | 0.86 | 0.92 |
| Random Forest | 0.77 | 0.98 | 0.86 | 0.99 |
| **XGBoost** ✅ | **0.89** | **0.93** | **0.91** | **0.9988** |

> XGBoost was selected as the final model because it achieved the best balance between fraud detection recall and prediction precision while maintaining an exceptionally high ROC-AUC score.

### Final Model Performance
| Metric | Score |
|---|---|
| Algorithm | XGBoost Classifier |
| Estimators | 200 |
| Precision | 0.93 |
| Recall | 0.89 |
| F1 Score | 0.91 |
| ROC-AUC | 0.9988 |
| scale_pos_weight | 336 |

---

## 📁 Project Structure
```
AI-RiskRadar/
│
├── backend/
│   ├── __init__.py
│   ├── app.py                  ← Flask application entry point
│   ├── config.py               ← Constants & currency config
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── predict_route.py    ← /predict endpoint
│   │   ├── receipt.py    ← /analyze-receipt endpoint
│   │   ├── batch_route.py      ← /batch-predict endpoint
│   │   └── chatbot_route.py    ← /chatbot endpoint
│   │
│   └── utils/
│       ├── __init__.py
│       ├── model_loader.py     ← XGBoost model + feature loader
│       ├── explainer.py        ← Groq transaction explainer
│       ├── groq_explainer.py   ← Groq receipt explainer
│       ├── gemini_analyzer.py  ← Gemini Vision OCR
│       ├── rule_engine.py      ← Relative fraud scoring rules
│       └── chatbot.py          ← Chatbot Groq integration
│
├── models/
│   ├── fraud_detection_model.pkl  ← Trained XGBoost model
│   └── feature_columns.json       ← Feature column order
│
├── notebooks/
│   └── PaySimFraudDetection.ipynb ← Training & EDA notebook
│
├── templates/
│   └── index.html              ← Single page application
│
├── static/
│   ├── css/
│   │   └── style.css           ← All styles
│   └── js/
│       ├── script.js           ← Transaction form logic
│       ├── receipt.js          ← Receipt upload logic
│       ├── batch.js            ← Batch CSV logic
│       └── chatbot.js          ← Chatbot logic
│
├── .env                        ← API keys (never commit)
├── .gitignore
├── requirements.txt
```

---

## 🚀 Installation
### Prerequisites
- Python 3.12+
- pip
- Git

### Step 1 — Clone Repository
```bash
git clone https://github.com/harshitachhabria18/FraudDetection.git
cd FraudDetection
```

### Step 2 — Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set Up Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```
> ⚠️ Never commit your `.env` file. It is already included in `.gitignore`.

Get API keys:
- Groq → [console.groq.com](https://console.groq.com)
- Gemini → [aistudio.google.com](https://aistudio.google.com)

### Step 5 — Run Application
```bash
python -m backend.app
```

Open browser → `http://127.0.0.1:5000`

---




