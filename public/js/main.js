// js/main.js
import { getShipFromParquet } from './database.js';
import { calculateCompliance } from './calculator.js';


// Icons initialisieren (Lucide)
lucide.createIcons();

const form = document.getElementById('searchForm');
const resultsSection = document.getElementById('resultsSection');
const statusMsg = document.getElementById('statusMsg');


form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const imo = document.getElementById('imoInput').value.trim();

    if (!imo) return;

    // UI zurücksetzen
    setLoading(true);
    resultsSection.classList.add('hidden');
    statusMsg.textContent = "Lese lokale Datenbank...";
    statusMsg.className = "mt-4 text-blue-600";

    try {
        // 1. Daten aus der "Datenbank" holen
        const shipData = await getShipFromParquet(imo);
        
        // 2. Berechnungen durchführen
        statusMsg.textContent = "Führe Compliance-Berechnungen durch...";
        const results = calculateCompliance(shipData);
        statusMsg.textContent = "Frage WatsonX API (via Server)...";

                const limit = 1450
        const aiText = await fetchAiReport(
            shipData.name, 
            results.co2EmissionsTonnes, 
            limit
        );

        console.log("KI Antwort:", aiText);
        // Hier könntest du den Text im UI anzeigen, z.B.:
        // document.getElementById('ai-result-box').innerText = aiText;


        // 3. UI updaten
        renderShipDetails(shipData, imo);
        renderMetrics(results, shipData);
        
        statusMsg.textContent = "Berechnung erfolgreich.";
        
        // Anzeigen
        statusMsg.textContent = "Berechnung erfolgreich.";
        statusMsg.className = "mt-4 text-green-600";
        resultsSection.classList.remove('hidden');

    } catch (error) {
        console.error(error);
        statusMsg.textContent = error.message;
        statusMsg.className = "mt-4 text-red-500";
    } finally {
        setLoading(false);
    }
});

// Hilfsfunktion, um den Server zu fragen
async function fetchAiReport(name, emissions, limit) {
    try {
        const response = await fetch('/api/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                shipName: name, 
                emissions: emissions, 
                limit: limit 
            })
        });
        
        const data = await response.json();
        if (data.success) {
            return data.text;
        } else {
            throw new Error(data.error);
        }
    } catch (e) {
        console.error("Server Error:", e);
        return "Fehler bei der KI-Generierung: " + e.message;
    }
}

function setLoading(isLoading) {
    const btn = form.querySelector('button');
    if (isLoading) {
        btn.textContent = "...";
        btn.disabled = true;
    } else {
        btn.textContent = "Berechnen";
        btn.disabled = false;
    }
}

function renderShipDetails(data, imo) {
    document.getElementById('uiName').textContent = data.name;
    document.getElementById('uiImo').textContent = imo;
    
    const grid = document.getElementById('shipDetailsGrid');
    grid.innerHTML = `
        <div><p class="text-gray-500">Flagge</p><p class="font-semibold">${data.flag}</p></div>
        <div><p class="text-gray-500">Typ</p><p class="font-semibold">${data.type}</p></div>
        <div><p class="text-gray-500">GT</p><p class="font-semibold">${data.grossTonnage}</p></div>
        <div><p class="text-gray-500">Fuel</p><p class="font-semibold">${data.fuelType}</p></div>
    `;
}

function renderMetrics(results, data) {
    const grid = document.getElementById('metricsGrid');
    
    // Farbe für Compliance Status
    const complianceColor = results.isCompliant ? "text-green-600" : "text-red-600";
    const complianceText = results.isCompliant ? "Konform" : "Nicht Konform";

    grid.innerHTML = `
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">CO₂ Ausstoß (Total)</p>
            <p class="text-2xl font-bold">${results.co2EmissionsTonnes} t</p>
            <p class="text-xs text-gray-400">basierend auf ${data.annualFuelConsumptionMT} t Verbrauch</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">GHG Intensität</p>
            <p class="text-2xl font-bold ${complianceColor}">${results.ghgIntensity}</p>
            <p class="text-xs text-gray-400">gCO₂eq/MJ</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Compliance Status</p>
            <p class="text-2xl font-bold ${complianceColor}">${complianceText}</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Geschätzte Strafe</p>
            <p class="text-2xl font-bold text-gray-800">€ ${results.penaltyEstimated}</p>
        </div>
    `;
}