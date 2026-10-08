import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

const MapUpdater = ({ routeCoords }) => {
  const map = useMap();
  useEffect(() => {
    if (routeCoords && routeCoords.length > 0) {
      const bounds = L.latLngBounds(routeCoords);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [routeCoords, map]);
  return null;
};

export default function RouteMap({ selectedRoute }) {
  const [fleetData, setFleetData] = useState(null);

  useEffect(() => {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';
    axios.get(`${API_BASE}/logistics/fleet-simulation`)
      .then(res => setFleetData(res.data))
      .catch(err => console.error("Error fetching fleet data:", err));
  }, []);

  if (!fleetData) return <div className="h-96 w-full bg-slate-100 animate-pulse rounded-xl"></div>;

  const activeRouteCoords = fleetData.routes[selectedRoute] || [];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 h-full min-h-[400px] flex flex-col">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Live AIS Maritime Corridors</h3>
      <div className="flex-grow rounded-lg overflow-hidden border border-slate-200 relative z-0" style={{ minHeight: '300px' }}>
        <MapContainer center={[5.0, 75.0]} zoom={3} scrollWheelZoom={false} attributionControl={false} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url="https://api.thunderforest.com/transport-dark/{z}/{x}/{y}.png?apikey=9c1bc75da69a4354aaea9183a13b293d"
            attribution='&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />

          {activeRouteCoords.length > 0 && (
            <Polyline positions={activeRouteCoords} color="#00E5FF" weight={4} dashArray="8, 12" opacity={0.9} />
          )}
          {fleetData.vessels.map(vessel => (
            <Marker key={vessel.id} position={vessel.position}>
              <Popup>
                <strong>{vessel.name}</strong><br />
                IMO: {vessel.imo}<br />
                Speed: {vessel.speed} knots<br />
                ETA: {vessel.eta}
              </Popup>
            </Marker>
          ))}
          <MapUpdater routeCoords={activeRouteCoords} />
        </MapContainer>
      </div>
    </div>
  );
}
