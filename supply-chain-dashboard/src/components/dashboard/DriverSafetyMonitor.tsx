import { Box, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { alertsApi } from '../../api/alerts';
import WarningIcon from '@mui/icons-material/Warning';
import { formatDistanceToNow } from 'date-fns';
import { motion } from 'framer-motion';

const VEHICLE_DRIVERS: Record<string, string> = {
  VH001: 'Rajesh Kumar',
  VH002: 'Priya Singh',
};

export const DriverSafetyMonitor = () => {
  // Get driver safety alerts (refreshes every 3 seconds)
  const { data: alerts = [] } = useQuery({
    queryKey: ['driver-alerts'],
    queryFn: async () => {
      const response = await alertsApi.getAll();
      return response.data.filter(a => 
        a.metric === 'driver_safety' && a.is_active
      );
    },
    refetchInterval: 3000,
  });

  // Build vehicle status map from latest alerts
  const vehicleStatus: Record<string, {
    status: string;
    lastAlert: string;
    severity: string;
    alertType: string;
  }> = {};
  
  alerts.forEach(alert => {
    const shipment = alert.shipment_id;
    // Map shipment to vehicle (SH001 → VH001, SH002 → VH002)
    const vehicle = shipment === 'SH001' ? 'VH001' : 'VH002';
    
    if (!vehicleStatus[vehicle] || 
        new Date(alert.created_at) > new Date(vehicleStatus[vehicle].lastAlert)) {
      vehicleStatus[vehicle] = {
        status: alert.value || 'unknown',
        lastAlert: alert.created_at,
        severity: alert.threshold || 'warning',
        alertType: alert.alert_type,
      };
    }
  });

  return (
    <Box sx={{ 
      background: '#111120', 
      border: '1px solid #1E1E2E', 
      borderRadius: 2, 
      p: 2.5,
      height: 420,
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <WarningIcon sx={{ fontSize: 16, color: '#FFB300' }} />
        <Typography variant="subtitle2" sx={{ 
          color: '#9E9EB8', 
          letterSpacing: 1, 
          fontSize: 11, 
          textTransform: 'uppercase',
          flex: 1,
        }}>
          Driver Safety Monitor
        </Typography>
        <Box sx={{
          width: 6, height: 6, borderRadius: '50%',
          background: alerts.length > 0 ? '#F44336' : '#A8FF3E',
          boxShadow: `0 0 8px ${alerts.length > 0 ? '#F44336' : '#A8FF3E'}`,
          animation: alerts.length > 0 ? 'pulse 2s infinite' : 'none',
          '@keyframes pulse': {
            '0%, 100%': { opacity: 1 },
            '50%': { opacity: 0.3 },
          },
        }} />
      </Box>

      {/* Driver Status Cards */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {Object.entries(VEHICLE_DRIVERS).map(([vehicleId, driverName]) => {
          const status = vehicleStatus[vehicleId];
          const isAlert = status && status.severity === 'critical';
          const statusColor = isAlert ? '#F44336' : '#A8FF3E';
          const statusText = status ? status.status.toUpperCase().replace('_', ' ') : 'ACTIVE';
          const statusIcon = status?.status === 'drowsy' ? '😴' : status?.status === 'head_down' ? '⬇️' : '✓';

          return (
            <motion.div
              key={vehicleId}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Box sx={{
                display: 'flex',
                flexDirection: 'column',
                py: 2,
                px: 2.5,
                borderRadius: 2,
                background: isAlert ? '#F4433608' : '#13131F',
                border: `1px solid ${isAlert ? '#F4433630' : '#1E1E2E'}`,
                position: 'relative',
                overflow: 'hidden',
              }}>
                {/* Alert pulse background */}
                {isAlert && (
                  <Box sx={{
                    position: 'absolute',
                    top: 0, left: 0, right: 0, bottom: 0,
                    background: `radial-gradient(circle at 50% 50%, ${statusColor}15 0%, transparent 70%)`,
                    animation: 'pulse 2s infinite',
                    pointerEvents: 'none',
                  }} />
                )}

                {/* Top row: Vehicle + Status indicator */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5, position: 'relative' }}>
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'monospace', fontSize: 15 }}>
                      {vehicleId}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>
                      Driver: {driverName}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{
                      width: 10, height: 10, borderRadius: '50%',
                      background: statusColor,
                      boxShadow: `0 0 12px ${statusColor}`,
                      animation: isAlert ? 'blink 1s infinite' : 'none',
                      '@keyframes blink': {
                        '0%, 100%': { opacity: 1 },
                        '50%': { opacity: 0.2 },
                      },
                    }} />
                  </Box>
                </Box>

                {/* Status text + emoji */}
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  background: isAlert ? '#00000020' : '#00000010',
                  borderRadius: 1,
                  px: 1.5,
                  py: 1,
                  position: 'relative',
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography sx={{ fontSize: 20 }}>{statusIcon}</Typography>
                    <Box>
                      <Typography variant="body2" sx={{ 
                        color: statusColor, 
                        fontWeight: 700, 
                        fontSize: 12,
                        letterSpacing: 0.5,
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

                  {/* Alert badge */}
                  {isAlert && (
                    <Box sx={{
                      background: `${statusColor}20`,
                      border: `1px solid ${statusColor}40`,
                      borderRadius: 1,
                      px: 1,
                      py: 0.3,
                    }}>
                      <Typography sx={{ 
                        fontSize: 9, 
                        color: statusColor, 
                        fontWeight: 700,
                        letterSpacing: 1,
                      }}>
                        ALERT
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Box>
            </motion.div>
          );
        })}
      </Box>

      {/* Footer info */}
      <Box sx={{ 
        mt: 2, 
        pt: 2, 
        borderTop: '1px solid #1E1E2E',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <Typography variant="caption" sx={{ color: '#555', fontSize: 9 }}>
          Monitoring: Eyes closed, head position
        </Typography>
        <Typography variant="caption" sx={{ color: '#666', fontSize: 9 }}>
          {alerts.length} active alert{alerts.length !== 1 ? 's' : ''}
        </Typography>
      </Box>
    </Box>
  );
};