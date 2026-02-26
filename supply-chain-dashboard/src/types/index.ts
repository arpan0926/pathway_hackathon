// Mirrors your FastAPI Pydantic models exactly

export interface Shipment {
  shipment_id: string;
  vehicle_id: string;
  source: string;
  destination: string;
  status: 'IN_TRANSIT' | 'DELIVERED' | 'DELAYED' | 'PENDING';
  current_eta: string | null;
  last_updated: string;
}

export interface Telemetry {
  id: number;
  ts: string;
  vehicle_id: string;
  shipment_id: string;
  lat: number;
  lon: number;
  speed_kmph: number;
  load_status: 'LOADED' | 'PARTIAL' | 'EMPTY';
}

export interface Alert {
  alert_id: number;
  shipment_id: string;
  alert_type: string;
  metric: string | null;
  value: string | null;
  threshold: string | null;
  created_at: string;
  is_active: boolean;
}

export interface ETAHistory {
  id: number;
  shipment_id: string;
  predicted_eta: string | null;
  distance_remaining_km: number | null;
  current_speed_kmph: number | null;
  confidence: number | null;
  computed_at: string;
}

export interface Stats {
  total_shipments: number;
  active_alerts: number;
  avg_fleet_speed_kmph: number;
  total_telemetry_records: number;
  timestamp: string;
}

// For the RAG bot
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: string[];   // RAG source docs
}

export interface ChatRequest {
  query: string;
  context?: string;     // Optional shipment context
  session_id?: string;
}