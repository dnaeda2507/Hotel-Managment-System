import api from './authApi'; // Mevcut axios instance'ını kullanıyoruz
import type { Room } from '../types/room';

export const roomApi = {
  // Tüm odaları getir
  getRooms: () => 
    api.get<Room[]>('/rooms/').then((r) => r.data),

  // Yeni oda ekle
  createRoom: (data: Partial<Room>) => 
    api.post<Room>('/rooms/', data).then((r) => r.data),
    
  // Oda durumunu güncelle (Temizlik/Bakım için)
  updateRoom: (id: number, data: Partial<Room>) =>
    api.put<Room>(`/rooms/${id}`, data).then((r) => r.data)
};