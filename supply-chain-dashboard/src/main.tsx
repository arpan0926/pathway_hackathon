import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import App from './App';
import './index.css';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#00E5FF' },
    secondary: { main: '#FF6B35' },
    background: { default: '#0A0A14', paper: '#111120' },
    text: { primary: '#E8EAF6', secondary: '#9E9EB8' },
  },
  typography: {
    fontFamily: '"JetBrains Mono", "Space Mono", monospace',
  },
  shape: { borderRadius: 8 },
  components: {
    MuiPaper: {
      styleOverrides: { root: { backgroundImage: 'none' } },
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);