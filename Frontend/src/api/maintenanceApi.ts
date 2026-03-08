import api from './authApi';
import type {
  MaintenanceTicket,
  MaintenanceTicketCreate,
  MaintenanceTicketUpdate,
} from '../types/maintenance';

export const maintenanceApi = {
  // Tüm ticketları getir
  getAllTickets: () =>
    api.get<MaintenanceTicket[]>('/maintenance/').then((r) => r.data),

  // Açık ticketları getir
  getOpenTickets: () =>
    api.get<MaintenanceTicket[]>('/maintenance/open').then((r) => r.data),

  // ID'ye göre getir
  getTicketById: (id: number) =>
    api.get<MaintenanceTicket>(`/maintenance/${id}`).then((r) => r.data),

  // Oda bazlı ticketları getir
  getTicketsByRoom: (roomId: number) =>
    api.get<MaintenanceTicket[]>(`/maintenance/room/${roomId}`).then((r) => r.data),

  // Duruma göre ticketları getir
  getTicketsByStatus: (status: string) =>
    api.get<MaintenanceTicket[]>(`/maintenance/status/${status}`).then((r) => r.data),

  // Önceliğe göre ticketları getir
  getTicketsByPriority: (priority: string) =>
    api.get<MaintenanceTicket[]>(`/maintenance/priority/${priority}`).then((r) => r.data),

  // Teknisyene atanmış ticketları getir
  getTicketsByTechnician: (technicianId: number) =>
    api.get<MaintenanceTicket[]>(`/maintenance/technician/${technicianId}`).then((r) => r.data),

  // Yeni ticket oluştur
  createTicket: (data: MaintenanceTicketCreate) =>
    api.post<MaintenanceTicket>('/maintenance/', data).then((r) => r.data),

  // Ticket güncelle
  updateTicket: (id: number, data: MaintenanceTicketUpdate) =>
    api.put<MaintenanceTicket>(`/maintenance/${id}`, data).then((r) => r.data),

  // Ticket sil
  deleteTicket: (id: number) =>
    api.delete(`/maintenance/${id}`).then((r) => r.data),

  // Teknisyen ata
  assignTechnician: (ticketId: number, technicianId: number) =>
    api.post<MaintenanceTicket>(`/maintenance/${ticketId}/assign`, {
      assigned_technician_id: technicianId,
    }).then((r) => r.data),

  // FIX: Ticket kapat — backend: POST /{id}/close
  closeTicket: (ticketId: number) =>
    api.post<MaintenanceTicket>(`/maintenance/${ticketId}/close`).then((r) => r.data),

  // İstatistikleri getir — backend: GET /stats/counts
  getStats: () =>
    api.get<{ by_status: Record<string, number>; by_priority: Record<string, number> }>(
      '/maintenance/stats/counts'
    ).then((r) => r.data),
};