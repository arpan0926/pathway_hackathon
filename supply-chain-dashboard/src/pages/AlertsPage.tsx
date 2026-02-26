import { useState } from 'react';
import { Box, Typography, Chip, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { alertsApi } from '../api/alerts';
import type { Alert } from '../types';
import { formatDistanceToNow } from 'date-fns';

const ALERT_COLORS: Record<string, string> = {
  delay: '#FFB300',
  critical: '#F44336',
  temperature_breach: '#FF6B35',
  info: '#00E5FF',
};

export const AlertsPage = () => {
  const [filter, setFilter] = useState<'all' | 'active'>('active');

  const { data: alerts = [], isLoading } = useQuery({
    queryKey: ['alerts-page', filter],
    queryFn: () => alertsApi.getAll(undefined, filter === 'active' ? true : undefined).then(r => r.data),
    refetchInterval: 5000,
  });

  const counts = alerts.reduce<Record<string, number>>((acc, a) => {
    acc[a.alert_type] = (acc[a.alert_type] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>Alerts</Typography>
          <Typography variant="caption" color="text.secondary">
            {alerts.length} {filter === 'active' ? 'active' : 'total'} alerts
          </Typography>
        </Box>
        <ToggleButtonGroup
          value={filter}
          exclusive
          onChange={(_, v) => v && setFilter(v)}
          size="small"
          sx={{ '& .MuiToggleButton-root': { px: 2, fontSize: 12, borderColor: '#1E1E2E', color: '#9E9EB8',
            '&.Mui-selected': { background: '#00E5FF18', color: '#00E5FF', borderColor: '#00E5FF40' } } }}
        >
          <ToggleButton value="active">Active</ToggleButton>
          <ToggleButton value="all">All</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Summary chips */}
      <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
        {Object.entries(counts).map(([type, count]) => {
          const color = ALERT_COLORS[type] ?? '#9E9EB8';
          return (
            <Chip key={type} label={`${type.replace('_', ' ')} · ${count}`} size="small"
              sx={{ background: `${color}18`, color, border: `1px solid ${color}40`, fontSize: 11 }} />
          );
        })}
      </Box>

      {/* Alert list */}
      <Box sx={{ background: '#111120', borderRadius: 2, border: '1px solid #1E1E2E', overflow: 'hidden' }}>
        {isLoading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">Loading alerts...</Typography>
          </Box>
        ) : alerts.length === 0 ? (
          <Box sx={{ p: 6, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">No alerts found</Typography>
          </Box>
        ) : (
          alerts.map(alert => <AlertItem key={alert.alert_id} alert={alert} />)
        )}
      </Box>
    </Box>
  );
};

const AlertItem = ({ alert }: { alert: Alert }) => {
  const color = ALERT_COLORS[alert.alert_type] ?? '#9E9EB8';
  return (
    <Box sx={{
      px: 3, py: 2,
      borderBottom: '1px solid #1A1A2A',
      borderLeft: `3px solid ${color}`,
      display: 'flex', alignItems: 'center', gap: 3,
      '&:last-child': { borderBottom: 0 },
      '&:hover': { background: '#13131F' },
      transition: 'background 0.15s',
    }}>
      <Box sx={{ flex: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
          <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
            {alert.shipment_id}
          </Typography>
          <Chip label={alert.alert_type.replace('_', ' ')} size="small"
            sx={{ height: 18, fontSize: 10, background: `${color}18`, color, border: `1px solid ${color}40` }} />
          {!alert.is_active && (
            <Chip label="resolved" size="small"
              sx={{ height: 18, fontSize: 10, background: '#A8FF3E18', color: '#A8FF3E', border: '1px solid #A8FF3E40' }} />
          )}
        </Box>
        {alert.metric && (
          <Typography variant="caption" color="text.secondary">
            {alert.metric}: <span style={{ color: '#fff' }}>{alert.value}</span>
            {alert.threshold && ` (threshold: ${alert.threshold})`}
          </Typography>
        )}
      </Box>
      <Typography variant="caption" sx={{ color: '#555', whiteSpace: 'nowrap' }}>
        {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
      </Typography>
    </Box>
  );
};