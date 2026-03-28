import { useEffect, useState } from 'react'
import { CircleMarker, MapContainer, TileLayer, useMap } from 'react-leaflet'
import { MOCK_THREATS, MOCK_PROFILE } from '../../data/mock'
import type { Threat } from '../../types'
import { ThreatMarker } from './ThreatMarker'
import { MonitoredZone } from './MonitoredZone'
import { AlertBottomSheet } from './AlertBottomSheet'

const MAP_CENTER: [number, number] = [41.882, -87.631]
const MAP_ZOOM = 14
const MAP_MIN_ZOOM = 3
// Clamp panning to the world bounds so the viewport never shows white space outside tiles
const WORLD_BOUNDS: [[number, number], [number, number]] = [[-85.051129, -180], [85.051129, 180]]

const TILE_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const TILE_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'

function FlyTo({ position }: { position: [number, number] }) {
  const map = useMap()
  useEffect(() => {
    map.flyTo(position, Math.max(map.getZoom(), 15), { duration: 1.5 })
  }, [position, map])
  return null
}

export function MapView() {
  const [selectedThreat, setSelectedThreat] = useState<Threat | null>(null)
  const [userPos, setUserPos] = useState<[number, number] | null>(null)

  const homeArea = MOCK_PROFILE.areas.find((a) => a.name === 'HOME')

  function locateUser() {
    navigator.geolocation.getCurrentPosition(
      (pos) => setUserPos([pos.coords.latitude, pos.coords.longitude]),
      () => { /* permission denied or unavailable — keep default center */ },
      { enableHighAccuracy: true, timeout: 10000 },
    )
  }

  useEffect(() => {
    locateUser()
  }, [])

  return (
    <div className="relative w-full h-full">
      {/* z-0 creates an isolated stacking context so Leaflet's internal z-indexes (400–700) don't bleed out */}
      <div className="absolute inset-0 z-0">
      <MapContainer
        center={MAP_CENTER}
        zoom={MAP_ZOOM}
        minZoom={MAP_MIN_ZOOM}
        maxBounds={WORLD_BOUNDS}
        maxBoundsViscosity={1}
        className="w-full h-full"
        zoomControl
        attributionControl={false}
      >
        <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} />

        {userPos && <FlyTo position={userPos} />}

        {userPos && (
          <>
            <CircleMarker
              center={userPos}
              radius={10}
              pathOptions={{ color: '#ffffff', fillColor: '#4d9fff', fillOpacity: 1, weight: 2 }}
            />
            <CircleMarker
              center={userPos}
              radius={20}
              pathOptions={{ color: '#4d9fff', fillColor: '#4d9fff', fillOpacity: 0.15, weight: 1 }}
            />
          </>
        )}

        {homeArea && <MonitoredZone area={homeArea} />}

        {MOCK_THREATS.map((threat) => (
          <ThreatMarker
            key={threat.id}
            threat={threat}
            isSelected={selectedThreat?.id === threat.id}
            onSelect={setSelectedThreat}
          />
        ))}
      </MapContainer>
      </div>

      {selectedThreat && (
        <AlertBottomSheet
          threat={selectedThreat}
          onClose={() => setSelectedThreat(null)}
          onViewDetails={(t) => console.log('View details for', t.id)}
        />
      )}

      <button
        onClick={locateUser}
        className="fixed bottom-44 right-6 w-12 h-12 bg-surface-container border-2 border-black shadow-hard active:translate-x-[2px] active:translate-y-[2px] active:shadow-none flex items-center justify-center z-40 transition-none"
        aria-label="Center map on my location"
      >
        <span className="material-symbols-outlined text-on-surface text-2xl">my_location</span>
      </button>

      <button
        className="fixed bottom-24 right-6 w-16 h-16 bg-primary-container border-[3px] border-black shadow-hard active:translate-x-[2px] active:translate-y-[2px] active:shadow-none flex items-center justify-center z-40 transition-none"
        aria-label="Add new alert"
      >
        <span className="material-symbols-outlined text-on-primary-container text-4xl font-bold">add</span>
      </button>
    </div>
  )
}
