import { Box, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { etaApi } from '../../api/eta';
import { format } from 'date-fns';

const SHIPMENT_COLORS: Record<string, string> = {
  SH001: '#00E5FF',
  SH002: '#FF6B35',
};

export const ETAChart = () => {
  const { data: etaHistory = [] } = useQuery({
    queryKey: ['eta-history'],
    queryFn: () => etaApi.getHistory().then(r => r.data),
    refetchInterval: 10000,
  });

  const chartData = etaHistory
    .slice()
    .reverse()
    .reduce<Record<string, any>>((acc, e) => {
      const key = format(new Date(e.computed_at), 'HH:mm');
      if (!acc[key]) acc[key] = { time: key };
      if (e.distance_remaining_km !== null) {
        acc[key][e.shipment_id] = parseFloat(e.distance_remaining_km.toFixed(1));
      }
      return acc;
    }, {});

  const data = Object.values(chartData).slice(-20);
  const shipmentIds = [...new Set(etaHistory.map(e => e.shipment_id))];

  return (
    <Box sx={{ background: '#111120', border: '1px solid #1E1E2E', borderRadius: 2, p: 2.5 }}>
      <Typography variant="subtitle2" sx={{ color: '#9E9EB8', letterSpacing: 1, fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
        Distance Remaining (km)
      </Typography>

      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data}>
          <defs>
            {shipmentIds.map(id => (
              <linearGradient key={id} id={`grad-${id}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={SHIPMENT_COLORS[id] ?? '#888'} stopOpacity={0.2} />
                <stop offset="95%" stopColor={SHIPMENT_COLORS[id] ?? '#888'} stopOpacity={0} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" />
          <XAxis
            dataKey="time"
            tick={{ fill: '#555', fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: '#1E1E2E' }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: '#555', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            unit=" km"
          />
          <Tooltip
            contentStyle={{ background: '#0A0A14', border: '1px solid #2A2A3E', borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: '#9E9EB8' }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {shipmentIds.map(id => (
            <Area
              key={id}
              type="monotone"
              dataKey={id}
              stroke={SHIPMENT_COLORS[id] ?? '#888'}
              strokeWidth={2}
              fill={`url(#grad-${id})`}
              dot={false}
              activeDot={{ r: 4 }}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </Box>
  );
};
