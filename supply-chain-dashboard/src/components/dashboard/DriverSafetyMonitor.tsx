import { Box, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { alertsApi } from '../../api/alerts';
import WarningIcon from '@mui/icons-material/Warning';
import { formatDistanceToNow } from 'date-fns';
import { motion } from 'framer-motion';

const VEHICLE_DRIVERS: Record<string, string> = {
  VH001: 'Rajesh Kumar',
  VH002: 'Priya Singh',
  VH003: 'Amit Patel',
  VH004: 'Sneha Sharma',
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
    // Map shipment to vehicle (SH001 → VH001, etc.)
    const vehicleMap: Record<string, string> = {
      'SH001': 'VH001',
      'SH002': 'VH002',
      'SH003': 'VH003',
      'SH004': 'VH004',
    };
    const vehicle = vehicleMap[shipment];
    
    if (vehicle && (!vehicleStatus[vehicle] || 
        new Date(alert.created_at) > new Date(vehicleStatus[vehicle].lastAlert))) {
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

      {/* Driver Status Cards - Grid Layout for 4 drivers */}
      <Box sx={{ 
        flex: 1, 
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: 1.5,
        minHeight: 0,
      }}>
        {Object.entries(VEHICLE_DRIVERS).map(([vehicleId, driverName]) => {
          const status = vehicleStatus[vehicleId];
          const isAlert = status && status.severity === 'critical';
          const statusColor = isAlert ? '#F44336' : '#A8FF3E';
          const statusText = status ? status.status.toUpperCase().replace('_', ' ') : 'ACTIVE';
          const statusIcon = status?.status === 'drowsy' ? '😴' : 
                            status?.status === 'head_down' ? '⬇️' : 
                            status?.status === 'distracted' ? '👀' : '✓';

          return (
            <motion.div
              key={vehicleId}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              style={{ height: '100%' }}
            >
              <Box sx={{
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                py: 1.5,
                px: 2,
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

                {/* Content */}
                <Box sx={{ position: 'relative', zIndex: 1 }}>
                  {/* Vehicle ID + Status Indicator */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="body2" sx={{ 
                      fontWeight: 700, 
                      fontFamily: 'monospace', 
                      fontSize: 13,
                      color: '#E8EAF6',
                    }}>
                      {vehicleId}
                    </Typography>
                    <Box sx={{
                      width: 8, height: 8, borderRadius: '50%',
                      background: statusColor,
                      boxShadow: `0 0 10px ${statusColor}`,
                      animation: isAlert ? 'blink 1s infinite' : 'none',
                      '@keyframes blink': {
                        '0%, 100%': { opacity: 1 },
                        '50%': { opacity: 0.2 },
                      },
                    }} />
                  </Box>

                  {/* Driver Name */}
                  <Typography variant="caption" sx={{ 
                    color: '#666', 
                    fontSize: 10,
                    display: 'block',
                    mb: 1.5,
                  }}>
                    Driver: {driverName}
                  </Typography>

                  {/* Status Badge */}
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    gap: 1,
                    background: isAlert ? '#00000030' : '#00000020',
                    borderRadius: 1,
                    px: 1.5,
                    py: 1,
                    border: `1px solid ${isAlert ? '#F4433620' : '#1E1E2E'}`,
                  }}>
                    <Typography sx={{ fontSize: 18 }}>{statusIcon}</Typography>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ 
                        color: statusColor, 
                        fontWeight: 700, 
                        fontSize: 11,
                        letterSpacing: 0.5,
                      }}>
                        {statusText}
                      </Typography>
                      {status && (
                        <Typography variant="caption" sx={{ 
                          color: '#555', 
                          fontSize: 8,
                          display: 'block',
                          mt: 0.3,
                        }}>
                          {formatDistanceToNow(new Date(status.lastAlert), { addSuffix: true })}
                        </Typography>
                      )}
                    </Box>
                    
                    {/* Alert Tag */}
                    {isAlert && (
                      <Box sx={{
                        background: `${statusColor}25`,
                        border: `1px solid ${statusColor}50`,
                        borderRadius: 0.5,
                        px: 0.8,
                        py: 0.2,
                      }}>
                        <Typography sx={{ 
                          fontSize: 8, 
                          color: statusColor, 
                          fontWeight: 700,
                          letterSpacing: 0.5,
                        }}>
                          ALERT
                        </Typography>
                      </Box>
                    )}
                  </Box>
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
          Real-time: Eyes, head position, attention
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{
            width: 4, height: 4, borderRadius: '50%',
            background: alerts.length > 0 ? '#F44336' : '#666',
          }} />
          <Typography variant="caption" sx={{ 
            color: alerts.length > 0 ? '#F44336' : '#666', 
            fontSize: 9,
            fontWeight: 600,
          }}>
            {alerts.length} active alert{alerts.length !== 1 ? 's' : ''}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};