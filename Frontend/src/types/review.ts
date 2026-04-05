export interface Review {
  id: number;
  room_id: number;
  user_id?: number | null;
  rating?: number | null;
  text: string;
  created_at: string;
}

export interface ReviewCreate {
  text: string;
  rating?: number | null;
}
