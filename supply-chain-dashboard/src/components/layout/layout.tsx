import { Box } from '@mui/material';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { useStore } from '../../store/useStore';
import { ChatBot } from '../chatBot/chatbot'

export const Layout = ({ children }: { children: React.ReactNode }) => {
  const { sidebarCollapsed, isChatOpen } = useStore();
  const sidebarW = sidebarCollapsed ? 60 : 220;

  return (
    <Box sx={{ display: 'flex', height: '100vh', background: '#0A0A14', color: '#E8EAF6', overflow: 'hidden' }}>
      <Sidebar />

      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', ml: `${sidebarW}px`, transition: 'margin 0.2s', minWidth: 0 }}>
        <TopBar />
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {children}
        </Box>
      </Box>

      {/* Sliding chat panel */}
      <Box sx={{
        position: 'fixed', right: 0, top: 0, bottom: 0,
        width: isChatOpen ? 360 : 0,
        transition: 'width 0.25s ease',
        background: '#0D0D1A',
        borderLeft: isChatOpen ? '1px solid #1E1E2E' : 'none',
        overflow: 'hidden',
        zIndex: 1200,
        display: 'flex',
        flexDirection: 'column',
      }}>
        {isChatOpen && (
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid #1E1E2E', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Box sx={{ fontSize: 13, fontWeight: 600 }}>Supply Chain Assistant</Box>
                <Box sx={{ fontSize: 10, color: '#555' }}>RAG · powered by your docs</Box>
              </Box>
              <Box onClick={() => useStore.getState().toggleChat()}
                sx={{ cursor: 'pointer', color: '#555', fontSize: 18, lineHeight: 1, '&:hover': { color: '#fff' } }}>✕</Box>
            </Box>
            <Box sx={{ flex: 1, minHeight: 0 }}>
              <ChatBot />
            </Box>
          </Box>
        )}
      </Box>
    </Box>
  );
};