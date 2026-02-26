import { apiClient } from './client';
import type { Telemetry } from '../types';

export const telemetryApi = {
  // Get all telemetry, optionally filtered by shipment
  getAll: (shipment_id?: string, limit = 100) =>
    apiClient.get<Telemetry[]>('/api/telemetry', {
      params: { shipment_id, limit },
    }),

  // Get latest single GPS point for a shipment
  getLatest: (shipment_id: string) =>
    apiClient.get<Telemetry>(`/api/telemetry/latest/${shipment_id}`),
};