import { Box, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { telemetryApi } from '../../api/telemetry';
import { format } from 'date-fns';

const SHIPMENT_COLORS: Record<string, string> = {
  SH001: '#00E5FF',
  SH002: '#FF6B35',
};

export const SpeedChart = () => {
  const { data: telemetry = [] } = useQuery({
    queryKey: ['telemetry-speed'],
    queryFn: () => telemetryApi.getAll(undefined, 60).then(r => r.data),
    refetchInterval: 5000,
  });

  // Group by time bucket and shipment
  const chartData = telemetry
    .slice()
    .reverse()
    .reduce<Record<string, any>>((acc, t) => {
      const key = format(new Date(t.ts), 'HH:mm:ss');
      if (!acc[key]) acc[key] = { time: key };
      acc[key][t.shipment_id] = parseFloat(t.speed_kmph.toFixed(1));
      return acc;
    }, {});

  const data = Object.values(chartData).slice(-20); // last 20 data points
  const shipmentIds = [...new Set(telemetry.map(t => t.shipment_id))];

  return (
    <Box sx={{ background: '#111120', border: '1px solid #1E1E2E', borderRadius: 2, p: 2.5 }}>
      <Typography variant="subtitle2" sx={{ color: '#9E9EB8', letterSpacing: 1, fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
        Fleet Speed (km/h)
      </Typography>

      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
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
            domain={[0, 120]}
            unit=" km/h"
          />
          <Tooltip
            contentStyle={{ background: '#0A0A14', border: '1px solid #2A2A3E', borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: '#9E9EB8' }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {shipmentIds.map(id => (
            <Line
              key={id}
              type="monotone"
              dataKey={id}
              stroke={SHIPMENT_COLORS[id] ?? '#888'}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};