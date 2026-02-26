import { apiClient } from './client';
const AI_ALERTS_URL = import.meta.env.VITE_AI_ALERTS_URL || 'http://localhost:8100';

const aiAlertsClient = apiClient.create({
  baseURL: AI_ALERTS_URL,
  timeout: 10000,
});

export interface StallCheckRequest {
  shipment_id?: string;
  stall_minutes?: number;
  speed_threshold_kmph?: number;
  max_move_meters?: number;
}

export interface StallCheckResponse {
  created_alerts: Array<{
    shipment_id: string;
    reason: string;
  }>;
}

export interface DriverSafetyReport {
  shipment_id: string;
  status: 'ACTIVE' | 'DROWSY' | 'HEAD_DOWN' | 'DISTRACTED';
  details?: string;
}

export const aiAlertsApi = {
  // Check database health
  healthCheck: () => 
    aiAlertsClient.get<{ db: string; value: number }>('/health/db'),

  // Check for stalled shipments
  checkStall: (request: StallCheckRequest) =>
    aiAlertsClient.post<StallCheckResponse>('/alerts/check-stall', request),

  // Report driver safety issue
  reportDriverSafety: (report: DriverSafetyReport) =>
    aiAlertsClient.post<{ status: string }>('/driver-safety/report', report),
};