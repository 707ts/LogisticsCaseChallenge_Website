// public/js/main.js
lucide.createIcons();

const form = document.getElementById('searchForm');
const resultsSection = document.getElementById('resultsSection');
const statusMsg = document.getElementById('statusMsg');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const imo = document.getElementById('imoInput').value.trim();
    if (!imo) return;

    // UI Reset
    setLoading(true);
    resultsSection.classList.add('hidden');
    statusMsg.textContent = "Suche Schiff in Datenbank...";
    statusMsg.className = "mt-4 text-blue-600";

    try {
        // 1. ANFRAGE AN DEIN PYTHON BACKEND
        const response = await fetch(`/api/search-ship?imo=${imo}`);
        const result = await response.json();

        if (!response.ok || !result.found) {
            throw new Error("Schiff nicht gefunden (Prüfen Sie die IMO-Nummer).");
        }

        const shipData = result.data;
        console.log("Gefundene Daten:", shipData); // Hilft dir beim Debuggen der Spaltennamen!

        // 2. UI UPDATEN (Keine Berechnung mehr nötig, Daten sind ja da)
        renderShipDetails(shipData);
        renderMetrics(shipData);

        // 3. KI REPORT GENERIEREN
        statusMsg.textContent = "Generiere KI-Analyse...";
        
        // Annahme: Dein Parquet hat eine Spalte 'limit_value' oder ähnlich. 
        // Falls nicht, setze hier einen festen Wert oder berechne ihn im Python-Code.
        const limit = shipData.limit_value || 1450; 
        const emissions = shipData.co2_total || 0;

        //const aiText = await fetchAiReport(shipData.name, emissions, limit);
        //console.log("KI Bericht:", aiText);
        
        // Optional: KI Text anzeigen (wenn du ein Element dafür im HTML hast)
        // document.getElementById('aiOutput').innerText = aiText;

        statusMsg.textContent = "Daten erfolgreich geladen.";
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

// Hilfsfunktion für KI
async function fetchAiReport(name, emissions, limit) {
    try {
        const response = await fetch('/api/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ shipName: name, emissions: emissions, limit: limit })
        });
        const data = await response.json();
        return data.success ? data.text : "Fehler: " + data.error;
    } catch (e) {
        return "Netzwerkfehler bei KI Anfrage";
    }
}

function renderShipDetails(data) {
    // ACHTUNG: Prüfe in der Browser-Konsole, ob diese Namen (flag, type, etc.) stimmen!
    // Die Namen kommen jetzt direkt aus deiner Parquet-Datei (oft kleingeschrieben).
    document.getElementById('uiName').textContent = data.name || data.Name || "Unbekannt";
    document.getElementById('uiImo').textContent = data.imo || data.IMO;
    
    const grid = document.getElementById('shipDetailsGrid');
    grid.innerHTML = `
        <div><p class="text-gray-500">Flagge</p><p class="font-semibold">${data.flag || "-"}</p></div>
        <div><p class="text-gray-500">Typ</p><p class="font-semibold">${data.type || "-"}</p></div>
        <div><p class="text-gray-500">GT</p><p class="font-semibold">${data.gross_tonnage || "-"}</p></div>
        <div><p class="text-gray-500">Baujahr</p><p class="font-semibold">${data.year_built || "-"}</p></div>
    `;
}

function renderMetrics(data) {
    const grid = document.getElementById('metricsGrid');
    
    // Annahme: Deine Parquet hat eine Spalte 'is_compliant' (true/false oder 1/0)
    // Falls nicht, musst du hier eine einfache Logik einbauen (z.B. emissions < limit)
    const isCompliant = data.is_compliant || (data.co2_total < (data.limit_value || 999999));
    
    const complianceColor = isCompliant ? "text-green-600" : "text-red-600";
    const complianceText = isCompliant ? "Konform" : "Nicht Konform";

    // Werte formatieren
    const co2 = typeof data.co2_total === 'number' ? data.co2_total.toFixed(1) : data.co2_total;
    const ghg = typeof data.ghg_intensity === 'number' ? data.ghg_intensity.toFixed(2) : data.ghg_intensity;
    const penalty = typeof data.penalty === 'number' ? data.penalty.toFixed(2) : "0.00";

    grid.innerHTML = `
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">CO₂ Ausstoß (Total)</p>
            <p class="text-2xl font-bold">${co2} t</p>
            <p class="text-xs text-gray-400">Jahreswert aus Report</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">GHG Intensität</p>
            <p class="text-2xl font-bold ${complianceColor}">${ghg}</p>
            <p class="text-xs text-gray-400">gCO₂eq/MJ</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Status</p>
            <p class="text-2xl font-bold ${complianceColor}">${complianceText}</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Strafe (Penalty)</p>
            <p class="text-2xl font-bold text-gray-800">€ ${penalty}</p>
        </div>
    `;
}

function setLoading(isLoading) {
    const btn = form.querySelector('button');
    if (isLoading) {
        btn.innerHTML = '<span class="animate-pulse">Suche...</span>';
        btn.disabled = true;
    } else {
        btn.innerText = "Suchen";
        btn.disabled = false;
    }
}