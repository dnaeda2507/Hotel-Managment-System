import api from './authApi';
import type {
  HousekeepingTask,
  HousekeepingTaskCreate,
  HousekeepingTaskUpdate,
  HousekeepingStats,
} from '../types/housekeeping';

export const housekeepingApi = {
  // Tüm görevleri getir
  getAllTasks: () =>
    api.get<HousekeepingTask[]>('/housekeeping/').then((r) => r.data),

  // ID'ye göre getir
  getTaskById: (id: number) =>
    api.get<HousekeepingTask>(`/housekeeping/${id}`).then((r) => r.data),

  // Oda bazlı görevleri getir
  getTasksByRoom: (roomId: number) =>
    api.get<HousekeepingTask[]>(`/housekeeping/room/${roomId}`).then((r) => r.data),

  // Duruma göre görevleri getir
  getTasksByStatus: (status: string) =>
    api.get<HousekeepingTask[]>(`/housekeeping/status/${status}`).then((r) => r.data),

  // Personele atanmış görevleri getir
  getTasksByStaff: (staffId: number) =>
    api.get<HousekeepingTask[]>(`/housekeeping/staff/${staffId}`).then((r) => r.data),

  // Bekleyen görevleri getir
  getPendingTasks: () =>
    api.get<HousekeepingTask[]>('/housekeeping/pending').then((r) => r.data),

  // Kirli odaları getir
  getDirtyRooms: () =>
    api.get<HousekeepingTask[]>('/housekeeping/dirty-rooms').then((r) => r.data),

  // Yeni görev oluştur
  createTask: (data: HousekeepingTaskCreate) =>
    api.post<HousekeepingTask>('/housekeeping/', data).then((r) => r.data),

  // Oda için görev oluştur
  createTaskForRoom: (roomId: number, notes: string = '') =>
    api.post<HousekeepingTask>(`/housekeeping/room/${roomId}/create`, null, {
      params: { notes },
    }).then((r) => r.data),

  // Görev güncelle
  updateTask: (id: number, data: HousekeepingTaskUpdate) =>
    api.put<HousekeepingTask>(`/housekeeping/${id}`, data).then((r) => r.data),

  // Görev sil
  deleteTask: (id: number) =>
    api.delete(`/housekeeping/${id}`).then((r) => r.data),

  // Personel ata
  assignStaff: (taskId: number, staffId: number) =>
    api.post<HousekeepingTask>(`/housekeeping/${taskId}/assign`, {
      assigned_staff_id: staffId,
    }).then((r) => r.data),

  // Durum güncelle
  updateStatus: (taskId: number, status: string) =>
    api.post<HousekeepingTask>(`/housekeeping/${taskId}/status`, { status }).then((r) => r.data),

  // Temizlik tamamlandı
  completeCleaning: (taskId: number) =>
    api.post<HousekeepingTask>(`/housekeeping/${taskId}/complete`).then((r) => r.data),

  // Görevi onayla
  approveTask: (taskId: number) =>
    api.post<HousekeepingTask>(`/housekeeping/${taskId}/approve`).then((r) => r.data),

  // İstatistikleri getir
  getStats: () =>
    api.get<HousekeepingStats>('/housekeeping/stats/counts').then((r) => r.data),

  // Bekleyen görev sayısı
  getPendingCount: () =>
    api.get<{ pending_count: number }>('/housekeeping/stats/pending-count').then((r) => r.data),
};