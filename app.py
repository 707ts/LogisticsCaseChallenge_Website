# app.py
import os
import pandas as pd 
from flask import Flask, request, jsonify, send_from_directory, send_file
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.foundation_models import Model
from report_gen import generate_report_pdf


app = Flask(__name__, static_url_path='', static_folder='public')

print("Lade Schiffsdatenbank (Parquet)...")
try:
    # Lade die Datei einmalig beim Start in den RAM
    df = pd.read_parquet('ship_report_imo_2024.parquet')
    df.columns = [c.lower() for c in df.columns]
    print("Spalten in DB:", df.columns.tolist())

    # Damit wir leichter suchen können, stellen wir sicher, dass die IMO ein String ist
    # Passe 'imo' an den echten Spaltennamen in deiner Datei an!
    if 'imo' in df.columns:
        df['imo'] = df['imo'].astype(str)
    else:
        print("WARNUNG: Keine Spalte 'imo' in der Parquet-Datei gefunden! Bitte Spaltennamen prüfen.")
        print("Vorhandene Spalten:", df.columns)

    print(f"Datenbank geladen: {len(df)} Schiffe gefunden.")
except Exception as e:
    print(f"FEHLER beim Laden der Parquet-Datei: {e}")
    df = pd.DataFrame() # Leerer Fallback


# --- KONFIGURATION ---

credentials = {
    "url": "https://au-syd.ml.cloud.ibm.com", # Achte darauf, dass die URL zu deinem Key passt (z.B. Dallas, Frankfurt, Sydney)
    "apikey": "Zid4Fd_rirNn23gKAsXS7f-Dso0XaUlh2T9wxkNmhSc0" 
}

project_id = "94b4d34d-ffa1-4f15-b3ec-0e0b98f802f3"
model_id = "ibm/granite-3-8b-instruct"

parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 1000,
    "min_new_tokens": 1,
    "repetition_penalty": 1.1
}

# Modell einmalig initialisieren
print("Initialisiere Watson Model...")
model = Model(
    model_id=model_id,
    params=parameters,
    credentials=credentials,
    project_id=project_id
)

# 1. Route: Liefert deine HTML-Seite aus (Frontend)
@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

#2. Route: API für die Schiffssuche aus der Parquet-Datei
@app.route('/api/search-ship', methods=['GET'])
def search_ship():
    imo = request.args.get('imo')
    
    if df.empty:
        return jsonify({"error": "Datenbank nicht geladen"}), 500
        
    # Suche im DataFrame
    # ACHTUNG: Passe 'imo' an deinen Spaltennamen an!
    ship_row = df[df['imo'] == imo]
    
    if ship_row.empty:
        return jsonify({"found": False, "message": "Schiff nicht gefunden"}), 404

    # Konvertiere die erste gefundene Zeile in ein Dictionary (JSON)
    ship_data = ship_row.iloc[0].to_dict()
    
    # NaN (leere Werte) durch null ersetzen, damit JSON valide bleibt
    ship_data = {k: (None if pd.isna(v) else v) for k, v in ship_data.items()}
    
    return jsonify({"found": True, "data": ship_data})

# 3. Route: API für den Report
@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    raw = request.get_json()
    if not raw:
        return jsonify({"success": False, "error": "No JSON payload"}), 400

    # Normalize incoming keys to lowercase so we can access them reliably
    data = {str(k).lower(): v for k, v in raw.items()}

    ship_name = data.get('ship_name') or data.get('name') or ''
    imo = data.get('imo') or ''
    mrv_ship_type = data.get('mrv_ship_type') or data.get('vesseltype') or ''
    length = data.get('length') or data.get('length_m') or ''
    width = data.get('width') or ''
    draft = data.get('draft_m_median') or data.get('draft') or ''
    report_year = data.get('report_year') or ''
    ais_distance = data.get('ais_distance_nm_total') or ''
    ais_time = data.get('ais_time_hours_total') or ''
    sog_mean = data.get('sog_mean_kn') or ''
    sog_p95 = data.get('sog_p95_kn') or ''
    moving_share = data.get('moving_share') or ''
    y_mrv = data.get('y_mrv_co2_per_nm_kg') or ''
    y_pred = data.get('y_pred_co2_per_nm_kg') or ''
    residual_kg = data.get('residual_kg') or ''
    residual_pctraw = data.get('residual_pct') or ''
    residual_pct = residual_pctraw * 100 or '' 
    flag_color = data.get('flag_color') or ''
    flag_reason = data.get('flag_reason') or ''

    print(f"Anfrage erhalten für: {ship_name} (IMO: {imo})")

    prompt = f"""You are an expert in maritime regulations and data analysis in the context of the EU MRV and FuelEU Maritime regulations.

                Analyze the following ship data for an official plausibility check:

            ### 1. Master data & dimensions
				- Ship name: {ship_name} (IMO: {imo})
				- Ship type: {mrv_ship_type}
				- Dimensions: Length {length}m, width {width}m, draft {draft}m

            ### 2. AIS movement profile (reporting year {report_year})
				- Total distance traveled: {ais_distance} nm
				- Operating time: {ais_time} h
				- Average speed: {sog_mean} kn (high load operation P95: {sog_p95} kn)
                - Time spent in motion: {moving_share}

            ### 3. Emission assessment (regression vs. MRV)
				- Reported intensity (MRV): {y_mrv} kg CO2/nm
				- Expected intensity (AI model): {y_pred} kg CO2/nm
                - Deviation (residual): {residual_kg} kg ({residual_pct}%)
				- Assessment: {flag_color}
				- Reason for assessment: {flag_reason}

            ### Your task:
				1. Create a concise summary of the operating profile (size, activity, speed).
				2. Evaluate the status of the “flag_color”:
				- If GREEN: Confirm the plausibility of the reported data in comparison to the AI model.
                - If RED: Explain the anomaly based on the “flag_reason” and point out the legal consequences of an incorrect MRV report.
				3. Provide a brief recommendation for the inspector.

				Respond in a structured, professional manner and in English."""

    try:
        generated_response = model.generate_text(prompt=prompt)
        text_result = generated_response if isinstance(generated_response, str) else generated_response.get('results', [{}])[0].get('generated_text', '')
        return jsonify({"success": True, "text": text_result})
    except Exception as e:
        print("Fehler:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
# 4. NEUE ROUTE FÜR PDF DOWNLOAD HINZUFÜGEN
@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    data = request.json
    imo = data.get('imo')
    text = data.get('text') # Der KI-Text, der im PDF stehen soll
    
    if not imo or not text:
        return jsonify({"error": "Fehlende Daten (IMO oder Text)"}), 400

    print(f"Erstelle PDF für IMO {imo}...")
    
    try:
        # Hier rufen wir dein Skript 'report_gen.py' auf
        pdf_path = generate_report_pdf(imo, text)
        
        # Wir senden die Datei direkt an den Nutzer zurück
        return send_file(pdf_path, as_attachment=True, download_name=f"FuelEU_Report_{imo}.pdf")
        
    except Exception as e:
        print(f"PDF Fehler: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("Server läuft auf http://localhost:5000")
    app.run(port=5000, debug=True)