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
| Flask-CORS | Cross-origin resource sharing |
| Gunicorn | Production WSGI server |
| Pandas | Data processing and analysis |
| NumPy | Numerical computations |
| python-dotenv | Environment variable management |

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
