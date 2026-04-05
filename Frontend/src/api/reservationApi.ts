import api from './authApi';
import type {
  Reservation,
  ReservationCreate,
  ReservationUpdate,
  AvailabilityResponse,
  ReservationStats,
} from '../types/reservation';

export const reservationApi = {
  getAll: () =>
    api.get<Reservation[]>('/reservations/').then((r) => r.data),

  getById: (id: number) =>
    api.get<Reservation>(`/reservations/${id}`).then((r) => r.data),

  getByStatus: (status: string) =>
    api.get<Reservation[]>(`/reservations/status/${status}`).then((r) => r.data),

  getByRoom: (roomId: number) =>
    api.get<Reservation[]>(`/reservations/room/${roomId}`).then((r) => r.data),

  getTodayCheckins: () =>
    api.get<Reservation[]>('/reservations/today/checkins').then((r) => r.data),

  getTodayCheckouts: () =>
    api.get<Reservation[]>('/reservations/today/checkouts').then((r) => r.data),

  getStats: () =>
    api.get<ReservationStats>('/reservations/stats/counts').then((r) => r.data),

  checkAvailability: (roomId: number, checkIn: string, checkOut: string) =>
    api.get<AvailabilityResponse>('/reservations/availability', {
      params: { room_id: roomId, check_in_date: checkIn, check_out_date: checkOut },
    }).then((r) => r.data),

  create: (data: ReservationCreate) =>
    api.post<Reservation>('/reservations/', data).then((r) => r.data),

  update: (id: number, data: ReservationUpdate) =>
    api.put<Reservation>(`/reservations/${id}`, data).then((r) => r.data),

  checkIn: (id: number) =>
    api.post<Reservation>(`/reservations/${id}/check-in`).then((r) => r.data),

  checkOut: (id: number) =>
    api.post<Reservation>(`/reservations/${id}/check-out`).then((r) => r.data),

  cancel: (id: number) =>
    api.post<Reservation>(`/reservations/${id}/cancel`).then((r) => r.data),

  delete: (id: number) =>
    api.delete(`/reservations/${id}`).then((r) => r.data),
};