var map = L.map('map').setView([52.40692, 16.92993], 13);

var getCentroid = function (arr) { 
    return arr.reduce(function (x,y) {
        return [x[0] + y[0]/arr.length, x[1] + y[1]/arr.length] 
    }, [0,0]) 
}

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

$(function () {
    function addMarker(lat, lon, popupName) {
        console.log("Adding marker: " + lat + ", " + lon + " " + popupName);
        try { L.marker([lat, lon]).addTo(map).bindPopup(String(popupName));} catch (e) { console.log(e); }
    }

    function getCenterAndFlyTo(LatLngs) {
        var centroid = getCentroid(LatLngs); 

        console.log(centroid);

        map.flyTo([centroid[0], centroid[1]], 12);
    }

    function clearMap() {
        map.eachLayer(function (layer) {
            if (!layer._url) {
                map.removeLayer(layer);
            }
        });
    }

    eel.expose(getCenterAndFlyTo);
    eel.expose(addMarker);
    eel.expose(clearMap);

});