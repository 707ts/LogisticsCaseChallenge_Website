# app.py
import os
from flask import Flask, request, jsonify, send_from_directory
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.foundation_models import Model

app = Flask(__name__, static_url_path='', static_folder='public')

# --- DEINE KONFIGURATION ---
# Sicherheitshinweis: In einer echten Prüfung Keys am besten als Umgebungsvariable laden!
# Für jetzt nutzen wir deinen Code:

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
    return send_from_directory('public', 'index.html')

# 2. Route: API für den Report
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