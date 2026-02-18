import { useEffect } from 'react';
import { io } from 'socket.io-client';
import { useStore } from '../store/useStore';
import type { Alert, Telemetry } from '../types';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000';

export const useSocket = () => {
  const { addAlert, updatePosition } = useStore();

  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ['websocket'] });

    socket.on('connect', () => console.log('🔌 Socket connected'));
    
    // Listen for real-time telemetry updates from GPS simulator
    socket.on('telemetry_update', (data: Telemetry) => {
      updatePosition(data.shipment_id, data);
    });
    
    // Listen for new alerts from pipeline
    socket.on('new_alert', (alert: Alert) => {
      addAlert(alert);
    });

    return () => { socket.disconnect(); };
  }, [addAlert, updatePosition]);
};