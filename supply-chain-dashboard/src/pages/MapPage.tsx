import { Box, Typography, Paper } from '@mui/material';
import { ShipmentMap } from '../components/map/shipmentMap';
import { useStore } from '../store/useStore';
import { useQuery } from '@tanstack/react-query';
import { telemetryApi } from '../api/telemetry';

export const MapPage = () => {
  const { selectedShipmentId, latestPositions } = useStore();

  const { data: latest } = useQuery({
    queryKey: ['telemetry-latest', selectedShipmentId],
    queryFn: () => telemetryApi.getLatest(selectedShipmentId!).then(r => r.data),
    enabled: !!selectedShipmentId,
    refetchInterval: 3000,
  });

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 3, gap: 2 }}>
      <Box>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>Live Map</Typography>
        <Typography variant="caption" color="text.secondary">
          {Object.keys(latestPositions).length} vehicle(s) tracked · click a marker to inspect
        </Typography>
      </Box>

      <Box sx={{ flex: 1, display: 'flex', gap: 2, minHeight: 0 }}>
        {/* Map */}
        <Box sx={{ flex: 1, borderRadius: 2, overflow: 'hidden', border: '1px solid #1E1E2E' }}>
          <ShipmentMap />
        </Box>

        {/* Side panel */}
        <Box sx={{ width: 260, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Fleet overview */}
          <Paper sx={{ p: 2, background: '#111120', border: '1px solid #1E1E2E' }}>
            <Typography variant="caption" sx={{ color: '#9E9EB8', letterSpacing: 1, textTransform: 'uppercase', fontSize: 10 }}>
              Fleet Overview
            </Typography>
            {Object.entries(latestPositions).map(([id, pos]) => (
              <Box key={id} sx={{ mt: 1.5, pb: 1.5, borderBottom: '1px solid #1A1A2A', '&:last-child': { border: 0, pb: 0 } }}>
                <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>{id}</Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                  {pos.lat.toFixed(4)}, {pos.lon.toFixed(4)}
                </Typography>
                <Typography variant="caption" sx={{
                  color: pos.speed_kmph > 40 ? '#00E5FF' : pos.speed_kmph > 0 ? '#FFB300' : '#F44336'
                }}>
                  {pos.speed_kmph.toFixed(1)} km/h · {pos.load_status}
                </Typography>
              </Box>
            ))}
            {Object.keys(latestPositions).length === 0 && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Waiting for GPS data...
              </Typography>
            )}
          </Paper>

          {/* Selected shipment detail */}
          {latest && (
            <Paper sx={{ p: 2, background: '#111120', border: '1px solid #00E5FF30' }}>
              <Typography variant="caption" sx={{ color: '#00E5FF', letterSpacing: 1, textTransform: 'uppercase', fontSize: 10 }}>
                Selected · {latest.shipment_id}
              </Typography>
              {[
                ['Vehicle', latest.vehicle_id],
                ['Speed', `${latest.speed_kmph.toFixed(1)} km/h`],
                ['Load', latest.load_status],
                ['Lat', latest.lat.toFixed(6)],
                ['Lon', latest.lon.toFixed(6)],
                ['Updated', new Date(latest.ts).toLocaleTimeString()],
              ].map(([label, value]) => (
                <Box key={label} sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">{label}</Typography>
                  <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>{value}</Typography>
                </Box>
              ))}
            </Paper>
          )}
        </Box>
      </Box>
    </Box>
  );
};