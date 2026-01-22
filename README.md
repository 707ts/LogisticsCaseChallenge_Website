FuelEU Maritime Compliance Dashboard
A professional web application for analyzing maritime vessel compliance with EU MRV (Monitoring, Reporting, and Verification) and FuelEU Maritime regulations.

Overview
This dashboard helps maritime inspectors and compliance officers:

Search vessel data by IMO number
View detailed ship characteristics and AIS movement profiles
Analyze CO₂ emission compliance with AI-powered insights
Generate professional PDF reports with regulatory assessments
Features
Ship Search: Quick lookup of vessel data from a comprehensive parquet database
Compliance Analysis: Automatic assessment against expected emission baselines
AI-Powered Reports: IBM WatsonX AI generates detailed analysis and recommendations
PDF Export: Professional report generation with charts and visualizations
Responsive Design: Mobile-friendly dashboard using Tailwind CSS

Installation
Prerequisites
Python 3.8+
pip package manager
Setup
Clone the repository and navigate to the project directory

Create a virtual environment:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Configure environment variables:
Create a .env file in the root directory:
WATSONX_URL=https://api.us-south.ml.cloud.ibm.com
WATSONX_APIKEY=your_ibm_api_key_here
WATSONX_PROJECT_ID=your_project_id_here

Add the ship database:

Place ship_report_imo_20xx.parquet in the root directory

Running the Application
Start the Flask development server:
python app.py

The application will be available at http://localhost:5000
