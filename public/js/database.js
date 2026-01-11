// js/database.js

/**
 * Simuliert den Datenbank-Zugriff.
 * Hier würde später der Code stehen, der die .parquet Datei liest
 * (z.B. mittels duckdb-wasm oder arrow-js).
 */
export async function getShipFromParquet(imoNumber) {
    console.log(`Suche in lokaler Datenbank nach IMO: ${imoNumber}...`);

    // PLATZHALTER: Simulierte Verzögerung (wie beim echten File-Read)
    await new Promise(resolve => setTimeout(resolve, 800));

    // MOCK DATEN (Fallback, solange keine echte DB angebunden ist)
    // Diese Struktur entspricht dem, was du später aus der Parquet-Datei lesen würdest.
    const mockDb = {
        "9876543": {
            name: "MS Atlantic Explorer",
            flag: "Deutschland",
            type: "Container",
            grossTonnage: 45230,
            fuelType: "HFO",
            enginePowerKW: 15000, // Beispielwert für Berechnung
            annualFuelConsumptionMT: 1200 // Beispielwert für Berechnung
        },
        "1234567": {
            name: "MV Nordic Spirit",
            flag: "Norwegen",
            type: "Tanker",
            grossTonnage: 82400,
            fuelType: "MGO",
            enginePowerKW: 22000,
            annualFuelConsumptionMT: 1850
        }
    };

    const result = mockDb[imoNumber];

    if (!result) {
        throw new Error("Schiff nicht in der Datenbank gefunden.");
    }

    return result;
}