import api from './authApi';
import type { RoomPricing, RoomPricingCreate, RoomPricingUpdate, PricingOptions } from '../types/pricing';

export const pricingApi = {
  // Tüm fiyatları getir
  getAllPrices: () =>
    api.get<RoomPricing[]>('/pricing/').then((r) => r.data),

  // Aktif fiyatları getir
  getActivePrices: () =>
    api.get<RoomPricing[]>('/pricing/active').then((r) => r.data),

  // ID'ye göre getir
  getPriceById: (id: number) =>
    api.get<RoomPricing>(`/pricing/${id}`).then((r) => r.data),

  // Oda tipi ve kapasiteye göre getir
  getPriceByTypeAndCapacity: (roomType: string, capacity: string) =>
    api.get<RoomPricing>(`/pricing/type/${roomType}/capacity/${capacity}`).then((r) => r.data),

  // Fiyat oluştur
  createPrice: (data: RoomPricingCreate) =>
    api.post<RoomPricing>('/pricing/', data).then((r) => r.data),

  // Fiyat güncelle
  updatePrice: (id: number, data: RoomPricingUpdate) =>
    api.put<RoomPricing>(`/pricing/${id}`, data).then((r) => r.data),

  // Fiyat sil
  deletePrice: (id: number) =>
    api.delete(`/pricing/${id}`).then((r) => r.data),

  // Fiyatı aktif/pasif yap
  toggleActive: (id: number) =>
    api.patch<RoomPricing>(`/pricing/${id}/toggle`).then((r) => r.data),

  // Oda tipi ve kapasite seçeneklerini getir
  getOptions: () =>
    api.get<PricingOptions>('/pricing/options').then((r) => r.data),

  // Fiyat matrisini getir
  getPriceMatrix: () =>
    api.get<any>('/pricing/matrix').then((r) => r.data),

  // Toplu fiyat güncelleme
  bulkUpdate: (data: RoomPricing[]) =>
    api.post('/pricing/bulk', data).then((r) => r.data),
};

