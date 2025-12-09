"use strict";

let map = L.map('mapid').setView([55.948162, -3.184111], 12);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let greenspaceLayer = L.geoJSON(null).addTo(map);

function loadGreenspace(postcode) {
    // 这里用模板里注入的全局变量
    const baseUrl = window.GREENSAPCE_API_URL || "/api/greenspace";
    const url = `${baseUrl}?postcode=${encodeURIComponent(postcode)}`;

    fetch(url)
      .then(response => response.json())
      .then(data => {
          greenspaceLayer.clearLayers();
          greenspaceLayer.addData(data);
          if (greenspaceLayer.getLayers().length > 0) {
              map.fitBounds(greenspaceLayer.getBounds());
          }
      })
      .catch(err => {
          console.error(err);
          alert("加载数据失败");
      });
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("search-form");
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const postcode = document.getElementById("postcode").value.trim();
        if (postcode) {
            loadGreenspace(postcode);
        }
    });
});
