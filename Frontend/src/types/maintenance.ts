export type Priority = string;
export type MaintenanceStatus = string;

export interface MaintenanceTicket {
  id: number;
  room_id: number;
  title: string;
  description: string;
  priority: Priority;
  status: MaintenanceStatus;
  assigned_technician_id: number | null;
  created_at: string;
  resolved_at: string | null;
}

export interface MaintenanceTicketCreate {
  room_id: number;
  title: string;
  description: string;
  priority: Priority;
}

export interface MaintenanceTicketUpdate {
  title?: string;
  description?: string;
  priority?: Priority;
  status?: MaintenanceStatus;
  assigned_technician_id?: number;
}

export interface MaintenanceTicketWithRoom extends MaintenanceTicket {
  room_number?: string;
}

export interface MaintenanceStats {
  total: number;
  open: number;
  in_progress: number;
  closed: number;
  critical: number;
}
