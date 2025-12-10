"use strict";

// ================= Global Variables =================
let map;
let geoJsonLayer;       // Polygon layer
let greenspaceLayer;    // Point layer
let allNeighbourhoods = []; 
let allGreenspaces = [];    

// Colour Scheme (Red -> Green)
const COLORS = {
    q1: '#d73027', // 0-25% (Poor)
    q2: '#fc8d59', // 25-50%
    q3: '#91cf60', // 50-75%
    q4: '#1a9850'  // 75-100% (Good)
};

// ================= 1. Initialization =================
document.addEventListener("DOMContentLoaded", () => {
    // 1.1 Initialize Map
    map = L.map('mapid').setView([55.95, -3.19], 12);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // 1.2 Fix: Force map resize to fill container
    setTimeout(function() {
        map.invalidateSize();
    }, 100);

    // 1.3 Event Listeners for UI
    document.getElementById('dataset-selector').addEventListener('change', updateMapDisplay);
    document.querySelectorAll('.quantile-filter').forEach(cb => {
        cb.addEventListener('change', updateMapDisplay);
    });

    // 1.4 Load Data
    loadData();
});

// ================= 2. Data Loading =================
function loadData() {
    // 2.1 Load Greenspaces (Points)
    fetch(window.API_GREENSPACES)
        .then(res => res.json())
        .then(data => {
            allGreenspaces = data.features;
            greenspaceLayer = L.geoJSON(data, {
                pointToLayer: (feature, latlng) => {
                    // Size depends on quality score
                    let r = feature.properties.quality / 10;
                    return L.circleMarker(latlng, {
                        radius: r,
                        fillColor: "#27ae60",
                        color: "#fff",
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    });
                },
                onEachFeature: (feature, layer) => {
                    layer.bindPopup(`
                        <b>🏞️ ${feature.properties.name}</b><br>
                        Type: ${feature.properties.type}<br>
                        Quality Score (PQA): <b>${feature.properties.quality}</b><br>
                        <small>Facilities: ${feature.properties.facilities}</small>
                    `);
                }
            }).addTo(map);
        });

    // 2.2 Load Neighbourhoods (Polygons)
    fetch(window.API_NEIGHBOURHOODS)
        .then(res => res.json())
        .then(data => {
            allNeighbourhoods = data.features;
            // Initialize layer but style it via updateMapDisplay
            geoJsonLayer = L.geoJSON(data, {
                onEachFeature: onEachNeighbourhood
            }).addTo(map);
            
            updateMapDisplay(); // Initial render
        });
}

// ================= 3. Core Logic: Rendering & Filtering =================
function updateMapDisplay() {
    if (!geoJsonLayer) return;

    // A. Get selected metric (health, simd, stress)
    const metric = document.getElementById('dataset-selector').value;
    
    // B. Get active quantiles
    const activeQuantiles = Array.from(document.querySelectorAll('.quantile-filter:checked'))
                                 .map(cb => parseInt(cb.value));

    // C. Calculate Quantiles dynamically
    const values = allNeighbourhoods.map(f => f.properties[metric]).sort((a, b) => a - b);
    const q25 = values[Math.floor(values.length * 0.25)];
    const q50 = values[Math.floor(values.length * 0.50)];
    const q75 = values[Math.floor(values.length * 0.75)];

    // D. Style each polygon
    geoJsonLayer.eachLayer(layer => {
        const val = layer.feature.properties[metric];
        let quantile = 0;
        let color = '#ccc';

        // Logic: Lower values are usually "worse" (Red)
        // Exception: For SIMD, 1 is worst. For Stress, High is worst. 
        // To keep it simple, we treat Low Value = Red, High Value = Green for this demo.
        if (val <= q25) { quantile = 1; color = COLORS.q1; }
        else if (val <= q50) { quantile = 2; color = COLORS.q2; }
        else if (val <= q75) { quantile = 3; color = COLORS.q3; }
        else { quantile = 4; color = COLORS.q4; }

        // Visibility check
        if (activeQuantiles.includes(quantile)) {
            layer.setStyle({
                fillColor: color,
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.6
            });
            layer.getElement().style.pointerEvents = 'auto'; 
        } else {
            layer.setStyle({
                fillOpacity: 0,
                opacity: 0
            });
            layer.getElement().style.pointerEvents = 'none'; 
        }
    });
}

