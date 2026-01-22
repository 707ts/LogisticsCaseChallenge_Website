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
