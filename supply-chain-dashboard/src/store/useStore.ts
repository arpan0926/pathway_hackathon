import { create } from 'zustand';
import type { Alert, Shipment, Telemetry } from '../types';

interface AppState {
  // Live data
  activeShipments: Shipment[];
  liveAlerts: Alert[];
  latestPositions: Record<string, Telemetry>; // keyed by shipment_id
  
  // UI state
  selectedShipmentId: string | null;
  isChatOpen: boolean;
  sidebarCollapsed: boolean;
  
  // Actions
  setActiveShipments: (shipments: Shipment[]) => void;
  addAlert: (alert: Alert) => void;
  updatePosition: (shipment_id: string, telemetry: Telemetry) => void;
  setSelectedShipment: (id: string | null) => void;
  toggleChat: () => void;
  toggleSidebar: () => void;
}

export const useStore = create<AppState>((set) => ({
  activeShipments: [],
  liveAlerts: [],
  latestPositions: {},
  selectedShipmentId: null,
  isChatOpen: false,
  sidebarCollapsed: false,

  setActiveShipments: (shipments) => set({ activeShipments: shipments }),
  
  addAlert: (alert) =>
    set((state) => ({ liveAlerts: [alert, ...state.liveAlerts].slice(0, 50) })),
  
  updatePosition: (shipment_id, telemetry) =>
    set((state) => ({
      latestPositions: { ...state.latestPositions, [shipment_id]: telemetry },
    })),
  
  setSelectedShipment: (id) => set({ selectedShipmentId: id }),
  toggleChat: () => set((state) => ({ isChatOpen: !state.isChatOpen })),
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}));