// ================= 4. Interaction: Click & Sidebar =================
function onEachNeighbourhood(feature, layer) {
    layer.on('click', (e) => {
        // Highlight effect
        geoJsonLayer.resetStyle(); 
        updateMapDisplay(); // Re-apply base styles
        
        e.target.setStyle({
            weight: 5,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.8
        });

        // Update Sidebar content
        const props = feature.properties;
        const html = `
            <h3 style="color:#2c3e50; margin-top:0; border-bottom:2px solid #3498db; padding-bottom:10px;">
                ${props.name}
            </h3>
            <table style="width:100%; line-height:1.8; color:#2c3e50;">
                <tr><td>🏥 <b>Health Index:</b></td> <td>${props.health} / 100</td></tr>
                <tr><td>📉 <b>SIMD Rank:</b></td> <td>Decile ${props.simd}</td></tr>
                <tr><td>⚠️ <b>Stress Level:</b></td> <td>${props.stress}</td></tr>
                <tr><td>👥 <b>Population:</b></td> <td>${props.pop}</td></tr>
            </table>
            <div style="margin-top:15px; padding:10px; background:#f0f3f4; border-radius:5px; font-size:0.9em; color:#555;">
                <strong>💡 Recommendation:</strong><br>
                ${getRecommendation(props.health)}
            </div>
        `;
        document.getElementById('info-content').innerHTML = html;

        // Setup Navigation button
        setupNavigation(props);
    });
}

function getRecommendation(health) {
    if (health < 60) return "Critical intervention needed. Prioritize green space quality improvements to mitigate high stress.";
    if (health < 80) return "Moderate health levels. Promote community activities in existing parks.";
    return "Healthy zone. Maintain current high-quality green infrastructure.";
}

// ================= 5. Navigation Logic =================
function setupNavigation(props) {
    let bestDist = Infinity;
    let target = null;
    
    // Find nearest High Quality Greenspace (>80)
    allGreenspaces.forEach(gs => {
        const d = Math.sqrt(Math.pow(gs.geometry.coordinates[1] - props.lat, 2) + 
                            Math.pow(gs.geometry.coordinates[0] - props.lon, 2));
        if (d < bestDist && gs.properties.quality > 80) {
            bestDist = d;
            target = gs;
        }
    });

    const navContainer = document.getElementById('nav-container');
    const navBtn = document.getElementById('nav-btn');

    if (target) {
        navContainer.style.display = 'block';
        const url = `https://www.google.com/maps/dir/?api=1&origin=${props.lat},${props.lon}&destination=${target.geometry.coordinates[1]},${target.geometry.coordinates[0]}&travelmode=walking`;
        navBtn.href = url;
        navBtn.innerHTML = `🚶 Walk to: ${target.properties.name}`;
    } else {
        navContainer.style.display = 'none';
    }
}

// ================= 6. CSV Download =================
window.downloadCSV = function() {
    if (allNeighbourhoods.length === 0) {
        alert("No data available to download.");
        return;
    }

    const headers = ["ID", "Name", "Health Index", "SIMD Rank", "Stress Index", "Population", "Latitude", "Longitude"];
    
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += headers.join(",") + "\r\n";

    allNeighbourhoods.forEach(item => {
        const p = item.properties;
        const row = [
            p.id,
            `"${p.name}"`, 
            p.health,
            p.simd,
            p.stress,
            p.pop,
            p.lat,
            p.lon
        ];
        csvContent += row.join(",") + "\r\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "edinburgh_analytics_data.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};