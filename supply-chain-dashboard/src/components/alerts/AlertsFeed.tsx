
import { Box, Typography, Chip } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { alertsApi } from '../../api/alerts';
import type { Alert } from '../../types';
import { formatDistanceToNow } from 'date-fns';

const ALERT_COLORS: Record<string, string> = {
  delay: '#FFB300',
  critical: '#F44336',
  temperature_breach: '#FF6B35',
  info: '#00E5FF',
};

export const AlertsFeed = () => {
  const { data: alerts = [] } = useQuery({
    queryKey: ['alerts', true],
    queryFn: () => alertsApi.getAll(undefined, true).then(r => r.data),
    refetchInterval: 5000,
  });

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid #1E1E2E' }}>
        <Typography variant="subtitle2" sx={{ color: '#9E9EB8', letterSpacing: 1, fontSize: 11, textTransform: 'uppercase' }}>
          Live Alerts
        </Typography>
      </Box>

      <Box sx={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
        {alerts.length === 0 ? (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
            <Typography variant="body2" color="text.secondary">No active alerts</Typography>
          </Box>
        ) : (
          alerts.map((alert) => (
            <AlertRow key={alert.alert_id} alert={alert} />
          ))
        )}
      </Box>
    </Box>
  );
};

const AlertRow = ({ alert }: { alert: Alert }) => {
  const color = ALERT_COLORS[alert.alert_type] ?? '#9E9EB8';

  return (
    <Box sx={{
      px: 2, py: 1.5,
      borderBottom: '1px solid #1A1A2A',
      borderLeft: `3px solid ${color}`,
      '&:hover': { background: '#13131F' },
      transition: 'background 0.15s',
    }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}>
        <Typography variant="body2" sx={{ fontWeight: 600, fontSize: 13 }}>
          {alert.shipment_id}
        </Typography>
        <Chip
          label={alert.alert_type.replace('_', ' ')}
          size="small"
          sx={{
            height: 18, fontSize: 10,
            background: `${color}20`,
            color: color,
            border: `1px solid ${color}40`,
          }}
        />
      </Box>

      {alert.metric && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
          {alert.metric}: {alert.value} (threshold: {alert.threshold})
        </Typography>
      )}

      <Typography variant="caption" sx={{ color: '#555', fontSize: 10 }}>
        {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
      </Typography>
    </Box>
  );
};