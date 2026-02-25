import { useState } from 'react';
import { Box, Typography, Button, TextField, Chip } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { aiAlertsApi } from '../../api/aiAlerts';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import toast from 'react-hot-toast';

export const AIAlertsPanel = () => {
  const [stallMinutes, setStallMinutes] = useState(15);
  const [speedThreshold, setSpeedThreshold] = useState(5);

  // Health check
  const { data: health } = useQuery({
    queryKey: ['ai-alerts-health'],
    queryFn: () => aiAlertsApi.healthCheck().then(r => r.data),
    refetchInterval: 30000,
  });

  // Stall check mutation
  const stallCheckMutation = useMutation({
    mutationFn: aiAlertsApi.checkStall,
    onSuccess: (data) => {
      const count = data.data.created_alerts.length;
      if (count > 0) {
        toast.error(`🚨 ${count} stall alert${count > 1 ? 's' : ''} created!`);
      } else {
        toast.success('✓ No stalled shipments detected');
      }
    },
    onError: () => {
      toast.error('Failed to check stalls');
    },
  });

  const handleCheckStalls = () => {
    stallCheckMutation.mutate({
      stall_minutes: stallMinutes,
      speed_threshold_kmph: speedThreshold,
      max_move_meters: 100,
    });
  };

  const isHealthy = health?.db === 'ok';

  return (
    <Box sx={{ 
      background: '#111120', 
      border: '1px solid #1E1E2E', 
      borderRadius: 2, 
      p: 2.5,
    }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <SmartToyIcon sx={{ fontSize: 16, color: '#00E5FF' }} />
        <Typography variant="subtitle2" sx={{ 
          color: '#9E9EB8', 
          letterSpacing: 1, 
          fontSize: 11, 
          textTransform: 'uppercase',
          flex: 1,
        }}>
          AI Alert System
        </Typography>
        <Chip 
          label={isHealthy ? 'ONLINE' : 'OFFLINE'}
          size="small"
          sx={{
            height: 18,
            fontSize: 9,
            fontWeight: 700,
            background: isHealthy ? '#A8FF3E18' : '#F4433618',
            color: isHealthy ? '#A8FF3E' : '#F44336',
            border: `1px solid ${isHealthy ? '#A8FF3E40' : '#F4433640'}`,
          }}
        />
      </Box>

      {/* Stall Detection Controls */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 10, display: 'block', mb: 1 }}>
          Stall Detection Parameters
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1.5, mb: 1.5 }}>
          <TextField
            label="Stall Time (min)"
            type="number"
            size="small"
            value={stallMinutes}
            onChange={(e) => setStallMinutes(Number(e.target.value))}
            sx={{
              flex: 1,
              '& .MuiOutlinedInput-root': {
                background: '#0A0A14',
                '& fieldset': { borderColor: '#1E1E2E' },
              },
              '& .MuiInputLabel-root': { fontSize: 11 },
              '& input': { fontSize: 12, fontFamily: 'monospace' },
            }}
          />
          
          <TextField
            label="Speed Threshold (km/h)"
            type="number"
            size="small"
            value={speedThreshold}
            onChange={(e) => setSpeedThreshold(Number(e.target.value))}
            sx={{
              flex: 1,
              '& .MuiOutlinedInput-root': {
                background: '#0A0A14',
                '& fieldset': { borderColor: '#1E1E2E' },
              },
              '& .MuiInputLabel-root': { fontSize: 11 },
              '& input': { fontSize: 12, fontFamily: 'monospace' },
            }}
          />
        </Box>

        <Button
          fullWidth
          variant="contained"
          onClick={handleCheckStalls}
          disabled={stallCheckMutation.isPending}
          sx={{
            background: 'linear-gradient(135deg, #00E5FF 0%, #0099CC 100%)',
            color: '#0A0A14',
            fontWeight: 700,
            fontSize: 11,
            py: 1,
            '&:hover': { background: 'linear-gradient(135deg, #00F5FF 0%, #00AADD 100%)' },
            '&:disabled': { background: '#1E1E2E', color: '#555' },
          }}
        >
          {stallCheckMutation.isPending ? 'Checking...' : 'Run Stall Detection'}
        </Button>
      </Box>

      {/* Last check results */}
      {stallCheckMutation.data && (
        <Box sx={{ 
          background: '#0A0A14', 
          border: '1px solid #1E1E2E',
          borderRadius: 1,
          p: 1.5,
        }}>
          <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 10, display: 'block', mb: 0.5 }}>
            Last Check Results
          </Typography>
          {stallCheckMutation.data.data.created_alerts.length === 0 ? (
            <Typography variant="caption" sx={{ color: '#A8FF3E', fontSize: 11 }}>
              ✓ All shipments moving normally
            </Typography>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              {stallCheckMutation.data.data.created_alerts.map((alert, i) => (
                <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ 
                    width: 4, height: 4, borderRadius: '50%', 
                    background: '#F44336', flexShrink: 0,
                  }} />
                  <Typography variant="caption" sx={{ color: '#F44336', fontSize: 10, fontFamily: 'monospace' }}>
                    {alert.shipment_id}: {alert.reason}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
        </Box>
      )}

      {/* Info footer */}
      <Box sx={{ 
        mt: 2, 
        pt: 2, 
        borderTop: '1px solid #1E1E2E',
      }}>
        <Typography variant="caption" sx={{ color: '#555', fontSize: 9 }}>
          AI-powered detection: Shipment stalls, driver safety anomalies
        </Typography>
      </Box>
    </Box>
  );
};