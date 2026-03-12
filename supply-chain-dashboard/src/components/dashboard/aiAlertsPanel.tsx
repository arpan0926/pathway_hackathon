import { useState } from 'react';
import { Box, Typography, Button, TextField, Chip, Tabs, Tab } from '@mui/material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { aiAlertsApi } from '../../api/aiAlerts';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import toast from 'react-hot-toast';

export const AIAlertsPanel = () => {
  const [activeTab, setActiveTab] = useState(0);
  
  // Stall detection state
  const [stallMinutes, setStallMinutes] = useState(15);
  const [speedThreshold, setSpeedThreshold] = useState(5);

  // Overspeed detection state
  const [speedLimit, setSpeedLimit] = useState(80);
  const [checkDuration, setCheckDuration] = useState(10);

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

  // ADD THIS: Overspeed check mutation
  const overspeedCheckMutation = useMutation({
    mutationFn: aiAlertsApi.checkOverspeed,
    onSuccess: (data) => {
      const count = data.data.created_alerts.length;
      if (count > 0) {
        toast.error(`⚡ ${count} overspeed alert${count > 1 ? 's' : ''} created!`);
      } else {
        toast.success('✓ No overspeeding detected');
      }
    },
    onError: () => {
      toast.error('Failed to check overspeeding');
    },
  });

  const handleCheckStalls = () => {
    stallCheckMutation.mutate({
      stall_minutes: stallMinutes,
      speed_threshold_kmph: speedThreshold,
      max_move_meters: 100,
    });
  };

  const handleCheckOverspeed = () => {
    overspeedCheckMutation.mutate({
      speed_limit_kmph: speedLimit,
      duration_minutes: checkDuration,
      min_violations: 5,
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

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onChange={(_, newValue) => setActiveTab(newValue)}
        sx={{
          mb: 2,
          minHeight: 32,
          '& .MuiTab-root': {
            minHeight: 32,
            fontSize: 10,
            color: '#666',
            textTransform: 'none',
            py: 0.5,
          },
          '& .Mui-selected': {
            color: '#00E5FF !important',
          },
          '& .MuiTabs-indicator': {
            backgroundColor: '#00E5FF',
          },
        }}
      >
        <Tab label="Stall Detection" />
        <Tab label="Overspeed Detection" />
      </Tabs>

      {/* Tab 0: Stall Detection */}
      {activeTab === 0 && (
        <Box>
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

          {stallCheckMutation.data && (
            <Box sx={{ 
              background: '#0A0A14', 
              border: '1px solid #1E1E2E',
              borderRadius: 1,
              p: 1.5,
              mt: 1.5,
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
        </Box>
      )}

      {/* Tab 1: Overspeed Detection */}
      {activeTab === 1 && (
        <Box>
          <Typography variant="caption" sx={{ color: '#9E9EB8', fontSize: 10, display: 'block', mb: 1 }}>
            Overspeed Detection Parameters
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1.5, mb: 1.5 }}>
            <TextField
              label="Speed Limit (km/h)"
              type="number"
              size="small"
              value={speedLimit}
              onChange={(e) => setSpeedLimit(Number(e.target.value))}
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
              label="Check Window (min)"
              type="number"
              size="small"
              value={checkDuration}
              onChange={(e) => setCheckDuration(Number(e.target.value))}
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
            onClick={handleCheckOverspeed}
            disabled={overspeedCheckMutation.isPending}
            sx={{
              background: 'linear-gradient(135deg, #FF6B35 0%, #CC5528 100%)',
              color: '#FFF',
              fontWeight: 700,
              fontSize: 11,
              py: 1,
              '&:hover': { background: 'linear-gradient(135deg, #FF7B45 0%, #DD6638 100%)' },
              '&:disabled': { background: '#1E1E2E', color: '#555' },
            }}
          >
            {overspeedCheckMutation.isPending ? 'Checking...' : 'Run Overspeed Detection'}
          </Button>

          {overspeedCheckMutation.data && (
            <Box sx={{ 
              background: '#0A0A14', 
              border: '1px solid #1E1E2E',
              borderRadius: 1,
              p: 1.5,
              mt: 1.5,
            }}>
              <Typography variant="caption" sx={{ color: '#9E9EB9', fontSize: 10, display: 'block', mb: 0.5 }}>
                Last Check Results
              </Typography>
              {overspeedCheckMutation.data.data.created_alerts.length === 0 ? (
                <Typography variant="caption" sx={{ color: '#A8FF3E', fontSize: 11 }}>
                  ✓ All shipments within speed limits
                </Typography>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                  {overspeedCheckMutation.data.data.created_alerts.map((alert, i) => (
                    <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                      <Box sx={{ 
                        width: 4, height: 4, borderRadius: '50%', 
                        background: '#FF6B35', flexShrink: 0, mt: 0.5,
                      }} />
                      <Typography variant="caption" sx={{ color: '#FF6B35', fontSize: 10, fontFamily: 'monospace', lineHeight: 1.4 }}>
                        {alert.shipment_id}: {alert.reason}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
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
          AI-powered detection: Stalls, overspeeding, driver safety
        </Typography>
      </Box>
    </Box>
  );
};