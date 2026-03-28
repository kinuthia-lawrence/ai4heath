const API_BASE_URL = 'http://localhost:8000';

// Status colors  
const statusColors = {
    'OUTBREAK': { bg: 'bg-red-100', border: 'border-red-400', text: 'text-red-800', dot: 'bg-red-500' },
    'MONITOR': { bg: 'bg-yellow-100', border: 'border-yellow-400', text: 'text-yellow-800', dot: 'bg-yellow-500' },
    'OK': { bg: 'bg-green-100', border: 'border-green-400', text: 'text-green-800', dot: 'bg-green-500' }
};

// Check API on load
document.addEventListener('DOMContentLoaded', () => {
    checkApiHealth();
});

async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/ping`);
        if (response.ok) {
            document.getElementById('statusText').textContent = '✓ API is Running';
            document.getElementById('statusText').className = 'text-sm text-green-600';
        } else {
            document.getElementById('statusText').textContent = '✗ API Error';
            document.getElementById('statusText').className = 'text-sm text-red-600';
        }
    } catch (error) {
        document.getElementById('statusText').textContent = '✗ Connection Failed';
        document.getElementById('statusText').className = 'text-sm text-red-600';
    }
}

async function simulateObvious() {
    const size = parseInt(document.getElementById('obvSize').value) || 50;
    if (size < 5 || size > 500) {
        alert('Size must be 5-500');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/simulate-batch?size=${size}&mode=obvious`, { method: 'POST' });
        const data = await response.json();
        if (data.status === 'success') {
            alert(`Generated ${data.cases_generated} obvious pattern cases`);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function simulateRandom() {
    const size = parseInt(document.getElementById('randSize').value) || 50;
    if (size < 5 || size > 500) {
        alert('Size must be 5-500');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/simulate-batch?size=${size}&mode=random`, { method: 'POST' });
        const data = await response.json();
        if (data.status === 'success') {
            alert(`Generated ${data.cases_generated} random pattern cases`);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function runPrediction() {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');

    loading.classList.remove('hidden');
    results.classList.add('hidden');
    error.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/predict`, { method: 'POST' });
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        displayResults(data);
        loading.classList.add('hidden');
        results.classList.remove('hidden');

    } catch (err) {
        loading.classList.add('hidden');
        error.classList.remove('hidden');
        document.getElementById('errorMsg').textContent = err.message;
    }
}

function displayResults(data) {
    // Stats
    document.getElementById('totalCases').textContent = data.total_analyzed || 0;
    document.getElementById('timestamp').textContent = data.timestamp;
    
    const outbreakCount = (data.regions || []).filter(r => r.status === 'OUTBREAK').length;
    document.getElementById('outbreakCount').textContent = outbreakCount;

    // Nationwide
    const nationwide = document.getElementById('nationwide');
    nationwide.innerHTML = '';
    
    if (data.nationwide) {
        Object.entries(data.nationwide).forEach(([disease, details]) => {
            const colors = statusColors[details.status] || statusColors.OK;
            const item = document.createElement('div');
            item.className = `${colors.bg} border-l-4 ${colors.border} p-3 rounded`;
            item.innerHTML = `
                <div class="flex justify-between">
                    <div>
                        <strong class="capitalize">${disease}</strong>
                        <p class="text-sm">${details.cases} cases</p>
                    </div>
                    <span class="font-bold ${colors.text}">${details.status}</span>
                </div>
            `;
            nationwide.appendChild(item);
        });
    }

    // Regions
    const regions = document.getElementById('regions');
    regions.innerHTML = '';
    
    if (data.regions && data.regions.length > 0) {
        data.regions.forEach(region => {
            const colors = statusColors[region.status] || statusColors.OK;
            const card = document.createElement('div');
            card.className = `${colors.bg} border-l-4 ${colors.border} p-4 rounded`;
            
            let diseaseBreakdown = '';
            if (region.diseases && Object.keys(region.diseases).length > 0) {
                diseaseBreakdown = '<div class="text-sm mt-2 pt-2 border-t"><strong>Diseases:</strong> ' +
                    Object.entries(region.diseases).map(([d, c]) => `${d}:${c}`).join(' | ') + '</div>';
            }
            
            card.innerHTML = `
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="font-bold">${region.region}</h4>
                        <p class="text-sm">${region.total_cases} total cases</p>
                        <p class="text-sm">Concentration: ${region.concentration.toFixed(1)}%</p>
                        ${diseaseBreakdown}
                    </div>
                    <span class="font-bold ${colors.text} text-lg">${region.status}</span>
                </div>
            `;
            regions.appendChild(card);
        });
    }
}

