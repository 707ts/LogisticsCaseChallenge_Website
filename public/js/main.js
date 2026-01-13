// public/js/main.js
lucide.createIcons();

const form = document.getElementById('searchForm');
const resultsSection = document.getElementById('resultsSection');
const statusMsg = document.getElementById('statusMsg');
const aiButton = document.getElementById('aiButton');
const pdfButton = document.getElementById('pdfButton');
let currentShipData = null;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const imo = document.getElementById('imoInput').value.trim();
    if (!imo) return;

    // UI Reset
    setLoading(true);
    resultsSection.classList.add('hidden');
    aiButton.classList.add('hidden');
    statusMsg.textContent = "Search Ship in Database...";
    statusMsg.className = "mt-4 text-blue-600";

    try {
        // 1. ANFRAGE AN DEIN PYTHON BACKEND
        const response = await fetch(`/api/search-ship?imo=${imo}`);
        const result = await response.json();

        if (!response.ok || !result.found) {
            throw new Error("Ship not found (Check the IMO number).");
        }

        const shipDataRaw = result.data;
        console.log("Found Data:", shipDataRaw);
        const shipData = roundNumbers(shipDataRaw);
        currentShipData = shipData;
        aiButton.classList.remove('hidden');

        // 2. UI UPDATEN 
        renderShipDetails(shipData);
        renderMetrics(shipData);
        renderComplianceGrid(shipData);

        statusMsg.textContent = "Data successfully loaded.";
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

// --- 2. KI REPORT (BUTTON CLICK) ---
aiButton.addEventListener('click', async () => {
    if (!currentShipData) return;

    // Ladezustand für den KI Button
    const originalText = aiButton.innerHTML;
    aiButton.innerHTML = '<span class="animate-pulse">Analyse...</span>';
    aiButton.disabled = true;
    
    statusMsg.textContent = "WatsonX generates Report...";
    statusMsg.className = "mt-4 text-indigo-600";

    try {
        const aiText = await fetchAiReport(currentShipData);
        
        console.log("KI Bericht:", aiText);
        
        statusMsg.textContent = "Analyse completed.";
        statusMsg.className = "mt-4 text-green-600";

        currentShipData.aiAnalysisText = aiText;
        
        // NEU: PDF Button anzeigen, sobald Text da ist
        if(pdfButton) {
            pdfButton.classList.remove('hidden');
        }

    } catch (e) {
        console.error(e);
        statusMsg.textContent = "Error during KI analysis.";
        statusMsg.className = "mt-4 text-red-500";
    } finally {
        // Button Reset
        aiButton.innerHTML = originalText;
        aiButton.disabled = false;
    }
});

// Hilfsfunktion für KI
async function fetchAiReport(shipData) {
    try {
        const response = await fetch('/api/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // ÄNDERUNG: Das komplette Objekt wird als JSON gesendet
            body: JSON.stringify(shipData) 
        });
        const data = await response.json();
        return data.success ? data.text : "Error: " + data.error;
    } catch (e) {
        return "Network error";
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
    document.getElementById('uiName').textContent = data.ship_name || "Unknown Name";
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
            <p class="text-sm text-gray-500">Time travelled</p>
            <p class="text-2xl font-bold">${data.ais_time_hours_total} h</p>
        </div>


        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">CO₂ Emission (Total) MRV</p>
            <p class="text-2xl font-bold">${co2} Kg per NM</p>
        </div>

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Calculated CO₂ Emission</p>
            <p class="text-2xl font-bold">${co2_pred} Kg per NM</p>
        </div>

    `;
}

function renderComplianceGrid(data) {
    const grid = document.getElementById('complianceGrid');

    const isCompliant = data.flag_color === 'GREEN' ;
    const flagReason = data.flag_reason || "No information";
    const complianceColor = isCompliant ? "text-green-600" : "text-red-600";
    const complianceText = isCompliant ? "Compliant" : "not Compliant";
    const residuallKg = data.residual_kg || 0;
    const residuallPct = data.residual_pct * 100 || 0;

    if (flagReason === "ok") {
    grid.innerHTML = `

        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Residual</p>
            <p class="text-2xl font-bold">${residuallKg} Kg</p>
        </div>
        
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500">Residual %</p>
            <p class="text-2xl font-bold">${residuallPct}%</p>
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
        btn.innerHTML = '<span class="animate-pulse">Loading...</span>';
        btn.disabled = true;
    } else {
        btn.innerText = "Calculate";
        btn.disabled = false;
    }
}

// 2. Event Listener für den PDF Button hinzufügen

if (pdfButton) {
    pdfButton.addEventListener('click', async () => {
        if (!currentShipData || !currentShipData.aiAnalysisText) {
            alert("Please perform a KI-Analyse first.");
            return;
        }

        const originalText = pdfButton.innerHTML;
        pdfButton.innerHTML = '<span class="animate-pulse">Creating PDF...</span>';
        pdfButton.disabled = true;

        try {
            // Anfrage an deine neue Route
            const response = await fetch('/api/download-pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    imo: currentShipData.imo || currentShipData.IMO, // Achte auf Groß/Klein je nach DB
                    text: currentShipData.aiAnalysisText
                })
            });

            if (response.ok) {
                // Den "Blob" (Datei) vom Server nehmen und Download starten
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Report_${currentShipData.imo}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                throw new Error("Error during PDF Creation");
            }

        } catch (error) {
            console.error(error);
            alert("Error during PDF Download");
        } finally {
            pdfButton.innerHTML = originalText;
            pdfButton.disabled = false;
        }
    });
}