import { Box, Typography, LinearProgress, Chip } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useState } from 'react';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface VehicleHealth {
  vehicle_id: string;
  overall_health_score: number;
  engine_health_score: number;
  brake_health_score: number;
  tire_health_score: number;
  battery_health_score: number;
  engine_temp_celsius: number;
  brake_pad_thickness_mm: number;
  tire_pressure_psi: number;
  predicted_failure_type: string | null;
  predicted_failure_days: number | null;
  maintenance_urgency: string;
}

export const VehicleHealthMonitor = () => {
  const { data: healthData = [] } = useQuery({
    queryKey: ['vehicle-health'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/vehicle-health/latest`);
      return response.data;
    },
    refetchInterval: 5000,
  });

  const getHealthColor = (score: number) => {
    if (score >= 80) return '#A8FF3E';
    if (score >= 50) return '#FFB300';
    return '#F44336';
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical': return '#F44336';
      case 'high': return '#FF6B35';
      case 'medium': return '#FFB300';
      default: return '#A8FF3E';
    }
  };

  return (
    <Box sx={{ 
      background: '#111120', 
      border: '1px solid #1E1E2E', 
      borderRadius: 2, 
      p: 2.5,
    }}>
      <Typography variant="subtitle2" sx={{ 
        color: '#9E9EB8', 
        letterSpacing: 1, 
        fontSize: 11, 
        textTransform: 'uppercase',
        mb: 2,
      }}>
        🔧 Predictive Maintenance
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {healthData.map((vehicle: VehicleHealth) => {
          const healthColor = getHealthColor(vehicle.overall_health_score);
          const urgencyColor = getUrgencyColor(vehicle.maintenance_urgency);

          return (
            <Box
              key={vehicle.vehicle_id}
              sx={{
                background: '#13131F',
                border: `1px solid ${vehicle.maintenance_urgency === 'critical' ? '#F4433630' : '#1E1E2E'}`,
                borderRadius: 1.5,
                p: 2,
              }}
            >
              {/* Header */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'monospace', fontSize: 13 }}>
                  {vehicle.vehicle_id}
                </Typography>
                <Chip
                  label={`${vehicle.overall_health_score.toFixed(0)}%`}
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: 10,
                    fontWeight: 700,
                    background: `${healthColor}20`,
                    color: healthColor,
                    border: `1px solid ${healthColor}40`,
                  }}
                />
              </Box>

              {/* Overall Health Bar */}
              <Box sx={{ mb: 1.5 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="caption" sx={{ fontSize: 9, color: '#666' }}>
                    Overall Health
                  </Typography>
                  <Typography variant="caption" sx={{ fontSize: 9, color: healthColor, fontWeight: 600 }}>
                    {vehicle.overall_health_score.toFixed(0)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={vehicle.overall_health_score}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    backgroundColor: '#0A0A14',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: healthColor,
                      borderRadius: 3,
                    },
                  }}
                />
              </Box>

              {/* Component Health Grid */}
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, mb: 1.5 }}>
                <Box>
                  <Typography variant="caption" sx={{ fontSize: 8, color: '#666' }}>Engine</Typography>
                  <Typography variant="caption" sx={{ fontSize: 10, color: getHealthColor(vehicle.engine_health_score), fontWeight: 600, display: 'block' }}>
                    {vehicle.engine_health_score.toFixed(0)}% ({vehicle.engine_temp_celsius.toFixed(0)}°C)
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" sx={{ fontSize: 8, color: '#666' }}>Brakes</Typography>
                  <Typography variant="caption" sx={{ fontSize: 10, color: getHealthColor(vehicle.brake_health_score), fontWeight: 600, display: 'block' }}>
                    {vehicle.brake_health_score.toFixed(0)}% ({vehicle.brake_pad_thickness_mm.toFixed(1)}mm)
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" sx={{ fontSize: 8, color: '#666' }}>Tires</Typography>
                  <Typography variant="caption" sx={{ fontSize: 10, color: getHealthColor(vehicle.tire_health_score), fontWeight: 600, display: 'block' }}>
                    {vehicle.tire_health_score.toFixed(0)}% ({vehicle.tire_pressure_psi.toFixed(0)} PSI)
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" sx={{ fontSize: 8, color: '#666' }}>Battery</Typography>
                  <Typography variant="caption" sx={{ fontSize: 10, color: getHealthColor(vehicle.battery_health_score), fontWeight: 600, display: 'block' }}>
                    {vehicle.battery_health_score.toFixed(0)}%
                  </Typography>
                </Box>
              </Box>

              {/* Failure Prediction */}
              {vehicle.predicted_failure_type && (
                <Box sx={{
                  background: `${urgencyColor}10`,
                  border: `1px solid ${urgencyColor}30`,
                  borderRadius: 1,
                  p: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}>
                  <Typography variant="caption" sx={{ fontSize: 9, color: urgencyColor, fontWeight: 600 }}>
                    ⚠️ {vehicle.predicted_failure_type.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                  <Typography variant="caption" sx={{ fontSize: 8, color: '#666' }}>
                    {vehicle.predicted_failure_days === 0 ? 'NOW' : `${vehicle.predicted_failure_days}d`}
                  </Typography>
                </Box>
              )}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};