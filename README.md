# 🚢 FuelEU Maritime Compliance Dashboard

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey?logo=flask&logoColor=white)
![IBM WatsonX](https://img.shields.io/badge/AI-IBM%20WatsonX-052FAD?logo=ibm&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/UI-Tailwind%20CSS-38B2AC?logo=tailwindcss&logoColor=white)

**A professional web application designed for maritime inspectors and compliance officers to analyze vessel compliance with EU MRV (Monitoring, Reporting, and Verification) and FuelEU Maritime regulations.**

---

## 📖 Overview

The FuelEU Maritime Compliance Dashboard streamlines the complex process of monitoring ship emissions. By integrating large-scale dataset queries with AI-powered insights, it provides a comprehensive tool for regulatory assessment.

This dashboard helps users to:
* **Search** vessel data instantly using IMO numbers.
* **Visualize** detailed ship characteristics and AIS movement profiles.
* **Analyze** CO₂ emission compliance against EU baselines.
* **Generate** professional PDF reports with AI-driven recommendations.

---

## ✨ Key Features

* 🔍 **Ship Search Engine**
    * Quick lookup of vessel data from a comprehensive Parquet database (`ship_report_imo_20xx.parquet`).
* 📊 **Compliance Analysis**
    * Automatic assessment of emission intensity.
    * Visual comparison against FuelEU Maritime targets.
* 🤖 **AI-Powered Insights**
    * Integration with **IBM WatsonX** to generate detailed textual analysis.
    * Automated recommendations for compliance improvements.
* 📄 **Professional Reporting**
    * One-click PDF export including charts, data tables, and AI assessments.
* 📱 **Modern UI**
    * Responsive, mobile-friendly design built with **Tailwind CSS**.

---

## 🛠 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python / Flask | Core application logic and API handling |
| **Frontend** | HTML5 / Tailwind CSS | Responsive user interface |
| **AI / LLM** | IBM WatsonX | Generative AI for compliance reports |
| **Data Storage** | Apache Parquet | High-performance columnar storage for ship data |
| **Reporting** | ReportLab / WeasyPrint | PDF generation engine |

---

## ⚙️ Installation

### Prerequisites
* Python 3.8 or higher
* `pip` package manager

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/fueleu-dashboard.git](https://github.com/your-username/fueleu-dashboard.git)
cd fueleu-dashboard

### 2. Set up Python Environment
Es wird empfohlen, eine virtuelle Umgebung zu nutzen:
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate

### 3. Install Dependencies
pip install flask pandas pyarrow python-dotenv ibm-watsonx-ai reportlab

### 4. Configure Environment Variables
WATSON_API_KEY=Dein_API_Key
WATSON_URL=[https://au-syd.ml.cloud.ibm.com](https://au-syd.ml.cloud.ibm.com)
WATSON_PROJECT_ID=Deine_Project_ID

### 5. Start Application
python app.py

*📂 Project Structure
/
├── app.py                  # Main Server (Flask Backend API)
├── report_gen.py           # Module for PDF generation
├── ship_report_imo_2024.parquet # Database (Ship Data)
├── .env                    # API Keys (excluded from Git)
├── public/                 # Frontend Files
│   ├── index.html          # Main Page
│   ├── style.css           # Custom Styles
│   └── js/
│       └── main.js         # Frontend Logic (Fetch API, DOM Manipulation)
└── requirements.txt        # Python Dependencies

🧠 How it Works
Search: The user enters an IMO number. The backend searches for the ship in the Parquet file.

Validation: The system checks the flag_color column. If it is "RED", the reported CO₂ values deviate significantly from the prediction.

AI Report: At the push of a button, the backend sends all ship data as a prompt to the WatsonX model (ibm/granite-3-8b-instruct). The AI analyzes the context and writes a summary.

Export: The result can be downloaded as a PDF, which is dynamically generated using Python.

📝 License
This project was created as part of a university project work.
