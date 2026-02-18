import { Box, Typography } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import { useStore } from '../../store/useStore';
import { useQuery } from '@tanstack/react-query';
import { alertsApi } from '../../api/alerts';
import { useLocation } from 'react-router-dom';

const PAGE_TITLES: Record<string, string> = {
  '/':           'Dashboard',
  '/shipments':  'Shipments',
  '/map':        'Live Map',
  '/alerts':     'Alerts',
  '/analytics':  'Analytics',
};

export const TopBar = () => {
  const { toggleChat, isChatOpen } = useStore();
  const location = useLocation();

  const { data: critical = [] } = useQuery({
    queryKey: ['critical-alerts'],
    queryFn: () => alertsApi.getCritical().then(r => r.data),
    refetchInterval: 10000,
  });

  return (
    <Box sx={{
      height: 56, px: 3, borderBottom: '1px solid #1E1E2E',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      background: '#0A0A14', flexShrink: 0,
    }}>
      <Typography variant="h6" sx={{ fontWeight: 700, fontSize: 16 }}>
        {PAGE_TITLES[location.pathname] ?? 'Supply Chain'}
      </Typography>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {/* Critical alert badge */}
        {critical.length > 0 && (
          <Box sx={{
            background: '#F4433618', border: '1px solid #F4433640',
            borderRadius: 1, px: 1.5, py: 0.5,
            display: 'flex', alignItems: 'center', gap: 0.8,
          }}>
            <Box sx={{ width: 6, height: 6, borderRadius: '50%', background: '#F44336',
              boxShadow: '0 0 6px #F44336', animation: 'pulse 2s infinite',
              '@keyframes pulse': { '0%, 100%': { opacity: 1 }, '50%': { opacity: 0.4 } } }} />
            <Typography variant="caption" sx={{ color: '#F44336', fontWeight: 600, fontSize: 11 }}>
              {critical.length} critical
            </Typography>
          </Box>
        )}

        {/* RAG bot toggle */}
        <Box onClick={toggleChat} sx={{
          display: 'flex', alignItems: 'center', gap: 1,
          px: 1.5, py: 0.8, borderRadius: 1, cursor: 'pointer',
          background: isChatOpen ? '#00E5FF18' : 'transparent',
          border: `1px solid ${isChatOpen ? '#00E5FF40' : '#1E1E2E'}`,
          color: isChatOpen ? '#00E5FF' : '#9E9EB8',
          '&:hover': { background: '#00E5FF10', color: '#00E5FF' },
          transition: 'all 0.15s',
        }}>
          <ChatIcon sx={{ fontSize: 16 }} />
          <Typography variant="caption" sx={{ fontWeight: 600, fontSize: 11 }}>AI Assistant</Typography>
        </Box>
      </Box>
    </Box>
  );
};