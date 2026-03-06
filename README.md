# 🔐 UPI Log Analyzer

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-purple?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> **A real-time security intelligence dashboard for analyzing UPI transaction logs — detecting fraud, brute force attacks, DOS patterns, and session anomalies across 5 log types.**

---

## 📌 Table of Contents
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Structure](#️-project-structure)
- [How It Works](#-how-it-works)
- [Log Types](#-log-types)
- [Fraud Score Logic](#-fraud-score-logic)
- [Anomaly Detection](#-anomaly-detection)
- [Tech Stack](#️-tech-stack)
- [Author](#️-author)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 Fraud Risk Score | Composite 0–100 score based on login failures, auth attempts, and attack patterns |
| 📊 Overview Dashboard | Live KPIs, alerts, and 4 interactive charts at a glance |
| 🔍 Deep Dive Analysis | Drill into login, session, attack, or service data individually |
| ⚠️ Anomaly Detection | Auto-detects brute force, credential stuffing, DOS attacks, suspicious sessions |
| 📥 Data Export | Download any of the 5 log CSVs + a full text summary report |
| 🔄 Synthetic Data | Generate realistic log data instantly — no real data needed |
| 📤 CSV Upload | Upload your own log files for analysis |
| 🌑 Dark Theme | Clean, minimal dark UI built for readability |

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/KuldeepB19/upi-log-analyzer.git
cd upi-log-analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

> On first load, click **"Generate & Analyze"** in the sidebar — the app creates synthetic log data and runs the full analysis instantly.

---

## 🗂️ Project Structure

```
upi-log-analyzer/
├── app.py              ← Main Streamlit app (single file)
└── requirements.txt    ← Dependencies
```

---

## 🧠 How It Works

```
Data Source (Synthetic / CSV Upload)
            ↓
    5 Log Files Parsed
            ↓
┌───────────┬──────────────┬─────────────┐
│  Login    │   Session    │  Unauth     │
│  Analysis │   Analysis   │  Analysis   │
└───────────┴──────────────┴─────────────┘
            ↓
    Anomaly Detection Engine
            ↓
    Composite Fraud Score (0–100%)
            ↓
  🟢 LOW  /  🟡 MEDIUM  /  🟠 HIGH  /  🔴 CRITICAL
```

---

## 📋 Log Types

| # | Log File | What It Contains |
|---|----------|-----------------|
| 1 | Login Logs | User login attempts, IP addresses, browser, success/failure |
| 2 | Session Logs | Session durations, user IDs, start/end times |
| 3 | Unauth Logs | Unauthenticated access attempts, failure reasons, retry counts |
| 4 | Request Logs | HTTP requests — normal, blank, and DOS attack patterns |
| 5 | Service Logs | UPI service subscriptions, plan types, active/suspended status |

---

## 📊 Fraud Score Logic

The fraud score is a weighted composite of three signals:

| Signal | Weight | Description |
|--------|--------|-------------|
| Login Failure Rate | 30% | % of logins that failed |
| Unauthenticated Rate | 40% | % of auth attempts that were rejected |
| Attack Rate | 30% | % of requests that were blank or DOS |

| Score | Level | Color |
|-------|-------|-------|
| 0–15 | LOW | 🟢 Green |
| 15–30 | MEDIUM | 🟡 Amber |
| 30–50 | HIGH | 🟠 Orange |
| 50–100 | CRITICAL | 🔴 Red |

---

## ⚠️ Anomaly Detection

The app automatically flags the following:

| Anomaly | Trigger Condition |
|---------|------------------|
| Brute Force | Any IP with >5 failed login attempts |
| Session Anomaly | Sessions shorter than 3 min or longer than 180 min |
| Credential Stuffing | Auth attempts with >10 retries |
| DOS Attack | Any request classified as `dos_attack` |
| Suspended Services | Services in `suspended` state |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.9+ | Core language |
| Streamlit | Web UI & dashboard |
| Plotly | Interactive charts |
| Pandas | Data processing |
| NumPy | Synthetic data generation |

---

## 👨‍💻 Author

**Kuldeep** — Big Data Capstone Project (Sem 3–4)

[![GitHub](https://img.shields.io/badge/GitHub-KuldeepB19-black?logo=github)](https://github.com/KuldeepB19)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
