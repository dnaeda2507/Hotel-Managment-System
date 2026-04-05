import api from './authApi';
import type { Review, ReviewCreate } from '../types/review';

export const reviewApi = {
  getReviews: (roomId: number) => api.get<Review[]>(`/rooms/${roomId}/reviews`).then((r) => r.data),
  createReview: (roomId: number, data: ReviewCreate) => api.post<Review>(`/rooms/${roomId}/reviews`, data).then((r) => r.data),
};

export default reviewApi;
