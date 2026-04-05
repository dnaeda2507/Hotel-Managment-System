export type ReservationStatus =
  | 'beklemede'
  | 'onaylandı'
  | 'giriş_yapıldı'
  | 'çıkış_yapıldı'
  | 'iptal_edildi';

export interface Reservation {
  id: number;
  room_id: number;
  guest_name: string;
  guest_email: string;
  guest_phone: string;
  guest_id_number: string;
  guest_count: number;
  special_requests: string;
  check_in_date: string;   // ISO date string "2025-06-01"
  check_out_date: string;
  actual_check_in?: string;
  actual_check_out?: string;
  price_per_night: number;
  total_nights: number;
  total_price: number;
  status: ReservationStatus;
  notes: string;
  created_at: string;
  updated_at?: string;
  capacity?: string;
  features?: string;
}

export interface ReservationCreate {
  room_id: number;
  guest_name: string;
  guest_email: string;
  guest_phone: string;
  guest_id_number: string;
  guest_count: number;
  special_requests: string;
  check_in_date: string;
  check_out_date: string;
  notes: string;
}

export interface ReservationUpdate {
  guest_name?: string;
  guest_email?: string;
  guest_phone?: string;
  guest_id_number?: string;
  guest_count?: number;
  special_requests?: string;
  check_in_date?: string;
  check_out_date?: string;
  status?: ReservationStatus;
  notes?: string;
}

export interface AvailabilityCheck {
  room_id: number;
  check_in_date: string;
  check_out_date: string;
}

export interface AvailabilityResponse {
  available: boolean;
  room_id: number;
  check_in_date: string;
  check_out_date: string;
  price_per_night: number;
  total_nights: number;
  total_price: number;
  message: string;
}

export interface ReservationStats {
  total: number;
  beklemede: number;
  'onaylandı': number;
  'giriş_yapıldı': number;
  'çıkış_yapıldı': number;
  'iptal_edildi': number;
}