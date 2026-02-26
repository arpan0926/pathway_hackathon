import { useEffect,  useCallback } from 'react';
import Map, { Marker, Source, Layer, Popup, NavigationControl } from 'react-map-gl';
import { Box, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { telemetryApi } from '../../api/telemetry';

import { useStore } from '../../store/useStore';
import 'mapbox-gl/dist/mapbox-gl.css';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;

// Exact route waypoints from gps_simulator.py
// Exact route waypoints from gps_simulator.py
const ROUTE_WAYPOINTS: Record<string, [number, number][]> = {
  SH001: [
    [72.8777, 19.0760],  // Mumbai
    [78.9629, 20.5937],  // Madhya Pradesh
    [77.4126, 23.2599],  // Bhopal
    [75.7873, 26.9124],  // Jaipur
    [77.2090, 28.6139],  // Delhi
  ],
  SH002: [
    [77.5946, 12.9716],  // Bangalore
    [78.1182, 12.8406],  // Waypoint
    [80.2707, 13.0827],  // Chennai
  ],
  SH003: [
    [88.3639, 22.5726],  // Kolkata
    [79.0882, 21.1458],  // Nagpur
    [79.0882, 19.0760],  // Waypoint
    [78.4867, 17.3850],  // Hyderabad
  ],
  SH004: [
    [73.8567, 18.5204],  // Pune
    [73.7898, 19.9975],  // Nashik
    [72.8311, 21.1702],  // Surat
    [72.5714, 23.0225],  // Ahmedabad
  ],
};

const SHIPMENT_CONFIG: Record<string, { color: string; label: string; route: string }> = {
  SH001: { color: '#00E5FF', label: 'Mumbai → Delhi',       route: 'VH001' },
  SH002: { color: '#FF6B35', label: 'Bangalore → Chennai',  route: 'VH002' },
  SH003: { color: '#A8FF3E', label: 'Kolkata → Hyderabad',  route: 'VH003' },
  SH004: { color: '#FFB300', label: 'Pune → Ahmedabad',     route: 'VH004' },
};

// Add new cities to the CITIES array
const CITIES: { name: string; lon: number; lat: number }[] = [
  { name: 'Mumbai',     lon: 72.8777, lat: 19.0760 },
  { name: 'Delhi',      lon: 77.2090, lat: 28.6139 },
  { name: 'Bangalore',  lon: 77.5946, lat: 12.9716 },
  { name: 'Chennai',    lon: 80.2707, lat: 13.0827 },
  { name: 'Kolkata',    lon: 88.3639, lat: 22.5726 },
  { name: 'Hyderabad',  lon: 78.4867, lat: 17.3850 },
  { name: 'Pune',       lon: 73.8567, lat: 18.5204 },
  { name: 'Ahmedabad',  lon: 72.5714, lat: 23.0225 },
  { name: 'Bhopal',     lon: 77.4126, lat: 23.2599 },
  { name: 'Jaipur',     lon: 75.7873, lat: 26.9124 },
  { name: 'Nagpur',     lon: 79.0882, lat: 21.1458 },
  { name: 'Nashik',     lon: 73.7898, lat: 19.9975 },
  { name: 'Surat',      lon: 72.8311, lat: 21.1702 },
];

interface LivePosition {
  shipment_id: string;
  lat: number;
  lon: number;
  speed_kmph: number;
  load_status: string;
  ts: string;
}

interface PopupInfo extends LivePosition {}

export const ShipmentMap = () => {
  const [positions, setPositions] = useState<Record<string, LivePosition>>({});
  const [trails, setTrails] = useState<Record<string, [number, number][]>>({});
  const [popupInfo, setPopupInfo] = useState<PopupInfo | null>(null);
  const [pulseStates, setPulseStates] = useState<Record<string, boolean>>({});
  const { setSelectedShipment, updatePosition } = useStore();

  // Poll latest telemetry for each shipment every 2 seconds
// Poll latest telemetry for all 4 shipments
const { data: sh001 } = useQuery({
  queryKey: ['live-telemetry', 'SH001'],
  queryFn: () => telemetryApi.getLatest('SH001').then(r => r.data),
  refetchInterval: 2000,
  retry: false,
});

const { data: sh002 } = useQuery({
  queryKey: ['live-telemetry', 'SH002'],
  queryFn: () => telemetryApi.getLatest('SH002').then(r => r.data),
  refetchInterval: 2000,
  retry: false,
});

const { data: sh003 } = useQuery({
  queryKey: ['live-telemetry', 'SH003'],
  queryFn: () => telemetryApi.getLatest('SH003').then(r => r.data),
  refetchInterval: 2000,
  retry: false,
});

const { data: sh004 } = useQuery({
  queryKey: ['live-telemetry', 'SH004'],
  queryFn: () => telemetryApi.getLatest('SH004').then(r => r.data),
  refetchInterval: 2000,
  retry: false,
});

// Get trails for all 4
const { data: trail001 } = useQuery({
  queryKey: ['trail', 'SH001'],
  queryFn: () => telemetryApi.getAll('SH001', 30).then(r => r.data),
  refetchInterval: 4000,
  retry: false,
});

const { data: trail002 } = useQuery({
  queryKey: ['trail', 'SH002'],
  queryFn: () => telemetryApi.getAll('SH002', 30).then(r => r.data),
  refetchInterval: 4000,
  retry: false,
});

const { data: trail003 } = useQuery({
  queryKey: ['trail', 'SH003'],
  queryFn: () => telemetryApi.getAll('SH003', 30).then(r => r.data),
  refetchInterval: 4000,
  retry: false,
});

const { data: trail004 } = useQuery({
  queryKey: ['trail', 'SH004'],
  queryFn: () => telemetryApi.getAll('SH004', 30).then(r => r.data),
  refetchInterval: 4000,
  retry: false,
});

// Update positions when data arrives (add sh003 and sh004)
useEffect(() => {
  if (sh003) {
    setPositions(prev => ({ ...prev, SH003: sh003 }));
    updatePosition('SH003', sh003);
    setPulseStates(prev => ({ ...prev, SH003: true }));
    setTimeout(() => setPulseStates(prev => ({ ...prev, SH003: false })), 600);
  }
}, [sh003]);

useEffect(() => {
  if (sh004) {
    setPositions(prev => ({ ...prev, SH004: sh004 }));
    updatePosition('SH004', sh004);
    setPulseStates(prev => ({ ...prev, SH004: true }));
    setTimeout(() => setPulseStates(prev => ({ ...prev, SH004: false })), 600);
  }
}, [sh004]);

// Build trails (add sh003 and sh004)
useEffect(() => {
  if (trail003 && trail003.length > 0) {
    const coords: [number, number][] = trail003.slice().reverse().map(t => [t.lon, t.lat]);
    setTrails(prev => ({ ...prev, SH003: coords }));
  }
}, [trail003]);

useEffect(() => {
  if (trail004 && trail004.length > 0) {
    const coords: [number, number][] = trail004.slice().reverse().map(t => [t.lon, t.lat]);
    setTrails(prev => ({ ...prev, SH004: coords }));
  }
}, [trail004]);

  // Update positions when data arrives
  useEffect(() => {
    if (sh001) {
      setPositions(prev => ({ ...prev, SH001: sh001 }));
      updatePosition('SH001', sh001);
      // Trigger pulse animation
      setPulseStates(prev => ({ ...prev, SH001: true }));
      setTimeout(() => setPulseStates(prev => ({ ...prev, SH001: false })), 600);
    }
  }, [sh001]);

  useEffect(() => {
    if (sh002) {
      setPositions(prev => ({ ...prev, SH002: sh002 }));
      updatePosition('SH002', sh002);
      setPulseStates(prev => ({ ...prev, SH002: true }));
      setTimeout(() => setPulseStates(prev => ({ ...prev, SH002: false })), 600);
    }
  }, [sh002]);

  // Build trail coordinates
  useEffect(() => {
    if (trail001 && trail001.length > 0) {
      const coords: [number, number][] = trail001
        .slice()
        .reverse()
        .map(t => [t.lon, t.lat]);
      setTrails(prev => ({ ...prev, SH001: coords }));
    }
  }, [trail001]);

  useEffect(() => {
    if (trail002 && trail002.length > 0) {
      const coords: [number, number][] = trail002
        .slice()
        .reverse()
        .map(t => [t.lon, t.lat]);
      setTrails(prev => ({ ...prev, SH002: coords }));
    }
  }, [trail002]);

  const handleMarkerClick = useCallback((shipId: string, pos: LivePosition) => {
    setPopupInfo(pos);
    setSelectedShipment(shipId);
  }, [setSelectedShipment]);

  const hasData = Object.keys(positions).length > 0;

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <Map
        mapboxAccessToken={MAPBOX_TOKEN}
        initialViewState={{
          longitude: 77.5,
          latitude: 21.0,
          zoom: 4.8,
        }}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/dark-v11"
      >
        <NavigationControl position="top-right" />

        {/* ── Static route lines ── */}
        {Object.entries(ROUTE_WAYPOINTS).map(([shipId, coords]) => (
          <Source
            key={`route-${shipId}`}
            id={`route-${shipId}`}
            type="geojson"
            data={{
              type: 'Feature',
              geometry: { type: 'LineString', coordinates: coords },
              properties: {},
            }}
            lineMetrics={true}
          >
            <Layer
              id={`route-line-${shipId}`}
              type="line"
              paint={{
                'line-color': SHIPMENT_CONFIG[shipId]?.color ?? '#888',
                'line-width': 1.5,
                'line-opacity': 0.3,
                'line-dasharray': [3, 3],
              }}
            />
          </Source>
        ))}

        {/* ── Live trail lines (breadcrumb from real telemetry) ── */}
        {Object.entries(trails).map(([shipId, coords]) =>
          coords.length >= 2 ? (
            <Source
              key={`trail-${shipId}`}
              id={`trail-${shipId}`}
              type="geojson"
              data={{
                type: 'Feature',
                geometry: { type: 'LineString', coordinates: coords },
                properties: {},
              }}
              lineMetrics={true}
            >
              <Layer
                id={`trail-line-${shipId}`}
                type="line"
                paint={{
                  'line-color': SHIPMENT_CONFIG[shipId]?.color ?? '#888',
                  'line-width': 3,
                  'line-opacity': 0.85,
                  'line-gradient': [
                    'interpolate',
                    ['linear'],
                    ['line-progress'],
                    0, 'rgba(0,0,0,0)',
                    1, SHIPMENT_CONFIG[shipId]?.color ?? '#888',
                  ],
                }}
                layout={{ 'line-cap': 'round', 'line-join': 'round' }}
              />
            </Source>
          ) : null
        )}

        {/* ── City waypoint dots ── */}
        {CITIES.map(city => (
          <Marker key={city.name} longitude={city.lon} latitude={city.lat}>
            <Box sx={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Box sx={{
                width: 6, height: 6,
                borderRadius: '50%',
                background: '#ffffff30',
                border: '1px solid #ffffff50',
              }} />
              <Typography sx={{
                position: 'absolute',
                top: 8,
                left: '50%',
                transform: 'translateX(-50%)',
                fontSize: 9,
                color: '#ffffff60',
                whiteSpace: 'nowrap',
                letterSpacing: 0.5,
                fontFamily: 'monospace',
                pointerEvents: 'none',
              }}>
                {city.name}
              </Typography>
            </Box>
          </Marker>
        ))}

        {/* ── Live truck markers ── */}
        {Object.entries(positions).map(([shipId, pos]) => {
          const cfg = SHIPMENT_CONFIG[shipId];
          if (!cfg) return null;
          const isPulsing = pulseStates[shipId];
          const isMoving = pos.speed_kmph > 5;
          const markerColor = pos.speed_kmph > 40 ? cfg.color
            : pos.speed_kmph > 0 ? '#FFB300'
            : '#F44336';

          return (
            <Marker
              key={shipId}
              longitude={pos.lon}
              latitude={pos.lat}
              onClick={() => handleMarkerClick(shipId, pos)}
            >
              <Box
                sx={{
                  position: 'relative',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {/* Outer pulse ring */}
                {isMoving && (
                  <Box sx={{
                    position: 'absolute',
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    border: `1.5px solid ${markerColor}`,
                    opacity: isPulsing ? 0.8 : 0.2,
                    transform: isPulsing ? 'scale(1.8)' : 'scale(1)',
                    transition: 'all 0.6s ease-out',
                    pointerEvents: 'none',
                  }} />
                )}

                {/* Inner glow */}
                <Box sx={{
                  position: 'absolute',
                  width: 20,
                  height: 20,
                  borderRadius: '50%',
                  background: `radial-gradient(circle, ${markerColor}40 0%, transparent 70%)`,
                  pointerEvents: 'none',
                }} />

                {/* Truck icon */}
                <Box sx={{
                  width: 28,
                  height: 28,
                  borderRadius: '50%',
                  background: `${markerColor}22`,
                  border: `2px solid ${markerColor}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 13,
                  boxShadow: `0 0 ${isPulsing ? 16 : 8}px ${markerColor}80`,
                  transition: 'box-shadow 0.3s ease',
                  zIndex: 10,
                }}>
                  🚛
                </Box>

                {/* Speed badge */}
                <Box sx={{
                  position: 'absolute',
                  bottom: -18,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: '#0A0A14EE',
                  border: `1px solid ${markerColor}60`,
                  borderRadius: 4,
                  px: 0.6,
                  py: 0.1,
                  whiteSpace: 'nowrap',
                }}>
                  <Typography sx={{ fontSize: 9, color: markerColor, fontFamily: 'monospace', fontWeight: 700 }}>
                    {pos.speed_kmph.toFixed(0)} km/h
                  </Typography>
                </Box>
              </Box>
            </Marker>
          );
        })}

        {/* ── Popup on click ── */}
        {popupInfo && (
          <Popup
            longitude={popupInfo.lon}
            latitude={popupInfo.lat}
            onClose={() => setPopupInfo(null)}
            offset={20}
            closeButton={true}
          >
            <Box sx={{ p: 0.5, minWidth: 180, background: '#0D0D1A' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography sx={{ fontWeight: 700, fontSize: 13, fontFamily: 'monospace', color: SHIPMENT_CONFIG[popupInfo.shipment_id]?.color ?? '#fff' }}>
                  {popupInfo.shipment_id}
                </Typography>
                <Box sx={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: popupInfo.speed_kmph > 40 ? '#00E5FF' : popupInfo.speed_kmph > 0 ? '#FFB300' : '#F44336',
                  boxShadow: `0 0 6px ${popupInfo.speed_kmph > 40 ? '#00E5FF' : '#FFB300'}`,
                }} />
              </Box>

              {[
                ['Route', SHIPMENT_CONFIG[popupInfo.shipment_id]?.label ?? '—'],
                ['Speed', `${popupInfo.speed_kmph.toFixed(1)} km/h`],
                ['Status', popupInfo.load_status],
                ['Lat', popupInfo.lat.toFixed(5)],
                ['Lon', popupInfo.lon.toFixed(5)],
                ['Updated', new Date(popupInfo.ts).toLocaleTimeString()],
              ].map(([label, value]) => (
                <Box key={label} sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, mb: 0.3 }}>
                  <Typography sx={{ fontSize: 10, color: '#666' }}>{label}</Typography>
                  <Typography sx={{ fontSize: 10, color: '#ccc', fontFamily: 'monospace' }}>{value}</Typography>
                </Box>
              ))}
            </Box>
          </Popup>
        )}
      </Map>

      {/* ── Legend overlay ── */}
      <Box sx={{
        position: 'absolute',
        bottom: 32,
        left: 16,
        background: '#0A0A14DD',
        border: '1px solid #1E1E2E',
        borderRadius: 2,
        px: 2,
        py: 1.5,
        backdropFilter: 'blur(8px)',
      }}>
        {Object.entries(SHIPMENT_CONFIG).map(([shipId, cfg]) => {
          const pos = positions[shipId];
          return (
            <Box key={shipId} sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.8, '&:last-child': { mb: 0 } }}>
              <Box sx={{
                width: 10, height: 10, borderRadius: '50%',
                background: cfg.color,
                boxShadow: `0 0 6px ${cfg.color}`,
                flexShrink: 0,
              }} />
              <Box>
                <Typography sx={{ fontSize: 11, fontWeight: 600, color: cfg.color, fontFamily: 'monospace' }}>
                  {shipId}
                </Typography>
                <Typography sx={{ fontSize: 9, color: '#555' }}>{cfg.label}</Typography>
              </Box>
              {pos && (
                <Typography sx={{ fontSize: 10, color: '#888', fontFamily: 'monospace', ml: 'auto' }}>
                  {pos.speed_kmph.toFixed(0)} km/h
                </Typography>
              )}
            </Box>
          );
        })}

        {/* Live indicator */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8, mt: 1, pt: 1, borderTop: '1px solid #1E1E2E' }}>
          <Box sx={{
            width: 6, height: 6, borderRadius: '50%',
            background: hasData ? '#A8FF3E' : '#F44336',
            animation: hasData ? 'livepulse 1.5s infinite' : 'none',
            '@keyframes livepulse': {
              '0%, 100%': { opacity: 1 },
              '50%': { opacity: 0.3 },
            },
          }} />
          <Typography sx={{ fontSize: 9, color: hasData ? '#A8FF3E' : '#F44336', letterSpacing: 1 }}>
            {hasData ? 'LIVE · 2s refresh' : 'WAITING FOR GPS DATA'}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};