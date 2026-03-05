import { Box, Tooltip } from '@mui/material';
import { NavLink } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import MapIcon from '@mui/icons-material/Map';
import NotificationsIcon from '@mui/icons-material/Notifications';
import BarChartIcon from '@mui/icons-material/BarChart';
import BuildIcon from '@mui/icons-material/Build';
import { useStore } from '../../store/useStore';

const NAV = [
  { to: '/',           icon: <DashboardIcon fontSize="small" />,     label: 'Dashboard'  },
  { to: '/shipments',  icon: <LocalShippingIcon fontSize="small" />, label: 'Shipments'  },
  { to: '/map',        icon: <MapIcon fontSize="small" />,           label: 'Live Map'   },
  { to: '/alerts',     icon: <NotificationsIcon fontSize="small" />, label: 'Alerts'     },
  { to: '/analytics',  icon: <BarChartIcon fontSize="small" />,      label: 'Analytics'  },
  { to: '/vehicle-health', icon: <BuildIcon fontSize="small" />,     label: 'Vehicle Health' },
  
];

export const Sidebar = () => {
  const { sidebarCollapsed, toggleSidebar } = useStore();
  const w = sidebarCollapsed ? 60 : 220;

  return (
    <Box sx={{
      position: 'fixed', top: 0, left: 0, bottom: 0,
      width: w, transition: 'width 0.2s',
      background: '#0D0D1A', borderRight: '1px solid #1E1E2E',
      display: 'flex', flexDirection: 'column',
      zIndex: 1100, overflow: 'hidden',
    }}>
      {/* Logo */}
      <Box sx={{ px: sidebarCollapsed ? 1.5 : 2.5, py: 2, borderBottom: '1px solid #1E1E2E',
        display: 'flex', alignItems: 'center', gap: 1.5, minHeight: 56 }}>
        <Box sx={{ width: 28, height: 28, background: '#00E5FF', borderRadius: 1,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 14, fontWeight: 800, color: '#0A0A14', flexShrink: 0 }}>
          SC
        </Box>
        {!sidebarCollapsed && (
          <Box sx={{ fontSize: 13, fontWeight: 700, letterSpacing: 0.5, whiteSpace: 'nowrap' }}>
            Supply Chain
          </Box>
        )}
      </Box>

      {/* Nav */}
      <Box sx={{ flex: 1, py: 1 }}>
        {NAV.map(({ to, icon, label }) => (
          <Tooltip key={to} title={sidebarCollapsed ? label : ''} placement="right">
            <NavLink to={to} end={to === '/'} style={{ textDecoration: 'none' }}>
              {({ isActive }) => (
                <Box sx={{
                  display: 'flex', alignItems: 'center', gap: 1.5,
                  px: sidebarCollapsed ? 0 : 2.5, py: 1.2,
                  justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
                  color: isActive ? '#00E5FF' : '#9E9EB8',
                  background: isActive ? '#00E5FF12' : 'transparent',
                  borderLeft: isActive ? '2px solid #00E5FF' : '2px solid transparent',
                  '&:hover': { background: '#00E5FF08', color: '#E8EAF6' },
                  transition: 'all 0.15s',
                  fontSize: 13,
                }}>
                  {icon}
                  {!sidebarCollapsed && <span>{label}</span>}
                </Box>
              )}
            </NavLink>
          </Tooltip>
        ))}
      </Box>

      {/* Collapse toggle */}
      <Box onClick={toggleSidebar} sx={{
        px: 2, py: 1.5, borderTop: '1px solid #1E1E2E', cursor: 'pointer',
        color: '#555', fontSize: 12, display: 'flex', alignItems: 'center',
        justifyContent: sidebarCollapsed ? 'center' : 'flex-start', gap: 1,
        '&:hover': { color: '#9E9EB8' }, transition: 'color 0.15s',
      }}>
        {sidebarCollapsed ? '→' : '← Collapse'}
      </Box>
    </Box>
  );
};