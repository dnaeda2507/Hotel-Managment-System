export interface Issue {
  room_id: number;
  type: string;
  desc: string;
  date?: string;
}

export interface Task {
  task_type: string;
  room_id: number;
  desc: string;
  date: string;
  task_id?: number;
}

export interface ReportResponse {
  report: string;
  detected_issues: Issue[];
}
