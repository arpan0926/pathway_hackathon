import { Box, Typography } from '@mui/material';
import { Grid } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { etaApi } from '../api/eta';
import { telemetryApi } from '../api/telemetry';
import { format } from 'date-fns';

export const AnalyticsPage = () => {
  const { data: etaHistory = [] } = useQuery({
    queryKey: ['eta-analytics'],
    queryFn: () => etaApi.getHistory().then(r => r.data),
    refetchInterval: 15000,
  });

  const { data: telemetry = [] } = useQuery({
    queryKey: ['telemetry-analytics'],
    queryFn: () => telemetryApi.getAll(undefined, 200).then(r => r.data),
    refetchInterval: 10000,
  });

  // Confidence over time
  const confidenceData = etaHistory.slice().reverse().slice(-30).map(e => ({
    time: format(new Date(e.computed_at), 'HH:mm'),
    confidence: e.confidence ?? 0,
    shipment: e.shipment_id,
  }));

  // Speed distribution buckets
  const buckets: Record<string, number> = { '0–20': 0, '20–40': 0, '40–60': 0, '60–80': 0, '80–100': 0, '100+': 0 };
  telemetry.forEach(t => {
    const s = t.speed_kmph;
    if (s < 20) buckets['0–20']++;
    else if (s < 40) buckets['20–40']++;
    else if (s < 60) buckets['40–60']++;
    else if (s < 80) buckets['60–80']++;
    else if (s < 100) buckets['80–100']++;
    else buckets['100+']++;
  });
  const speedDist = Object.entries(buckets).map(([range, count]) => ({ range, count }));

  // Avg speed per shipment
  const speedByShipment = telemetry.reduce<Record<string, number[]>>((acc, t) => {
    if (!acc[t.shipment_id]) acc[t.shipment_id] = [];
    acc[t.shipment_id].push(t.speed_kmph);
    return acc;
  }, {});
  const avgSpeedData = Object.entries(speedByShipment).map(([id, speeds]) => ({
    id,
    avg: parseFloat((speeds.reduce((a, b) => a + b, 0) / speeds.length).toFixed(1)),
  }));

  const chartCard = (title: string, children: React.ReactNode) => (
    <Box sx={{ background: '#111120', border: '1px solid #1E1E2E', borderRadius: 2, p: 2.5 }}>
      <Typography variant="subtitle2" sx={{ color: '#9E9EB8', letterSpacing: 1, fontSize: 11, textTransform: 'uppercase', mb: 2 }}>
        {title}
      </Typography>
      {children}
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>Analytics</Typography>
        <Typography variant="caption" color="text.secondary">
          Based on {telemetry.length} telemetry records · {etaHistory.length} ETA predictions
        </Typography>
      </Box>

      <Grid container spacing={2}>
        {/* Speed distribution */}
        <Grid size={{ xs: 12, md: 6 }}>
          {chartCard('Speed Distribution', (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={speedDist}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" />
                <XAxis dataKey="range" tick={{ fill: '#555', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#1E1E2E' }} />
                <YAxis tick={{ fill: '#555', fontSize: 11 }} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ background: '#0A0A14', border: '1px solid #2A2A3E', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {speedDist.map((_, i) => (
                    <Cell key={i} fill={i < 2 ? '#F44336' : i < 4 ? '#00E5FF' : '#FFB300'} fillOpacity={0.8} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ))}
        </Grid>

        {/* Avg speed per shipment */}
        <Grid size={{ xs: 12, md: 6 }}>
          {chartCard('Avg Speed per Shipment', (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={avgSpeedData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" />
                <XAxis type="number" tick={{ fill: '#555', fontSize: 11 }} tickLine={false} axisLine={false} unit=" km/h" />
                <YAxis type="category" dataKey="id" tick={{ fill: '#9E9EB8', fontSize: 12, fontFamily: 'monospace' }} tickLine={false} axisLine={false} width={50} />
                <Tooltip contentStyle={{ background: '#0A0A14', border: '1px solid #2A2A3E', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="avg" radius={[0, 4, 4, 0]} fill="#00E5FF" fillOpacity={0.8} />
              </BarChart>
            </ResponsiveContainer>
          ))}
        </Grid>

        {/* ETA confidence over time */}
        <Grid size={{ xs: 12}}>
          {chartCard('ETA Prediction Confidence Over Time (%)', (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={confidenceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E1E2E" />
                <XAxis dataKey="time" tick={{ fill: '#555', fontSize: 10 }} tickLine={false} axisLine={{ stroke: '#1E1E2E' }} interval="preserveStartEnd" />
                <YAxis tick={{ fill: '#555', fontSize: 10 }} tickLine={false} axisLine={false} domain={[0, 100]} unit="%" />
                <Tooltip contentStyle={{ background: '#0A0A14', border: '1px solid #2A2A3E', borderRadius: 8, fontSize: 12 }} />
                <Line type="monotone" dataKey="confidence" stroke="#A8FF3E" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          ))}
        </Grid>
      </Grid>
    </Box>
  );
};