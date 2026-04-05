import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { roomApi } from '../api/roomApi';
import { reviewApi } from '../api/reviewApi';
import { reservationApi } from '../api/reservationApi';
import type { Room } from '../types/room';
import type { Review } from '../types/review';
import type { ReservationCreate } from '../types/reservation';

export default function RoomDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [room, setRoom] = useState<Room | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [newReviewText, setNewReviewText] = useState('');
  const [newReviewRating, setNewReviewRating] = useState<number | null>(null);

  const [resForm, setResForm] = useState<ReservationCreate>({
    room_id: Number(id || 0),
    guest_name: '',
    guest_email: user?.email || '',
    guest_phone: '',
    guest_id_number: '',
    guest_count: 1,
    special_requests: '',
    check_in_date: '',
    check_out_date: '',
    notes: '',
  });

  const [availability, setAvailability] = useState<{ available: boolean; message?: string; total_price?: number } | null>(null);
  const [totalPrice, setTotalPrice] = useState<number | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [reservationConfirmed, setReservationConfirmed] = useState<number | null>(null);

  useEffect(() => {
    if (!id) return;
    roomApi.getRoom(Number(id))
      .then(setRoom)
      .catch(() => setRoom(null));
    reviewApi.getReviews(Number(id)).then(setReviews).catch(() => setReviews([]));
  }, [id]);

  useEffect(() => {
    setResForm((f) => ({ ...f, room_id: Number(id || 0), guest_name: f.guest_name, guest_email: user?.email || f.guest_email }));
  }, [id, user]);

  // When dates change, check availability and compute total
  useEffect(() => {
    const { check_in_date: ci, check_out_date: co } = resForm;
    if (!room || !ci || !co) {
      setAvailability(null);
      setTotalPrice(null);
      return;
    }

    // compute nights
    const d1 = new Date(ci);
    const d2 = new Date(co);
    const diffMs = d2.getTime() - d1.getTime();
    const nights = Math.max(0, Math.ceil(diffMs / (1000 * 60 * 60 * 24)));

    // compute local total price
    const localTotal = nights * (room.price_per_night || 0);
    setTotalPrice(localTotal || null);

    // call API to confirm availability and get server-side pricing
    reservationApi.checkAvailability(room.id, ci, co)
      .then((res) => {
        setAvailability({ available: res.available, message: res.message, total_price: res.total_price });
        if (res.total_price) setTotalPrice(res.total_price);
      })
      .catch(() => {
        setAvailability({ available: false, message: 'Uygunluk kontrolü yapılamadı' });
      });
  }, [resForm.check_in_date, resForm.check_out_date, room]);

  const handleReviewSubmit = async () => {
    if (!room || !newReviewText.trim()) return;
    const token = localStorage.getItem('token');
    if (!token) return navigate('/login', { state: { from: location.pathname } });
    try {
      await reviewApi.createReview(room.id, { text: newReviewText, rating: newReviewRating });
      const updated = await reviewApi.getReviews(room.id);
      setReviews(updated);
      setNewReviewText('');
      setNewReviewRating(null);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err.message || JSON.stringify(err);
      alert(`Yorum gönderilemedi: ${msg}`);
      console.error('Review POST error', err);
    }
  };

  const handleReserve = async () => {
    if (!room) return;
    const token = localStorage.getItem('token');
    if (!token) return navigate('/login', { state: { from: location.pathname } });
    try {
      const payload: ReservationCreate = { ...resForm, room_id: room.id };
      const created = await reservationApi.create(payload);
      setReservationConfirmed(created.id);
      alert(`Rezervasyon başarılı. Rezervasyon ID: ${created.id}`);
    } catch (err) {
      alert('Rezervasyon yapılamadı. Lütfen bilgilerinizi kontrol edin.');
    }
  };

  if (!room) return <div style={{ padding: 40 }}>Oda bulunamadı veya yükleniyor...</div>;

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', padding: 20 }}>
      <div style={{ maxWidth: 1000, margin: '20px auto', background: 'white', borderRadius: 12, padding: 24 }}>
        <h1>Oda {room.room_number} — {room.room_type}</h1>
        <p>Kapasite: {room.capacity} kişi</p>
        <h3 style={{ color: '#667eea' }}>₺{room.price_per_night} / gece</h3>

        <div style={{ display: 'flex', gap: 20, marginTop: 20 }}>
          <div style={{ flex: 1 }}>
            <div style={{ height: 220, background: '#ddd', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {Array.isArray((room as any).images) && (room as any).images.length > 0 ? (
                <div style={{ width: '100%', position: 'relative' }}>
                  <img src={(room as any).images[currentImageIndex]} alt={`room-${room.id}`} style={{ width: '100%', height: 220, objectFit: 'cover', borderRadius: 8 }} />
                  <button onClick={() => setCurrentImageIndex((i) => Math.max(0, i - 1))} style={{ position: 'absolute', left: 8, top: '50%', transform: 'translateY(-50%)' }}>{'‹'}</button>
                  <button onClick={() => setCurrentImageIndex((i) => Math.min(((room as any).images.length - 1), i + 1))} style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)' }}>{'›'}</button>
                </div>
              ) : (
                <span style={{ fontSize: 72 }}>{room.room_type === 'Suite' ? '👑' : '🛌'}</span>
              )}
            </div>

            <div style={{ marginTop: 16 }}>
              <h4>Açıklama</h4>
              <p>{room.description || 'Açıklama bulunamadı.'}</p>
              <h4>Özellikler</h4>
              <ul>
                {Array.isArray((room as any).features)
                  ? (room as any).features.map((f: string) => <li key={f}>{f}</li>)
                  : (room.features || '').toString().split(',').map((s) => s.trim()).filter(Boolean).map((f) => <li key={f}>{f}</li>)}
              </ul>
            </div>
          </div>

          <div style={{ width: 360 }}>
            <div style={{ background: '#fafafa', padding: 16, borderRadius: 8 }}>
              <h4>Rezervasyon Yap</h4>

              <label style={{ display: 'block', marginTop: 8 }}>Giriş</label>
              <input type="date" value={resForm.check_in_date} onChange={(e) => setResForm({ ...resForm, check_in_date: e.target.value })} style={{ width: '100%', padding: 8 }} />

              <label style={{ display: 'block', marginTop: 8 }}>Çıkış</label>
              <input type="date" value={resForm.check_out_date} onChange={(e) => setResForm({ ...resForm, check_out_date: e.target.value })} style={{ width: '100%', padding: 8 }} />

              <label style={{ display: 'block', marginTop: 8 }}>İsim</label>
              <input value={resForm.guest_name} onChange={(e) => setResForm({ ...resForm, guest_name: e.target.value })} style={{ width: '100%', padding: 8 }} />

              <label style={{ display: 'block', marginTop: 8 }}>E-posta</label>
              <input value={resForm.guest_email} onChange={(e) => setResForm({ ...resForm, guest_email: e.target.value })} style={{ width: '100%', padding: 8 }} />

              <label style={{ display: 'block', marginTop: 8 }}>Telefon</label>
              <input value={resForm.guest_phone} onChange={(e) => setResForm({ ...resForm, guest_phone: e.target.value })} style={{ width: '100%', padding: 8 }} />

              <label style={{ display: 'block', marginTop: 8 }}>Kişi Sayısı</label>
              <input type="number" min={1} value={resForm.guest_count} onChange={(e) => setResForm({ ...resForm, guest_count: Number(e.target.value) })} style={{ width: '100%', padding: 8 }} />

              <div style={{ marginTop: 12 }}>
                {totalPrice !== null && <div style={{ marginBottom: 8, fontWeight: '600' }}>Toplam: ₺{totalPrice}</div>}
                {availability && availability.message && <div style={{ marginBottom: 8, color: availability.available ? 'green' : 'red' }}>{availability.message}</div>}
                <button onClick={handleReserve} disabled={availability ? !availability.available : false} style={{ width: '100%', padding: 10, background: availability && !availability.available ? '#ccc' : '#667eea', color: 'white', border: 'none', borderRadius: 8 }}>Rezervasyon Yap</button>
              </div>
            </div>

            <div style={{ marginTop: 18, background: '#fff', padding: 12, borderRadius: 8 }}>
              <h4>Misafir Yorumları</h4>
              <div style={{ maxHeight: 180, overflowY: 'auto' }}>
                {reviews.length === 0 ? <p>Henüz yorum yok.</p> : reviews.map((r) => (
                  <div key={r.id} style={{ padding: 8, borderBottom: '1px solid #f0f0f0' }}>
                    <strong>{r.rating} ⭐</strong>
                    <div style={{ marginTop: 6 }}>{r.text}</div>
                  </div>
                ))}
              </div>

              <textarea value={newReviewText} onChange={(e) => setNewReviewText(e.target.value)} placeholder="Yorumunuz..." style={{ width: '100%', minHeight: 80, marginTop: 8 }} />
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                <select value={newReviewRating ?? ''} onChange={(e) => setNewReviewRating(e.target.value ? Number(e.target.value) : null)}>
                  <option value="">Puan</option>
                  {[5,4,3,2,1].map((n) => <option key={n} value={n}>{n} ⭐</option>)}
                </select>
                <button onClick={handleReviewSubmit} style={{ flex: 1, background: '#3b82f6', color: 'white', border: 'none', borderRadius: 6 }}>Yorum Gönder</button>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
