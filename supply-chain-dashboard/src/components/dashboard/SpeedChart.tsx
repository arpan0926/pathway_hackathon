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
  SH003: '#A8FF3E',
  SH004: '#FFB300',
};

export const SpeedChart = () => {
  const { data: telemetry = [] } = useQuery({
    queryKey: ['telemetry-speed'],
    queryFn: () => telemetryApi.getAll(undefined, 100).then(r => r.data),
    refetchInterval: 5000,
  });

  // Get last 30 points per shipment
  const shipmentData: Record<string, any[]> = {};
  
  telemetry.forEach(t => {
    if (!shipmentData[t.shipment_id]) {
      shipmentData[t.shipment_id] = [];
    }
    shipmentData[t.shipment_id].push(t);
  });

  // Build time series - take last 30 points
  const timePoints: Record<string, any> = {};
  
  Object.entries(shipmentData).forEach(([shipId, data]) => {
    const sorted = data.sort((a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime()).slice(-30);
    
    sorted.forEach(t => {
      const timeKey = format(new Date(t.ts), 'HH:mm:ss');
      if (!timePoints[timeKey]) {
        timePoints[timeKey] = { time: timeKey };
      }
      timePoints[timeKey][shipId] = parseFloat(t.speed_kmph.toFixed(1));
    });
  });

  const chartData = Object.values(timePoints).slice(-20); // Show last 20 time points
  const shipmentIds = Object.keys(shipmentData);

  return (
    <Box sx={{ background: '#111120', border: '1px solid #1E1E2E', borderRadius: 2, p: 2.5 }}>
      <Typography variant="subtitle2" sx={{ 
        color: '#9E9EB8', letterSpacing: 1, fontSize: 11, textTransform: 'uppercase', mb: 2 
      }}>
        Fleet Speed (km/h)
      </Typography>

      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData}>
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
            domain={[0, 100]}
            label={{ value: 'km/h', angle: -90, position: 'insideLeft', fill: '#555', fontSize: 10 }}
          />
          <Tooltip
            contentStyle={{ 
              background: '#0A0A14', 
              border: '1px solid #2A2A3E', 
              borderRadius: 8, 
              fontSize: 12 
            }}
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
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};