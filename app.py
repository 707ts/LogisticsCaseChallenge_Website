# app.py
import os
import pandas as pd # NEU: Für die Parquet Datei
from flask import Flask, request, jsonify, send_from_directory
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.foundation_models import Model

app = Flask(__name__, static_url_path='', static_folder='public')

print("Lade Schiffsdatenbank (Parquet)...")
try:
    # Lade die Datei einmalig beim Start in den RAM
    df = pd.read_parquet('ship_report_imo_2024.parquet')
    
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
    "max_new_tokens": 500,
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
    return send_from_directory('public', 'index_copy.html')

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
    data = request.json
    schiffs_name = data.get('shipName', 'Unbekanntes Schiff')
    berechneter_wtw = data.get('emissions', 0)
    grenzwert = data.get('limit', 0)

    print(f"Anfrage erhalten für: {schiffs_name}")

    # Dein Prompt
    prompt = f"""Du bist ein Experte für EU-Maritime-Regulierungen.
    Analysiere folgende Daten für eine Behördenprüfung:
    - Schiff: {schiffs_name}
    - Berechnete Well-to-Wake Emissionen: {berechneter_wtw} Tonnen CO2-eq
    - Erlaubter Grenzwert: {grenzwert} Tonnen CO2-eq

    Aufgabe: Erstelle eine kurze Zusammenfassung für den Inspektor.
    Ist das Schiff konform? Falls nein, berechne die prozentuale Überschreitung
    und nenne die rechtliche Konsequenz laut FuelEU Maritime."""

    try:
        # Generierung starten
        generated_response = model.generate_text(prompt=prompt)
        
        # Manchmal gibt die API ein Objekt zurück, manchmal direkt den Text. 
        # Wir stellen sicher, dass wir den Text haben.
        text_result = generated_response if isinstance(generated_response, str) else generated_response.get('results', [{}])[0].get('generated_text', '')
        
        return jsonify({"success": True, "text": text_result})

    except Exception as e:
        print("Fehler:", e)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("Server läuft auf http://localhost:5000")
    app.run(port=5000, debug=True)