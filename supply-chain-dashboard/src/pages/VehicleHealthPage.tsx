import { useState } from 'react';
import { Box, Typography, Grid, Card, CardContent, LinearProgress, Chip, Button, Tabs, Tab } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import BuildIcon from '@mui/icons-material/Build';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ThermostatIcon from '@mui/icons-material/Thermostat';
import SpeedIcon from '@mui/icons-material/Speed';
import BatteryChargingFullIcon from '@mui/icons-material/BatteryChargingFull';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface VehicleHealth {
  vehicle_id: string;
  overall_health_score: number;
  engine_health_score: number;
  brake_health_score: number;
  tire_health_score: number;
  battery_health_score: number;
  engine_temp_celsius: number;
  engine_rpm: number;
  oil_pressure_psi: number;
  coolant_level_percent: number;
  vibration_level: number;
  brake_pad_thickness_mm: number;
  tire_pressure_psi: number;
  battery_voltage: number;
  alternator_output: number;
  predicted_failure_type: string | null;
  predicted_failure_days: number | null;
  maintenance_urgency: string;
  ts: string;
}

interface MaintenanceAlert {
  alert_id: number;
  vehicle_id: string;
  alert_type: string;
  component: string;
  severity: string;
  predicted_failure_date: string;
  recommendation: string;
  created_at: string;
}

const VEHICLE_NAMES: Record<string, string> = {
  VH001: 'Mumbai Express',
  VH002: 'Chennai Cruiser',
  VH003: 'Kolkata Carrier',
  VH004: 'Ahmedabad Arrow',
};

