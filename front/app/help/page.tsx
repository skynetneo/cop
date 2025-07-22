"use client";

import dynamic from "next/dynamic";
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import { Agency } from "@/lib/types";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { divIcon } from "leaflet";

// Disable SSR for MapCanvas
const MapCanvas = () => {
  const searchParams = useSearchParams();
  const agenciesJson = searchParams.get('agencies');
  const category = searchParams.get('category');
  
  let agencies: Agency[] = [];
  try {
    if (agenciesJson) {
      agencies = JSON.parse(decodeURIComponent(agenciesJson));
    }
  } catch (error) {
    console.error("Failed to parse agencies JSON:", error);
  }

  // Calculate center of map
  const centerLat = agencies.length > 0 ? agencies.reduce((sum, a) => sum + a.latitude, 0) / agencies.length : 34.0522;
  const centerLng = agencies.length > 0 ? agencies.reduce((sum, a) => sum + a.longitude, 0) / agencies.length : -118.2437;
  
  return (
    <main className="h-screen w-screen">
      <h1 className="absolute top-4 left-1/2 -translate-x-1/2 z-10 bg-white p-2 rounded-lg shadow-md font-bold">
        {category ? `${category} Agencies` : 'Local Resources'}
      </h1>
      <MapContainer
        className="w-full h-full"
        center={[centerLat, centerLng]}
        zoom={12}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {agencies.map((agency, index) => (
          <Marker 
            key={agency.id} 
            position={[agency.latitude, agency.longitude]}
            icon={divIcon({
              className: "bg-transparent",
              html: `<div class="bg-blue-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold border-2 border-white shadow-lg">${index + 1}</div>`,
            })}
          >
            <Popup>
              <div className="font-bold text-md">{agency.name}</div>
              <div className="text-sm">{agency.address}</div>
              <div className="text-sm">Contact: {agency.contactInformation || 'N/A'}</div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </main>
  );
};

export default function FindHelpPage() {
  return (
    <Suspense fallback={<div>Loading map...</div>}>
      <MapCanvas />
    </Suspense>
  )
}