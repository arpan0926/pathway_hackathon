import { Box, Typography, Chip } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { alertsApi } from '../../api/alerts';
import WarningIcon from '@mui/icons-material/Warning';
import { formatDistanceToNow } from 'date-fns';

const VEHICLE_DRIVERS: Record<string, string> = {
  VH001: 'Rajesh Kumar',
  VH002: 'Priya Singh',
};

export const DriverSafetyMonitor = () => {
  // Get latest driver safety alerts
  const { data: alerts = [] } = useQuery({
    queryKey: ['driver-alerts'],
    queryFn: () => alertsApi.getAll().then(r => 
      r.data.filter(a => a.metric === 'driver_safety' && a.is_active)
    ),
    refetchInterval: 3000,
  });

  const vehicleStatus: Record<string, { status: string; lastAlert: string; severity: string }> = {};
  
  alerts.forEach(alert => {
    const shipment = alert.shipment_id;
    const vehicle = shipment === 'SH001' ? 'VH001' : 'VH002';
    
    if (!vehicleStatus[vehicle] || new Date(alert.created_at) > new Date(vehicleStatus[vehicle].lastAlert)) {
      vehicleStatus[vehicle] = {
        status: alert.value || 'unknown',
        lastAlert: alert.created_at,
        severity: alert.threshold || 'warning',
      };
    }
  });

  return (
    <Box sx={{ background: '#111120', border: '1px solid #1E1E2E', borderRadius: 2, p: 2.5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <WarningIcon sx={{ fontSize: 16, color: '#FFB300' }} />
        <Typography variant="subtitle2" sx={{ 
          color: '#9E9EB8', letterSpacing: 1, fontSize: 11, textTransform: 'uppercase' 
        }}>
          Driver Safety Monitor
        </Typography>
      </Box>

      {Object.entries(VEHICLE_DRIVERS).map(([vehicleId, driverName]) => {
        const status = vehicleStatus[vehicleId];
        const isAlert = status && status.severity === 'critical';
        const statusColor = isAlert ? '#F44336' : '#A8FF3E';
        const statusText = status?.status.toUpperCase() || 'ACTIVE';

        return (
          <Box key={vehicleId} sx={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            py: 1.5, px: 2, mb: 1, borderRadius: 1,
            background: isAlert ? '#F4433610' : '#13131F',
            border: `1px solid ${isAlert ? '#F4433630' : '#1E1E2E'}`,
            '&:last-child': { mb: 0 },
          }}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
                {vehicleId}
              </Typography>
              <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>
                {driverName}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{
                width: 8, height: 8, borderRadius: '50%',
                background: statusColor,
                boxShadow: `0 0 8px ${statusColor}`,
                animation: isAlert ? 'blink 1s infinite' : 'none',
                '@keyframes blink': {
                  '0%, 100%': { opacity: 1 },
                  '50%': { opacity: 0.3 },
                },
              }} />
              <Typography variant="caption" sx={{ 
                color: statusColor, fontWeight: 700, fontSize: 10, minWidth: 70 
              }}>
                {statusText}
              </Typography>
              {status && (
                <Typography variant="caption" sx={{ color: '#555', fontSize: 9 }}>
                  {formatDistanceToNow(new Date(status.lastAlert), { addSuffix: true })}
                </Typography>
              )}
            </Box>
          </Box>
        );
      })}
    </Box>
  );
};