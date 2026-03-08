export type HousekeepingStatus = 'beklemede' | 'temizleniyor' | 'temiz' | 'onayli';

export interface HousekeepingTask {
  id: number;
  room_id: number;
  assigned_staff_id?: number;
  status: HousekeepingStatus;
  notes: string;
  created_at: string;
  completed_at?: string;
}

export interface HousekeepingTaskCreate {
  room_id: number;
  notes?: string;
}

export interface HousekeepingTaskUpdate {
  assigned_staff_id?: number;
  status?: HousekeepingStatus;
  notes?: string;
}

export interface HousekeepingTaskAssign {
  assigned_staff_id: number;
}

export interface HousekeepingTaskStatusUpdate {
  status: HousekeepingStatus;
}

export interface HousekeepingTaskWithRoom extends HousekeepingTask {
  room_number?: string;
  staff_name?: string;
}

export interface HousekeepingStats {
  beklemede: number;
  temizleniyor: number;
  temiz: number;
  onayli: number;
}

