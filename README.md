# 🛡️ AI-Based Fake Review Detection System (Master Project Edition)

A complete, modern, user-friendly web application designed for **College Final-Year & Master's Degree Project Presentations**. The system uses Artificial Intelligence, Machine Learning, and Natural Language Processing (NLP) to classify online product/service reviews into **Genuine Review**, **Fake Review**, or **Suspicious Review** along with **Explainable AI (XAI)** factor weights and confidence scores.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-yellow.svg)

---

## 🌟 Master Project Features

1. **🏠 Home & Hero Dashboard**:
   - Project overview, statistics cards (Total Reviews, Genuine, Fake, Accuracy), and target application use cases (E-Commerce, Hotels, Restaurants, Shoppers).

2. **🔍 Review Analyzer & AI Classification**:
   - Form inputs: Product/Service Name, Review Text, Rating (1–5 Stars), Reviewer Name, Date.
   - Real-time classification into:
     - 🟢 **Genuine Review** (Naturally written, trustworthy)
     - 🚨 **Fake Review** (Deceptive, bot spam, promotional manipulation)
     - ⚠️ **Suspicious Review** (Requires further verification)
   - Confidence Score %, Sentiment polarity, Suspicious indicators, and Recommendation.

3. **💡 Explainable AI ("Why was this review detected?")**:
   - Visual factor progress bars displaying risk weights:
     - Excessive positive language
     - Repeated phrases / filler density
     - Rating vs text sentiment mismatch
     - Review length anomaly
     - Promotional trigger words

4. **📜 Review History Database**:
   - Search review text or product name.
   - Filter by Genuine / Fake / Suspicious categories.
   - Sort by Newest, Highest Confidence, or Lowest Confidence.
   - View analysis details modal dialog.
   - Delete individual records via API (`DELETE /api/reviews/:id`).

5. **📊 Admin Analytics Dashboard**:
   - Summary metric cards + 4 interactive Chart.js charts:
     - Genuine vs Fake Reviews (Doughnut)
     - Reviews Analyzed Over Time (Line)
     - Prediction Distribution (Bar)
     - Confidence Score Distribution (Histogram)

6. **ℹ️ Project Specifications & Machine Learning Architecture**:
   - Detailed breakdown of supported ML models (Logistic Regression, Naive Bayes, Random Forest, SVM, TF-IDF, BERT Transformers) and NLP preprocessing steps.

---

## 🏗️ Project Architecture

```
fake-review-detector/
├── index.html                  # Single Page Application Dashboard Layout
├── src/
│   ├── css/
│   │   └── style.css           # Glassmorphism & High-Contrast Design System
│   └── js/
│       ├── app.js              # SPA Routing, Form Handlers & Presets
│       ├── classifier.js       # NLP & Explainable AI Classification Engine
│       ├── history.js          # Review History Manager (Search, Filter, Delete)
│       └── dashboard.js        # Admin Analytics Dashboard (4 Chart.js Visuals)
├── backend/
│   ├── main.py                 # FastAPI REST API Server & Endpoints
│   ├── database.py             # SQLite Database Persistence Engine
│   ├── model_trainer.py        # ML Model Training Pipeline (scikit-learn)
│   ├── requirements.txt        # Python Package Requirements
│   └── data/
│       ├── sample_reviews.json # Benchmark Dataset
│       └── reviews.db          # SQLite Database File
├── README.md                   # Project Documentation
└── package.json                # Project Dependencies & Scripts
```

---

## 📡 REST API Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/analyze-review` | Submit review text, run AI analysis, store in DB, return XAI results |
| `GET` | `/api/reviews` | Retrieve all previously analyzed reviews from database |
| `GET` | `/api/reviews/{id}` | Get single review analysis record by ID |
| `DELETE` | `/api/reviews/{id}` | Delete individual review record from database |
| `GET` | `/api/dashboard` | Get summary statistics for admin charts |

---

## 🚀 Quick Start Guide

### 1. Launch Web Dashboard (Standalone Mode)
Simply double click or open [`index.html`](file:///C:/Users/Jeeva%20M/.gemini/antigravity/scratch/fake-review-detector/index.html) in any web browser.

### 2. Launch Full-Stack REST Backend & SQLite DB
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```
- Swagger API Docs: `http://localhost:8000/docs`
