const API_BASE = "http://localhost:8000";

// Status colors
const STATUS_COLORS = {
    "HIGH": { bg: "bg-red-100", border: "border-red-400", text: "text-red-800", dot: "bg-red-500" },
    "MEDIUM": { bg: "bg-yellow-100", border: "border-yellow-400", text: "text-yellow-800", dot: "bg-yellow-500" },
    "LOW": { bg: "bg-green-100", border: "border-green-400", text: "text-green-800", dot: "bg-green-500" }
};

const RISK_COLORS = {
    "OUTBREAK LIKELY": { bg: "bg-red-100", border: "border-red-400", text: "text-red-800" },
    "RISING": { bg: "bg-orange-100", border: "border-orange-400", text: "text-orange-800" },
    "MONITOR": { bg: "bg-yellow-100", border: "border-yellow-400", text: "text-yellow-800" },
    "STABLE": { bg: "bg-green-100", border: "border-green-400", text: "text-green-800" },
    "LOW ACTIVITY": { bg: "bg-blue-100", border: "border-blue-400", text: "text-blue-800" }
};

async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE}/ping`);
        if (response.ok) {
            document.getElementById("statusText").textContent = "✓ API is Running";
            document.getElementById("statusText").className = "text-green-300";
        } else {
            document.getElementById("statusText").textContent = "✗ API Error";
            document.getElementById("statusText").className = "text-red-300";
        }
    } catch (error) {
        document.getElementById("statusText").textContent = "✗ Offline";
        document.getElementById("statusText").className = "text-red-300";
    }
}

async function simulateObvious() {
    const size = parseInt(document.getElementById("obvSize").value) || 50;
    showFeedback(false);
    
    try {
        const response = await fetch(`${API_BASE}/simulate-batch-obvious?size=${size}`, {
            method: "POST"
        });
        const data = await response.json();
        
        if (data.status === "success") {
            showFeedback(true, `✓ Generated ${data.cases_generated} cases with OBVIOUS patterns`);
        } else {
            showError(data.error || "Simulation failed");
        }
    } catch (error) {
        showError(`Error: ${error.message}`);
    }
}

async function simulateRandom() {
    const size = parseInt(document.getElementById("randSize").value) || 50;
    showFeedback(false);
    
    try {
        const response = await fetch(`${API_BASE}/simulate-batch-random?size=${size}`, {
            method: "POST"
        });
        const data = await response.json();
        
        if (data.status === "success") {
            showFeedback(true, `✓ Generated ${data.cases_generated} cases with RANDOM patterns`);
        } else {
            showError(data.error || "Simulation failed");
        }
    } catch (error) {
        showError(`Error: ${error.message}`);
    }
}

async function runPrediction() {
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("results").classList.add("hidden");
    document.getElementById("error").classList.add("hidden");
    showFeedback(false);
    
    try {
        const response = await fetch(`${API_BASE}/predict`, { method: "POST" });
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            document.getElementById("loading").classList.add("hidden");
            return;
        }
        
        displayResults(data);
        document.getElementById("loading").classList.add("hidden");
    } catch (error) {
        showError(`Prediction failed: ${error.message}`);
        document.getElementById("loading").classList.add("hidden");
    }
}

function displayResults(data) {
    // Summary section
    const summ = data.prediction_summary;
    document.getElementById("sumDominant").textContent = summ.current_dominant_disease.toUpperCase();
    document.getElementById("sumRisk").textContent = `${(summ.outbreak_probability * 100).toFixed(0)}%`;
    
    const riskColor = STATUS_COLORS[summ.risk_level] || STATUS_COLORS["LOW"];
    document.getElementById("sumLevel").textContent = summ.risk_level;
    document.getElementById("sumLevel").className = `font-bold text-base ${riskColor.text}`;
    
    document.getElementById("sumConfidence").textContent = `${(summ.confidence_score * 100).toFixed(0)}%`;
    document.getElementById("sumTotal").textContent = data.total_analyzed;
    document.getElementById("sumSummary").textContent = summ.summary;
    
    // Disease predictions grid
    const diseaseGrid = document.getElementById("diseaseGrid");
    diseaseGrid.innerHTML = "";
    
    for (const [disease, pred] of Object.entries(data.disease_predictions)) {
        const colors = RISK_COLORS[pred.status] || RISK_COLORS["STABLE"];
        const card = document.createElement("div");
        card.className = `${colors.bg} ${colors.border} border rounded p-2 text-sm`;
        
        const drivers = pred.top_shap_drivers.map(d => 
            `<div class="text-xs"><span class="font-semibold">${d.feature}</span>: ${(d.mean_impact * 100).toFixed(0)}%</div>`
        ).join("");
        
        card.innerHTML = `
            <div class="font-bold text-base mb-1">${disease.toUpperCase()}</div>
            <div>
                <div><span class="font-semibold">Status:</span> ${pred.status}</div>
                <div><span class="font-semibold">Current:</span> ${pred.current_cases} cases</div>
                <div><span class="font-semibold">Forecast:</span> ${pred.predicted_cases_next_window} cases</div>
                <div><span class="font-semibold">Growth:</span> ${(pred.growth_rate * 100).toFixed(0)}%</div>
                <div><span class="font-semibold">Confidence:</span> ${(pred.prediction_confidence * 100).toFixed(0)}%</div>
                <div class="mt-1 pt-1 border-t border-gray-300">
                    <div class="font-semibold text-xs mb-1">SHAP Drivers:</div>
                    ${drivers}
                </div>
                <div class="mt-1 text-xs italic">${pred.interpretation}</div>
            </div>
        `;
        diseaseGrid.appendChild(card);
    }
    
    // Regional predictions
    const regionsGrid = document.getElementById("regionsGrid");
    regionsGrid.innerHTML = "";
    
    for (const region of data.regional_predictions) {
        const colors = STATUS_COLORS[region.risk_level] || STATUS_COLORS["LOW"];
        const card = document.createElement("div");
        card.className = `${colors.bg} ${colors.border} border rounded p-2 text-sm`;
        
        const drivers = region.top_shap_drivers.map(d => 
            `<div class="text-xs"><span class="font-semibold">${d.feature}</span>: ${(d.mean_impact * 100).toFixed(0)}%</div>`
        ).join("");
        
        card.innerHTML = `
            <div class="font-bold text-base mb-1">${region.region}</div>
            <div>
                <div><span class="font-semibold">Disease:</span> ${region.dominant_disease}</div>
                <div><span class="font-semibold">Risk Level:</span> ${region.risk_level}</div>
                <div><span class="font-semibold">Current Cases:</span> ${region.current_cases}</div>
                <div><span class="font-semibold">Forecast:</span> ${region.predicted_cases_next_window} cases</div>
                <div><span class="font-semibold">Outbreak Prob:</span> ${(region.outbreak_probability * 100).toFixed(0)}%</div>
                <div class="mt-1 pt-1 border-t border-gray-300">
                    <div class="font-semibold text-xs mb-1">SHAP Drivers:</div>
                    ${drivers}
                </div>
                <div class="mt-1 text-xs italic">${region.forecast}</div>
            </div>
        `;
        regionsGrid.appendChild(card);
    }
    
    document.getElementById("results").classList.remove("hidden");
}

function showFeedback(show, message = "") {
    const fb = document.getElementById("simFeedback");
    if (show) {
        document.getElementById("simMsg").textContent = message;
        fb.classList.remove("hidden");
        setTimeout(() => fb.classList.add("hidden"), 4000);
    } else {
        fb.classList.add("hidden");
    }
}

function showError(message) {
    document.getElementById("errorMsg").textContent = message;
    document.getElementById("error").classList.remove("hidden");
}

// Check API on load
window.addEventListener("load", checkApiHealth);