export const VehicleHealthPage = () => {
  const [selectedVehicle, setSelectedVehicle] = useState<string>('VH001');
  const [activeTab, setActiveTab] = useState(0);

  // Fetch latest health data
  const { data: healthData = [] } = useQuery<VehicleHealth[]>({
    queryKey: ['vehicle-health'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/vehicle-health/latest`);
      return response.data;
    },
    refetchInterval: 5000,
  });

  // Fetch maintenance alerts
  const { data: alerts = [] } = useQuery<MaintenanceAlert[]>({
    queryKey: ['maintenance-alerts'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/maintenance-alerts`);
      return response.data;
    },
    refetchInterval: 5000,
  });

  // Fetch historical health data for trends
  const { data: healthHistory = [] } = useQuery({
    queryKey: ['vehicle-health-history', selectedVehicle],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/vehicle-health/history/${selectedVehicle}?limit=20`);
      return response.data;
    },
    refetchInterval: 10000,
  });

  const selectedVehicleData = healthData.find(v => v.vehicle_id === selectedVehicle);
  const vehicleAlerts = alerts.filter(a => a.vehicle_id === selectedVehicle);

  const getHealthColor = (score: number) => {
    if (score >= 80) return '#A8FF3E';
    if (score >= 60) return '#FFB300';
    if (score >= 40) return '#FF6B35';
    return '#F44336';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#F44336';
      case 'high': return '#FF6B35';
      case 'medium': return '#FFB300';
      default: return '#A8FF3E';
    }
  };

  const getStatusIcon = (score: number) => {
    if (score >= 80) return <CheckCircleIcon sx={{ color: '#A8FF3E', fontSize: 20 }} />;
    if (score >= 60) return <WarningIcon sx={{ color: '#FFB300', fontSize: 20 }} />;
    return <WarningIcon sx={{ color: '#F44336', fontSize: 20 }} />;
  };

  // Prepare radar chart data
  const radarData = selectedVehicleData ? [
    {
      component: 'Engine',
      score: selectedVehicleData.engine_health_score,
      fullMark: 100,
    },
    {
      component: 'Brakes',
      score: selectedVehicleData.brake_health_score,
      fullMark: 100,
    },
    {
      component: 'Tires',
      score: selectedVehicleData.tire_health_score,
      fullMark: 100,
    },
    {
      component: 'Battery',
      score: selectedVehicleData.battery_health_score,
      fullMark: 100,
    },
  ] : [];

  // Fleet overview stats
  const fleetStats = {
    totalVehicles: healthData.length,
    healthy: healthData.filter(v => v.overall_health_score >= 80).length,
    needsAttention: healthData.filter(v => v.overall_health_score >= 60 && v.overall_health_score < 80).length,
    critical: healthData.filter(v => v.overall_health_score < 60).length,
    avgHealth: healthData.length > 0 
      ? healthData.reduce((sum, v) => sum + v.overall_health_score, 0) / healthData.length 
      : 0,
  };

  return (
    <Box sx={{ 
    minHeight: '100vh',  // Changed from height
    background: '#0A0A14', 
    p: 3,
    pb: 6  // Extra padding at bottom
  }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
          <BuildIcon sx={{ fontSize: 32, color: '#00E5FF' }} />
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#E8EAF6' }}>
            Predictive Maintenance Dashboard
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: '#9E9EB8', fontSize: 14 }}>
          Real-time vehicle health monitoring powered by AI-driven failure prediction
        </Typography>
      </Box>

      {/* Fleet Overview Stats */}
      <Grid container spacing={2} mb={3}>
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card sx={{ background: '#111120', border: '1px solid #1E1E2E' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 10, textTransform: 'uppercase' }}>
                Total Fleet
              </Typography>
              <Typography variant="h4" sx={{ color: '#00E5FF', fontWeight: 700, mt: 0.5 }}>
                {fleetStats.totalVehicles}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card sx={{ background: '#111120', border: '1px solid #A8FF3E30', borderLeft: '3px solid #A8FF3E' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 10, textTransform: 'uppercase' }}>
                Healthy
              </Typography>
              <Typography variant="h4" sx={{ color: '#A8FF3E', fontWeight: 700, mt: 0.5 }}>
                {fleetStats.healthy}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card sx={{ background: '#111120', border: '1px solid #FFB30030', borderLeft: '3px solid #FFB300' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 10, textTransform: 'uppercase' }}>
                Needs Attention
              </Typography>
              <Typography variant="h4" sx={{ color: '#FFB300', fontWeight: 700, mt: 0.5 }}>
                {fleetStats.needsAttention}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card sx={{ background: '#111120', border: '1px solid #F4433630', borderLeft: '3px solid #F44336' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 10, textTransform: 'uppercase' }}>
                Critical
              </Typography>
              <Typography variant="h4" sx={{ color: '#F44336', fontWeight: 700, mt: 0.5 }}>
                {fleetStats.critical}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
          <Card sx={{ background: '#111120', border: '1px solid #1E1E2E' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 10, textTransform: 'uppercase' }}>
                Avg Health
              </Typography>
              <Typography variant="h4" sx={{ color: getHealthColor(fleetStats.avgHealth), fontWeight: 700, mt: 0.5 }}>
                {fleetStats.avgHealth.toFixed(0)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Vehicle Selector */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 1 }}>
          Select Vehicle
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          {healthData.map((vehicle) => {
            const isSelected = vehicle.vehicle_id === selectedVehicle;
            const healthColor = getHealthColor(vehicle.overall_health_score);

            return (
              <motion.div
                key={vehicle.vehicle_id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  onClick={() => setSelectedVehicle(vehicle.vehicle_id)}
                  sx={{
                    background: isSelected ? '#00E5FF10' : '#111120',
                    border: isSelected ? '2px solid #00E5FF' : '1px solid #1E1E2E',
                    cursor: 'pointer',
                    minWidth: 180,
                    transition: 'all 0.2s',
                    '&:hover': {
                      borderColor: '#00E5FF60',
                    },
                  }}
                >
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'monospace' }}>
                        {vehicle.vehicle_id}
                      </Typography>
                      {getStatusIcon(vehicle.overall_health_score)}
                    </Box>
                    <Typography variant="caption" sx={{ color: '#666', fontSize: 10, display: 'block', mb: 1 }}>
                      {VEHICLE_NAMES[vehicle.vehicle_id]}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={vehicle.overall_health_score}
                        sx={{
                          flex: 1,
                          height: 6,
                          borderRadius: 3,
                          backgroundColor: '#0A0A14',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: healthColor,
                            borderRadius: 3,
                          },
                        }}
                      />
                      <Typography variant="caption" sx={{ color: healthColor, fontWeight: 700, fontSize: 11, minWidth: 35 }}>
                        {vehicle.overall_health_score.toFixed(0)}%
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </Box>
      </Box>

      {/* Tabs */}
      <Tabs 
        value={activeTab} 
        onChange={(_, newValue) => setActiveTab(newValue)}
        sx={{
          mb: 3,
          '& .MuiTab-root': {
            color: '#9E9EB8',
            textTransform: 'none',
            fontSize: 13,
            fontWeight: 600,
          },
          '& .Mui-selected': {
            color: '#00E5FF !important',
          },
          '& .MuiTabs-indicator': {
            backgroundColor: '#00E5FF',
          },
        }}
      >
        <Tab label="Health Overview" />
        <Tab label="Component Details" />
        <Tab label="Maintenance Alerts" />
        <Tab label="Trends & Analytics" />
      </Tabs>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 0 && selectedVehicleData && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Grid container spacing={3}>
              {/* Overall Health Card */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Card sx={{ background: '#111120', border: '1px solid #1E1E2E', height: '100%' }}>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
                      Overall Vehicle Health
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
                      <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                        <Box
                          sx={{
                            width: 180,
                            height: 180,
                            borderRadius: '50%',
                            background: `conic-gradient(${getHealthColor(selectedVehicleData.overall_health_score)} ${selectedVehicleData.overall_health_score}%, #1E1E2E 0)`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <Box
                            sx={{
                              width: 150,
                              height: 150,
                              borderRadius: '50%',
                              background: '#0A0A14',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              flexDirection: 'column',
                            }}
                          >
                            <Typography variant="h2" sx={{ color: getHealthColor(selectedVehicleData.overall_health_score), fontWeight: 700 }}>
                              {selectedVehicleData.overall_health_score.toFixed(0)}
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#666', fontSize: 12 }}>
                              Health Score
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                    </Box>

                    {selectedVehicleData.predicted_failure_type && (
                      <Box
                        sx={{
                          background: `${getSeverityColor(selectedVehicleData.maintenance_urgency)}15`,
                          border: `1px solid ${getSeverityColor(selectedVehicleData.maintenance_urgency)}40`,
                          borderRadius: 2,
                          p: 2,
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <WarningIcon sx={{ fontSize: 18, color: getSeverityColor(selectedVehicleData.maintenance_urgency) }} />
                          <Typography variant="body2" sx={{ color: getSeverityColor(selectedVehicleData.maintenance_urgency), fontWeight: 700, fontSize: 13 }}>
                            Predicted Failure
                          </Typography>
                        </Box>
                        <Typography variant="body2" sx={{ color: '#E8EAF6', fontSize: 12, mb: 0.5 }}>
                          {selectedVehicleData.predicted_failure_type.replace(/_/g, ' ').toUpperCase()}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 11 }}>
                          Expected in {selectedVehicleData.predicted_failure_days === 0 ? 'immediate attention required' : `${selectedVehicleData.predicted_failure_days} days`}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Radar Chart */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Card sx={{ background: '#111120', border: '1px solid #1E1E2E', height: '100%' }}>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
                      Component Health Distribution
                    </Typography>

                    <ResponsiveContainer width="100%" height={280}>
                      <RadarChart data={radarData}>
                        <PolarGrid stroke="#1E1E2E" />
                        <PolarAngleAxis dataKey="component" tick={{ fill: '#9E9EB8', fontSize: 12 }} />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#666', fontSize: 10 }} />
                        <Radar
                          name="Health Score"
                          dataKey="score"
                          stroke="#00E5FF"
                          fill="#00E5FF"
                          fillOpacity={0.3}
                          strokeWidth={2}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>

              {/* Component Health Bars */}
              <Grid size={{ xs: 12 }}>
                <Card sx={{ background: '#111120', border: '1px solid #1E1E2E' }}>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 3 }}>
                      System Components
                    </Typography>

                    <Grid container spacing={3}>
                      {[
                        { name: 'Engine', score: selectedVehicleData.engine_health_score, icon: <ThermostatIcon /> },
                        { name: 'Brakes', score: selectedVehicleData.brake_health_score, icon: <SpeedIcon /> },
                        { name: 'Tires', score: selectedVehicleData.tire_health_score, icon: <SpeedIcon /> },
                        { name: 'Battery', score: selectedVehicleData.battery_health_score, icon: <BatteryChargingFullIcon /> },
                      ].map((component) => (
                        <Grid size={{ xs: 12, sm: 6, md: 3 }} key={component.name}>
                          <Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                              <Box sx={{ color: getHealthColor(component.score) }}>
                                {component.icon}
                              </Box>
                              <Typography variant="body2" sx={{ fontWeight: 600, fontSize: 13 }}>
                                {component.name}
                              </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={component.score}
                                sx={{
                                  flex: 1,
                                  height: 8,
                                  borderRadius: 4,
                                  backgroundColor: '#0A0A14',
                                  '& .MuiLinearProgress-bar': {
                                    backgroundColor: getHealthColor(component.score),
                                    borderRadius: 4,
                                  },
                                }}
                              />
                              <Typography variant="body2" sx={{ color: getHealthColor(component.score), fontWeight: 700, fontSize: 14, minWidth: 40 }}>
                                {component.score.toFixed(0)}%
                              </Typography>
                            </Box>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </motion.div>
        )}

        {activeTab === 1 && selectedVehicleData && (
          <motion.div
            key="details"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Grid container spacing={3}>
              {/* Engine Metrics */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Card sx={{ background: '#111120', border: '1px solid #1E1E2E' }}>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
                      🔥 Engine Metrics
                    </Typography>

                    <Grid container spacing={2}>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Box sx={{ background: '#0A0A14', borderRadius: 1, p: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>Temperature</Typography>
                          <Typography variant="h6" sx={{ color: getHealthColor(100 - Math.abs(selectedVehicleData.engine_temp_celsius - 85)), fontWeight: 700 }}>
                            {selectedVehicleData.engine_temp_celsius.toFixed(1)}°C
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 9 }}>Normal: 85-95°C</Typography>
                        </Box>
                      </Grid>

                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Box sx={{ background: '#0A0A14', borderRadius: 1, p: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>RPM</Typography>
                          <Typography variant="h6" sx={{ color: '#00E5FF', fontWeight: 700 }}>
                            {selectedVehicleData.engine_rpm}
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 9 }}>Current Speed</Typography>
                        </Box>
                      </Grid>

                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Box sx={{ background: '#0A0A14', borderRadius: 1, p: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>Oil Pressure</Typography>
                          <Typography variant="h6" sx={{ color: getHealthColor((selectedVehicleData.oil_pressure_psi / 50) * 100), fontWeight: 700 }}>
                            {selectedVehicleData.oil_pressure_psi?.toFixed(0) || 0} PSI
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 9 }}>Normal: 35-50 PSI</Typography>
                        </Box>
                      </Grid>

                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Box sx={{ background: '#0A0A14', borderRadius: 1, p: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>Coolant Level</Typography>
                          <Typography variant="h6" sx={{ color: getHealthColor(selectedVehicleData.coolant_level_percent), fontWeight: 700 }}>
                            {selectedVehicleData.coolant_level_percent?.toFixed(0) || 0}%
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 9 }}>Optimal: &gt;90%</Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Brake & Tire Metrics */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Card sx={{ background: '#111120', border: '1px solid #1E1E2E' }}>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
                      🛞 Brakes & Tires
                    </Typography>

                    <Grid container spacing={2}>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Box sx={{ background: '#0A0A14', borderRadius: 1, p: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>Brake Pads</Typography>
                          <Typography variant="h6" sx={{ color: getHealthColor((selectedVehicleData.brake_pad_thickness_mm / 12) * 100), fontWeight: 700 }}>
                            {selectedVehicleData.brake_pad_thickness_mm?.toFixed(1) || 0} mm
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 9 }}>Replace at 3mm</Typography>
                        </Box>
                      </Grid>

                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Box sx={{ background: '#0A0A14', borderRadius: 1, p: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>Tire Pressure</Typography>
                          <Typography variant="h6" sx={{ color: getHealthColor(100 - Math.abs(selectedVehicleData.tire_pressure_psi - 32) * 5), fontWeight: 700 }}>
                            {selectedVehicleData.tire_pressure_psi?.toFixed(0) || 0} PSI
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 9 }}>Optimal: 32 PSI</Typography>
                        </Box>
                      </Grid>

                      <Grid size={{ xs: 12 }}>
                        <Box sx={{ background: '#0A0A14', borderRadius: 1, p: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>Vibration Level</Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={selectedVehicleData.vibration_level * 10}
                              sx={{
                                flex: 1,
                                height: 8,
                                borderRadius: 4,
                                backgroundColor: '#0A0A14',
                                border: '1px solid #1E1E2E',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: selectedVehicleData.vibration_level > 7 ? '#F44336' : selectedVehicleData.vibration_level > 5 ? '#FFB300' : '#A8FF3E',
                                  borderRadius: 4,
                                },
                              }}
                            />
                            <Typography variant="h6" sx={{ 
                              color: selectedVehicleData.vibration_level > 7 ? '#F44336' : selectedVehicleData.vibration_level > 5 ? '#FFB300' : '#A8FF3E',
                              fontWeight: 700,
                              minWidth: 40,
                            }}>
                              {selectedVehicleData.vibration_level?.toFixed(1) || 0}
                            </Typography>
                          </Box>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 9, display: 'block', mt: 0.5 }}>
                            Scale: 0-10 (Normal: 0-5)
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Electrical System */}
              <Grid size={{ xs: 12, md: 6 }}>
                <Card sx={{ background: '#111120', border: '1px solid #1E1E2E' }}>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
                      ⚡ Electrical System
                    </Typography>

                    <Grid container spacing={2}>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Box sx={{ background: '#0A0A14', borderRadius: 1, p: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>Battery</Typography>
                          <Typography variant="h6" sx={{ color: getHealthColor(((selectedVehicleData.battery_voltage - 11.5) / (12.8 - 11.5)) * 100), fontWeight: 700 }}>
                            {selectedVehicleData.battery_voltage?.toFixed(2) || 0}V
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 9 }}>Normal: 12.4-12.8V</Typography>
                        </Box>
                      </Grid>

                      <Grid size={{ xs: 12, sm: 6 }}>
                        <Box sx={{ background: '#0A0A14', borderRadius: 1, p: 1.5 }}>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>Alternator</Typography>
                          <Typography variant="h6" sx={{ color: '#A8FF3E', fontWeight: 700 }}>
                            {selectedVehicleData.alternator_output?.toFixed(1) || 0}V
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#666', fontSize: 9 }}>Normal: 13.5-14.5V</Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </motion.div>
        )}

        {activeTab === 2 && (
          <motion.div
            key="alerts"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card sx={{ background: '#111120', border: '1px solid #1E1E2E' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
                  Active Maintenance Alerts
                </Typography>

                {vehicleAlerts.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <CheckCircleIcon sx={{ fontSize: 48, color: '#A8FF3E', mb: 2 }} />
                    <Typography variant="body2" sx={{ color: '#9E9EB8' }}>
                      No active maintenance alerts for {selectedVehicle}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666', fontSize: 11 }}>
                      All systems operating normally
                    </Typography>
                  </Box>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {vehicleAlerts.map((alert) => (
                      <motion.div
                        key={alert.alert_id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                      >
                        <Box
                          sx={{
                            background: `${getSeverityColor(alert.severity)}08`,
                            border: `1px solid ${getSeverityColor(alert.severity)}30`,
                            borderLeft: `4px solid ${getSeverityColor(alert.severity)}`,
                            borderRadius: 1,
                            p: 2,
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                            <Box>
                              <Typography variant="body2" sx={{ fontWeight: 700, fontSize: 13, mb: 0.5 }}>
                                {alert.alert_type.replace(/_/g, ' ').toUpperCase()}
                              </Typography>
                              <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 11 }}>
                                Component: {alert.component}
                              </Typography>
                            </Box>
                            <Chip
                              label={alert.severity.toUpperCase()}
                              size="small"
                              sx={{
                                height: 20,
                                fontSize: 9,
                                fontWeight: 700,
                                background: `${getSeverityColor(alert.severity)}20`,
                                color: getSeverityColor(alert.severity),
                                border: `1px solid ${getSeverityColor(alert.severity)}40`,
                              }}
                            />
                          </Box>

                          <Typography variant="body2" sx={{ color: '#E8EAF6', fontSize: 12, mb: 1 }}>
                            {alert.recommendation}
                          </Typography>

                          {alert.predicted_failure_date && (
                            <Typography variant="caption" sx={{ color: '#666', fontSize: 10 }}>
                              Expected failure: {new Date(alert.predicted_failure_date).toLocaleString()}
                            </Typography>
                          )}
                        </Box>
                      </motion.div>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {activeTab === 3 && (
          <motion.div
            key="trends"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Grid container spacing={3}>
              <Grid size={{ xs: 12 }}>
                <Card sx={{ background: '#111120', border: '1px solid #1E1E2E' }}>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
                      Health Score Trend
                    </Typography>

                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={healthHistory}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" />
                        <XAxis 
                          dataKey="ts" 
                          tick={{ fill: '#666', fontSize: 10 }}
                          tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                        />
                        <YAxis 
                          domain={[0, 100]} 
                          tick={{ fill: '#666', fontSize: 10 }}
                        />
                        <Tooltip
                          contentStyle={{
                            background: '#0A0A14',
                            border: '1px solid #2A2A3E',
                            borderRadius: 8,
                          }}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="overall_health_score" stroke="#00E5FF" strokeWidth={2} dot={false} name="Overall" />
                        <Line type="monotone" dataKey="engine_health_score" stroke="#A8FF3E" strokeWidth={2} dot={false} name="Engine" />
                        <Line type="monotone" dataKey="brake_health_score" stroke="#FFB300" strokeWidth={2} dot={false} name="Brakes" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>

              <Grid size={{ xs: 12 }}>
                <Card sx={{ background: '#111120', border: '1px solid #1E1E2E' }}>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ color: '#9E9EB8', fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
                      Fleet Health Comparison
                    </Typography>

                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={healthData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" />
                        <XAxis dataKey="vehicle_id" tick={{ fill: '#666', fontSize: 10 }} />
                        <YAxis domain={[0, 100]} tick={{ fill: '#666', fontSize: 10 }} />
                        <Tooltip
                          contentStyle={{
                            background: '#0A0A14',
                            border: '1px solid #2A2A3E',
                            borderRadius: 8,
                          }}
                        />
                        <Legend />
                        <Bar dataKey="engine_health_score" fill="#A8FF3E" name="Engine" />
                        <Bar dataKey="brake_health_score" fill="#FFB300" name="Brakes" />
                        <Bar dataKey="tire_health_score" fill="#00E5FF" name="Tires" />
                        <Bar dataKey="battery_health_score" fill="#FF6B35" name="Battery" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </motion.div>
        )}
      </AnimatePresence>
    </Box>
  );
};