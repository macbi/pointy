var map = L.map('map').setView([52.40692, 16.92993], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

$(function () {
    function addMarker(lat, lon, name) {
        L.marker([lat, lon]).addTo(map).bindPopup(name);
    }

    // TODO fix this function
    function getCenterAndFlyTo(LatLngs) {
        centroid = centroid(LatLngs);

        console.log(centroid);

        map.flyTo(centroid.lat, centroid.lng, 15);
    }

    function clearMap() {
        map.eachLayer(function (layer) {
            if (!layer._url) {
                map.removeLayer(layer);
            }
        });
    }

    function LatLng(lat, lon){
        return LatLng(lat, lon);
    }
    eel.expose(getCenterAndFlyTo); 
    eel.expose(addMarker);
    eel.expose(clearMap);
    eel.expose(LatLng);
});