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

        const shipDataRaw = result.data;
        console.log("Gefundene Daten:", shipDataRaw); // Hilft dir beim Debuggen der Spaltennamen!
        const shipData = roundNumbers(shipDataRaw);

        // 2. UI UPDATEN 
        renderShipDetails(shipData);
        renderMetrics(shipData);
        renderComplianceGrid(shipData);

        // 3. KI REPORT GENERIEREN
        statusMsg.textContent = "Generiere KI-Analyse...";
        
        // Annahme: Dein Parquet hat eine Spalte 'limit_value' oder ähnlich. 
        // Falls nicht, setze hier einen festen Wert oder berechne ihn im Python-Code.
        //const limit = shipData.limit_value || 1450; 
        //const emissions = shipData.co2_total || 0;

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

function roundNumbers(value) {
    if (value === null || value === undefined) return value;
    if (Array.isArray(value)) return value.map(roundNumbers);
    if (typeof value === 'object') {
        const out = {};
        for (const k in value) {
            if (!Object.prototype.hasOwnProperty.call(value, k)) continue;
            out[k] = roundNumbers(value[k]);
        }
        return out;
    }
    if (typeof value === 'number' && isFinite(value)) {
        return Number(value.toFixed(2));
    }
    return value;
}

function renderShipDetails(data) {
    // ACHTUNG: Prüfe in der Browser-Konsole, ob diese Namen (flag, type, etc.) stimmen!
    // Die Namen kommen jetzt direkt aus deiner Parquet-Datei (oft kleingeschrieben).
    document.getElementById('uiName').textContent = data.ship_name || "Unbekannt";
    document.getElementById('uiImo').textContent = data.imo || data.IMO;
    
    const grid = document.getElementById('shipDetailsGrid');
    grid.innerHTML = `
        <div><p class="text-gray-500">Typ</p><p class="font-semibold">${data.mrv_ship_type || "-"} </p></div>
        <div><p class="text-gray-500">Length</p><p class="font-semibold">${data.length || "-"} M</p></div>
        <div><p class="text-gray-500">Width</p><p class="font-semibold">${data.width || "-"} M</p></div>
        <div><p class="text-gray-500">Draft median</p><p class="font-semibold">${data.draft_m_median || "-"} M</p></div>
    `;
}

function renderMetrics(data) {
    const grid = document.getElementById('metricsGrid');

    // Werte formatieren
    const co2 = typeof data.y_mrv_co2_per_nm_kg === 'number' ? data.y_mrv_co2_per_nm_kg.toFixed(1) : data.y_mrv_co2_per_nm_kg;
    const co2_pred = typeof data.y_pred_co2_per_nm_kg === 'number' ? data.y_pred_co2_per_nm_kg.toFixed(2) : data.y_pred_co2_per_nm_kg;

    grid.innerHTML = `

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Distance travelled</p>
            <p class="text-2xl font-bold">${data.ais_distance_nm_total} NM</p>
        </div>

                <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Time Travelled</p>
            <p class="text-2xl font-bold">${data.ais_time_hours_total} h</p>
        </div>


        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">CO₂ Ausstoß (Total) MRV Angabe</p>
            <p class="text-2xl font-bold">${co2} Kg</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Calculated CO₂ per NM</p>
            <p class="text-2xl font-bold">${co2_pred} Kg</p>
        </div>

    `;
}

function renderComplianceGrid(data) {
    const grid = document.getElementById('complianceGrid');

    const isCompliant = data.flag_color === 'GREEN' ;
    const flagReason = data.flag_reason || "Keine Angabe";
    const complianceColor = isCompliant ? "text-green-600" : "text-red-600";
    const complianceText = isCompliant ? "Compliant" : "not Compliant";
    const residuallKg = data.residual_kg || 0;
    const residuallPct = data.residual_pct || 0;

    if (flagReason === "ok") {
    grid.innerHTML = `

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Residual</p>
            <p class="text-2xl font-bold">${residuallKg} Kg</p>
        </div>
        
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Residual %</p>
            <p class="text-2xl font-bold">${residuallPct}</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Status</p>
            <p class="text-2xl font-bold ${complianceColor}">${complianceText}</p>
        </div>
    `;

    } else {
            grid.innerHTML = `

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Residual</p>
            <p class="text-2xl font-bold">${residuallKg} Kg</p>
        </div>
        
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Residual %</p>
            <p class="text-2xl font-bold">${residuallPct}</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Status</p>
            <p class="text-2xl font-bold ${complianceColor}">${complianceText}</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Flag Reason</p>
            <p class="text-2xl font-bold">${flagReason}</p>
        </div>
    `;
    }
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