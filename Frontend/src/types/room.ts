export type RoomStatus = 'Aktif' | 'Bakımda' | 'Kapalı';

export interface Room {
  id: number;
  room_number: string;
  floor: number;
  room_type: string;
  capacity: string;
  features: string;
  description: string;
  service_notes: string;
  price_per_night: number;
  is_clean: boolean;
  is_occupied: boolean;
  maintenance_status: string;
  status: RoomStatus;
}

export interface RoomCreate {
  room_number: string;
  floor: number;
  room_type: string;
  capacity: string;
  features?: string;
  description?: string;
  service_notes?: string;
  price_per_night: number;
  status?: RoomStatus;
}

export interface RoomUpdate {
  room_number?: string;
  floor?: number;
  room_type?: string;
  capacity?: string;
  features?: string;
  description?: string;
  service_notes?: string;
  price_per_night?: number;
  status?: RoomStatus;
}

export interface RoomFilters {
  floor?: number;
  room_type?: string;
  is_occupied?: boolean;
  is_clean?: boolean;
  status?: RoomStatus;
}

export interface RoomStats {
  total: number;
  occupied: number;
  available: number;
  dirty: number;
  maintenance: number;
}

