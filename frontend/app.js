const API_BASE = "http://localhost:8000";
let isLoading = false; // Prevent multiple simultaneous requests

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
    // Prevent multiple simultaneous requests
    if (isLoading) {
        console.log("Already loading, skipping...");
        return;
    }
    
    const size = parseInt(document.getElementById("simSize").value) || 500;
    showFeedback(false);
    document.getElementById("error").classList.add("hidden");
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("results").classList.add("hidden");
    
    isLoading = true;
    
    try {
        // Create an abort controller with 30-second timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);
        
        console.log("Fetching predictions...");
        const response = await fetch(`${API_BASE}/simulate-batch?size=${size}`, {
            method: "POST",
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`API responded with status ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Response received:", data);
        
        if (data.error) {
            showError(data.error);
            document.getElementById("loading").classList.add("hidden");
            return;
        }
        
        if (data.prediction_summary && data.disease_predictions && data.regional_predictions) {
            console.log("Displaying results...");
            displayResults(data);
            showFeedback(true, `✓ Analysis complete: ${size} cases analyzed`);
            document.getElementById("loading").classList.add("hidden");
        } else {
            showError("Invalid response format - missing required fields");
            document.getElementById("loading").classList.add("hidden");
        }
    } catch (error) {
        if (error.name === "AbortError") {
            console.error("Request timeout");
            showError("Request timed out. API may be slow or offline.");
        } else {
            console.error("Simulate error:", error);
            showError(`Error: ${error.message}`);
        }
        document.getElementById("loading").classList.add("hidden");
    } finally {
        isLoading = false;
    }
}

async function simulateRandom() {
    // Same as simulateObvious now - just use the unified /simulate-batch endpoint
    const size = parseInt(document.getElementById("randSize").value) || 500;
    showFeedback(false);
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("results").classList.add("hidden");
    document.getElementById("error").classList.add("hidden");
    
    isLoading = true;
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);
        
        const response = await fetch(`${API_BASE}/simulate-batch?size=${size}`, {
            method: "POST",
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else if (data.prediction_summary && data.disease_predictions && data.regional_predictions) {
            displayResults(data);
            showFeedback(true, `✓ Generated ${size} cases - showing regional outbreak patterns`);
        } else {
            showError("Unexpected response format");
        }
    } catch (error) {
        if (error.name === "AbortError") {
            showError("Request timed out. API may be slow or offline.");
        } else {
            showError(`Error: ${error.message}`);
        }
    } finally {
        document.getElementById("loading").classList.add("hidden");
        isLoading = false;
    }
}

async function runPrediction() {
    if (isLoading) return;
    
    isLoading = true;
    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("results").classList.add("hidden");
    document.getElementById("error").classList.add("hidden");
    showFeedback(false);
    
    try {
        // Create an abort controller with 30-second timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);
        
        const response = await fetch(`${API_BASE}/predict`, { 
            method: "POST",
            signal: controller.signal 
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`API responded with status ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            document.getElementById("loading").classList.add("hidden");
            return;
        }
        
        displayResults(data);
        document.getElementById("loading").classList.add("hidden");
    } catch (error) {
        if (error.name === "AbortError") {
            showError("Request timed out. API may be slow or offline.");
        } else {
            showError(`Prediction failed: ${error.message}`);
        }
        document.getElementById("loading").classList.add("hidden");
    } finally {
        isLoading = false;
    }
}

function displayResults(data) {
    try {
        // Update dashboard summary at top
        if (data.disease_predictions) {
            updateDashboardSummary(data);
        }
        
        // Summary section
        const summ = data.prediction_summary;
        if (summ) {
            document.getElementById("sumDominant").textContent = summ.current_dominant_disease.toUpperCase();
            document.getElementById("sumRisk").textContent = `${(summ.outbreak_probability * 100).toFixed(0)}%`;
            
            const riskColor = STATUS_COLORS[summ.risk_level] || STATUS_COLORS["LOW"];
            document.getElementById("sumLevel").textContent = summ.risk_level;
            document.getElementById("sumLevel").className = `font-bold text-base ${riskColor.text}`;
            
            document.getElementById("sumConfidence").textContent = `${(summ.confidence_score * 100).toFixed(0)}%`;
            document.getElementById("sumTotal").textContent = data.total_analyzed;
            document.getElementById("sumSummary").textContent = summ.summary;
        }
        
        // Disease predictions grid
        const diseaseGrid = document.getElementById("diseaseGrid");
        if (diseaseGrid && data.disease_predictions) {
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
        }
        
        // Regional predictions
        const regionsGrid = document.getElementById("regionsGrid");
        if (regionsGrid && data.regional_predictions) {
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
        }
        
        document.getElementById("results").classList.remove("hidden");
    } catch (error) {
        console.error("Display error:", error);
        throw error;
    }
}

function updateDashboardSummary(data) {
    // Count diseases by status category
    let outbreak = 0, high = 0, rising = 0, monitor = 0, stable = 0;
    
    for (const [disease, pred] of Object.entries(data.disease_predictions)) {
        if (pred.current_cases === 0) continue; // Skip diseases with no cases
        
        if (pred.status === "OUTBREAK LIKELY") {
            outbreak++;
        } else if (pred.status === "RISING") {
            rising++;
        } else if (pred.status === "MONITOR") {
            monitor++;
        } else if (pred.status === "STABLE") {
            stable++;
        }
    }
    
    // Estimate HIGH from regional predictions
    high = data.regional_predictions.filter(r => r.risk_level === "HIGH").length;
    
    document.getElementById("summaryOutbreak").textContent = outbreak;
    document.getElementById("summaryHigh").textContent = high;
    document.getElementById("summaryRising").textContent = rising;
    document.getElementById("summaryMonitor").textContent = monitor;
    document.getElementById("summaryStable").textContent = stable;
    
    document.getElementById("dashboardSummary").classList.remove("hidden");
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
    console.error("Error shown:", message);
    const errorEl = document.getElementById("error");
    const errorMsg = document.getElementById("errorMsg");
    if (errorEl && errorMsg) {
        errorMsg.textContent = message;
        errorEl.classList.remove("hidden");
    }
}

// // Named function for DOMContentLoaded to ensure proper removal
// function autoLoadOnce() {
//     console.log("Page loaded, auto-loading prediction with 500 cases...");
//     document.removeEventListener("DOMContentLoaded", autoLoadOnce);
//     simulateObvious();
// }
// document.addEventListener("DOMContentLoaded", autoLoadOnce);

