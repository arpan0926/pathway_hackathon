import { apiClient } from './client';
import type { Alert } from '../types';

export const alertsApi = {
  getAll: (shipment_id?: string, is_active?: boolean) =>
    apiClient.get<Alert[]>('/api/alerts', { params: { shipment_id, is_active } }),
  
  getCritical: () =>
    apiClient.get<Alert[]>('/api/alerts/critical'),
};