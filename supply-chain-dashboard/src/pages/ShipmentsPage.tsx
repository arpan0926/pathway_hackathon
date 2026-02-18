import { useState } from 'react';
import { Box, Typography, Chip, TextField, InputAdornment, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useQuery } from '@tanstack/react-query';
import { shipmentsApi } from '../api/shipment';
import type { Shipment } from '../types';
import { formatDistanceToNow } from 'date-fns';

const STATUS_COLORS: Record<string, string> = {
  IN_TRANSIT: '#00E5FF',
  DELIVERED:  '#A8FF3E',
  DELAYED:    '#F44336',
  PENDING:    '#FFB300',
};

export const ShipmentsPage = () => {
  const [search, setSearch] = useState('');
  const { data: shipments = [], isLoading } = useQuery({
    queryKey: ['shipments'],
    queryFn: () => shipmentsApi.getAll().then(r => r.data),
    refetchInterval: 5000,
  });

  const filtered = shipments.filter(s =>
    s.shipment_id.toLowerCase().includes(search.toLowerCase()) ||
    s.source.toLowerCase().includes(search.toLowerCase()) ||
    s.destination.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>Shipments</Typography>
          <Typography variant="caption" color="text.secondary">
            {shipments.length} total · auto-refreshing
          </Typography>
        </Box>
        <TextField
          size="small"
          placeholder="Search shipments..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ fontSize: 18, color: '#555' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            width: 240,
            '& .MuiOutlinedInput-root': {
              background: '#111120',
              '& fieldset': { borderColor: '#1E1E2E' },
              '&:hover fieldset': { borderColor: '#2A2A3E' },
            },
          }}
        />
      </Box>

      <TableContainer sx={{ background: '#111120', borderRadius: 2, border: '1px solid #1E1E2E' }}>
        <Table>
          <TableHead>
            <TableRow sx={{ '& th': { borderColor: '#1E1E2E', color: '#9E9EB8', fontSize: 11, letterSpacing: 1, textTransform: 'uppercase' } }}>
              <TableCell>Shipment ID</TableCell>
              <TableCell>Vehicle</TableCell>
              <TableCell>Route</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>ETA</TableCell>
              <TableCell>Last Updated</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ color: '#555', py: 6, borderColor: '#1E1E2E' }}>
                  Loading shipments...
                </TableCell>
              </TableRow>
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ color: '#555', py: 6, borderColor: '#1E1E2E' }}>
                  No shipments found
                </TableCell>
              </TableRow>
            ) : (
              filtered.map(s => <ShipmentRow key={s.shipment_id} shipment={s} />)
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

const ShipmentRow = ({ shipment: s }: { shipment: Shipment }) => {
  const color = STATUS_COLORS[s.status] ?? '#9E9EB8';
  return (
    <TableRow sx={{
      '& td': { borderColor: '#1A1A2A' },
      '&:hover': { background: '#13131F' },
      transition: 'background 0.15s',
    }}>
      <TableCell>
        <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
          {s.shipment_id}
        </Typography>
      </TableCell>
      <TableCell>
        <Typography variant="body2" color="text.secondary">{s.vehicle_id}</Typography>
      </TableCell>
      <TableCell>
        <Typography variant="body2">
          {s.source} <span style={{ color: '#555' }}>→</span> {s.destination}
        </Typography>
      </TableCell>
      <TableCell>
        <Chip
          label={s.status.replace('_', ' ')}
          size="small"
          sx={{
            height: 20, fontSize: 10, fontWeight: 600,
            background: `${color}18`, color,
            border: `1px solid ${color}40`,
          }}
        />
      </TableCell>
      <TableCell>
        <Typography variant="body2" color="text.secondary">
          {s.current_eta ? new Date(s.current_eta).toLocaleTimeString() : '—'}
        </Typography>
      </TableCell>
      <TableCell>
        <Typography variant="caption" color="text.secondary">
          {formatDistanceToNow(new Date(s.last_updated), { addSuffix: true })}
        </Typography>
      </TableCell>
    </TableRow>
  );
};