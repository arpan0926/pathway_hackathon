import { useEffect } from 'react';
import { io } from 'socket.io-client';
import { useStore } from '../store/useStore';
import type { Alert, Telemetry } from '../types';
import toast from 'react-hot-toast';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000';

export const useSocket = () => {
  const { addAlert, updatePosition } = useStore();

  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ['websocket'] });

    socket.on('connect', () => {
      console.log('🔌 Socket connected');
    });
    
    // Listen for real-time telemetry updates
    socket.on('telemetry_update', (data: Telemetry) => {
      updatePosition(data.shipment_id, data);
    });
    
    // Listen for new alerts (including driver safety)
    socket.on('new_alert', (alert: Alert) => {
      console.log('🚨 New alert received:', alert);
      addAlert(alert);
      
      // Show toast notification for critical alerts
    if (alert.metric === 'driver_safety' && alert.value) {
  const status = alert.value.toUpperCase();

  const emojiMap: Record<string, string> = {
    DROWSY: '😴',
    HEAD_DOWN: '⬇️',
    DRUNK: '🍺',
    ACTIVE: '✅'
  };

  const emoji = emojiMap[status] || '⚠️';

  toast.error(
    `${emoji} Driver Alert: ${status} - ${alert.shipment_id}`,
    { duration: 5000 }
  );
}
    });

    socket.on('disconnect', () => {
      console.log('🔌 Socket disconnected');
    });

    return () => { socket.disconnect(); };
  }, [addAlert, updatePosition]);
};