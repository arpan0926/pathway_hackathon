import { useQuery } from '@tanstack/react-query';
import { shipmentsApi } from '../api/shipment';

export const useShipments = (status?: string) =>
  useQuery({
    queryKey: ['shipments', status],
    queryFn: () => shipmentsApi.getAll(status).then(r => r.data),
    refetchInterval: 5000, // Poll every 5s (or use WebSocket below)
  });

export const useShipmentById = (id: string) =>
  useQuery({
    queryKey: ['shipment', id],
    queryFn: () => shipmentsApi.getById(id).then(r => r.data),
    enabled: !!id,
  });

export const useStats = () =>
  useQuery({
    queryKey: ['stats'],
    queryFn: () => shipmentsApi.getStats().then(r => r.data),
    refetchInterval: 10000,
  });