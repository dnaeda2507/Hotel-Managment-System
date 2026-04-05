import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { roomApi } from '../api/roomApi';
import type { Room } from '../types/room';

export default function RoomsPage() {
  const [filter, setFilter] = useState<string>('all');
  const [rooms, setRooms] = useState<Room[]>([]);
  const [checkIn, setCheckIn] = useState<string>('');
  const [checkOut, setCheckOut] = useState<string>('');
  const navigate = useNavigate();

  const filteredRooms = filter === 'all' 
    ? rooms 
    : rooms.filter(room => room.room_type.toLowerCase() === filter);

  useEffect(() => {
    // Eğer tarih seçilmişse tarihleri backend'e gönder
    const ci = checkIn || undefined;
    const co = checkOut || undefined;
    roomApi.getAvailableRooms(ci, co)
      .then((data) => setRooms(data))
      .catch((err) => {
        console.error('Rooms load error', err);
        setRooms([]);
      });
  }, []);

  // navigate to room detail page
  const openRoomDetail = (roomId: number) => navigate(`/rooms/${roomId}`);

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', fontFamily: "'DM Sans', sans-serif" }}>
      {/* Navigation */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px 50px', background: 'white', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '28px' }}>🏨</span>
            <span style={{ color: '#667eea', fontSize: '22px', fontWeight: 'bold' }}>AI Hotel PMS</span>
          </Link>
        </div>
        <div style={{ display: 'flex', gap: '30px' }}>
          <Link to="/" style={{ color: '#333', textDecoration: 'none' }}>Ana Sayfa</Link>
          <Link to="/rooms" style={{ color: '#667eea', textDecoration: 'none', fontWeight: '600' }}>Odalar</Link>
          <Link to="/login" style={{ color: 'white', textDecoration: 'none', padding: '10px 25px', background: '#667eea', borderRadius: '25px' }}>Giriş Yap</Link>
        </div>
      </nav>

      {/* Hero */}
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '60px 20px', textAlign: 'center', color: 'white' }}>
        <h1 style={{ fontSize: '48px', fontWeight: 'bold' }}>Odalarımız</h1>
        <p>Size uygun odayı seçin ve rezervasyon yapın</p>
      </div>

      {/* Filters */}
      <div style={{ padding: '30px', display: 'flex', gap: '10px', justifyContent: 'center' }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input type="date" value={checkIn} onChange={(e) => setCheckIn(e.target.value)} style={{ padding: 8 }} />
          <input type="date" value={checkOut} onChange={(e) => setCheckOut(e.target.value)} style={{ padding: 8 }} />
          <button onClick={() => {
            const ci = checkIn || undefined;
            const co = checkOut || undefined;
            roomApi.getAvailableRooms(ci, co).then((data) => setRooms(data)).catch(() => setRooms([]));
          }} style={{ padding: '10px 20px', borderRadius: 20, background: '#667eea', color: 'white', border: 'none' }}>Ara</button>
        </div>

        {['all', 'deluxe', 'suite', 'standart'].map((type) => (
          <button key={type} onClick={() => setFilter(type)} style={{ padding: '10px 20px', borderRadius: '20px', border: 'none', background: filter === type ? '#667eea' : '#ddd', color: filter === type ? 'white' : '#333', cursor: 'pointer' }}>
            {type === 'all' ? 'Tüm Odalar' : type.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div style={{ padding: '50px', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '30px' }}>
        {filteredRooms.map((room) => (
          <div key={room.id} style={{ background: 'white', borderRadius: '20px', overflow: 'hidden', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
            <div style={{ height: '150px', background: '#667eea', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '50px', color: 'white' }}>
              {room.room_type === 'Suite' ? '👑' : '🛌'}
            </div>
            <div style={{ padding: '20px' }}>
              <h3>Oda {room.room_number}</h3>
              <p>₺{room.price_per_night} / gece</p>
              <button 
                onClick={() => openRoomDetail(room.id)} 
                disabled={room.is_occupied}
                style={{ width: '100%', padding: '10px', background: room.is_occupied ? '#ccc' : '#667eea', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer' }}
              >
                {room.is_occupied ? 'Dolu' : 'Detay gör'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Room detail handled on a separate page */}

      <footer style={{ background: '#111', color: 'white', padding: '30px', textAlign: 'center', marginTop: '40px' }}>
        <p>© 2025 AI Hotel PMS. Tüm hakları saklıdır.</p>
      </footer>
    </div>
  );
}