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
  SH003: '#A8FF3E',
  SH004: '#FFB300',
};

export const ETAChart = () => {
  const { data: etaHistory = [] } = useQuery({
    queryKey: ['eta-history'],
    queryFn: () => etaApi.getHistory().then(r => r.data),
    refetchInterval: 10000,
  });

  // Build time series per shipment
  const shipmentData: Record<string, any[]> = {};
  
  etaHistory.forEach(e => {
    if (!shipmentData[e.shipment_id]) {
      shipmentData[e.shipment_id] = [];
    }
    shipmentData[e.shipment_id].push(e);
  });

  const timePoints: Record<string, any> = {};
  
  Object.entries(shipmentData).forEach(([shipId, data]) => {
    const sorted = data
      .sort((a, b) => new Date(a.computed_at).getTime() - new Date(b.computed_at).getTime())
      .slice(-30);
    
    sorted.forEach(e => {
      const timeKey = format(new Date(e.computed_at), 'HH:mm');
      if (!timePoints[timeKey]) {
        timePoints[timeKey] = { time: timeKey };
      }
      if (e.distance_remaining_km !== null) {
        timePoints[timeKey][shipId] = parseFloat(e.distance_remaining_km.toFixed(1));
      }
    });
  });

  const chartData = Object.values(timePoints).slice(-20);
  const shipmentIds = Object.keys(shipmentData);

  return (
    <Box sx={{ background: '#111120', border: '1px solid #1E1E2E', borderRadius: 2, p: 2.5 }}>
      <Typography variant="subtitle2" sx={{ 
        color: '#9E9EB8', letterSpacing: 1, fontSize: 11, textTransform: 'uppercase', mb: 2 
      }}>
        Distance Remaining (km)
      </Typography>

      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={chartData}>
          <defs>
            {shipmentIds.map(id => (
              <linearGradient key={id} id={`grad-${id}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={SHIPMENT_COLORS[id] ?? '#888'} stopOpacity={0.3} />
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
            label={{ value: 'km', angle: -90, position: 'insideLeft', fill: '#555', fontSize: 10 }}
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
            <Area
              key={id}
              type="monotone"
              dataKey={id}
              stroke={SHIPMENT_COLORS[id] ?? '#888'}
              strokeWidth={2}
              fill={`url(#grad-${id})`}
              dot={false}
              activeDot={{ r: 4 }}
              connectNulls
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </Box>
  );
};