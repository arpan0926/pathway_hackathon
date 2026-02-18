import { apiClient } from './client';
import type { Shipment,Stats } from '../types';

export const shipmentsApi = {
  getAll: (status?: string) =>
    apiClient.get<Shipment[]>('/api/shipments', { params: { status } }),
  
  getById: (id: string) =>
    apiClient.get<Shipment>(`/api/shipments/${id}`),
  
  getStats: () =>
    apiClient.get<Stats>('/api/stats'),
};