import { apiClient } from './client';
import type { ETAHistory } from '../types';

export const etaApi = {
  getHistory: (shipment_id?: string) =>
    apiClient.get<ETAHistory[]>('/api/eta-history', { params: { shipment_id } }),
  
  getLatest: (shipment_id: string) =>
    apiClient.get<ETAHistory>(`/api/eta-history/latest/${shipment_id}`),
};