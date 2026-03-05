import { Grid, Box, Typography } from '@mui/material';
import { useStats } from '../hooks/useShipments';
import { ShipmentMap } from '../components/map/shipmentMap'
import { AlertsFeed } from '../components/alerts/AlertsFeed';
import { SpeedChart } from '../components/dashboard/SpeedChart';
import { ETAChart } from '../components/dashboard/ETAChart';
import { DriverSafetyMonitor } from '../components/dashboard/DriverSafetyMonitor';  // ← ADD THIS
import { AIAlertsPanel } from '../components/dashboard/aiAlertsPanel';  // ← ADD THIS
import { VehicleHealthMonitor } from '../components/dashboard/VehicleHealthMonitor';

export const Dashboard = () => {
  const { data: stats } = useStats();

  const kpis = [
    { label: 'Active Shipments', value: stats?.total_shipments ?? '--', color: '#00E5FF' },
    { label: 'Active Alerts', value: stats?.active_alerts ?? '--', color: '#FF6B35' },
    { label: 'Avg Fleet Speed', value: stats ? `${stats.avg_fleet_speed_kmph} km/h` : '--', color: '#A8FF3E' },
    { label: 'GPS Records', value: stats?.total_telemetry_records ?? '--', color: '#FFB300' },
  ];

  return (
    <Box sx={{ p: 3, height: '100%', overflowY: 'auto' }}>
      {/* KPI Row */}
      <Grid container spacing={2} mb={3}>
        {kpis.map((kpi) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={kpi.label}>
            <Box sx={{
              background: '#111120', border: `1px solid ${kpi.color}30`,
              borderRadius: 2, p: 2.5,
              borderLeft: `3px solid ${kpi.color}`,
            }}>
              <Typography variant="caption" color="text.secondary">{kpi.label}</Typography>
              <Typography variant="h4" sx={{ color: kpi.color, fontWeight: 600, mt: 0.5 }}>
                {kpi.value}
              </Typography>
            </Box>
          </Grid>
        ))}
      </Grid>

      {/* Map + Alerts row */}
      <Grid container spacing={2} mb={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Box sx={{ height: 420, background: '#111120', borderRadius: 2, overflow: 'hidden', border: '1px solid #1E1E2E' }}>
            <ShipmentMap />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <Box sx={{ height: 420, background: '#111120', borderRadius: 2, overflow: 'hidden', border: '1px solid #1E1E2E' }}>
            <AIAlertsPanel/>
          </Box>
        </Grid>
      </Grid>
      

      {/* ADD THIS NEW ROW - Driver Safety + Charts */}
      <Grid container spacing={2} mb={2}>
        <Grid size={{ xs: 12, md: 4 }}>
          <DriverSafetyMonitor />
        </Grid>
        <Grid size={{ xs: 12, md: 8 }}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12 }}>
              <SpeedChart />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      
      {/* ETA Chart row */}
      <Grid container spacing={2}>
        <Grid size={{ xs: 12 }}>
          <ETAChart />
        </Grid>
      </Grid>
    </Box>
  );
};