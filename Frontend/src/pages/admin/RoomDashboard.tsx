import { useEffect, useState } from 'react';
import { roomApi } from '../../api/roomApi';
import type { Room } from '../../types/room';

const ROOM_TYPES = ['Standard', 'Deluxe', 'Suite'];
const CAPACITIES = ['1 kişilik', '2 kişilik', '2+1 kişilik', '3 kişilik', '3+1 kişilik', '4 kişilik'];

export default function RoomDashboard() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [showForm, setShowForm] = useState(false);

  // FIX: price_per_night kaldırıldı (backend otomatik belirliyor)
  // FIX: capacity eklendi (backend fiyat için gerekli)
  const [newRoom, setNewRoom] = useState({
    room_number: '',
    floor: 1,
    room_type: 'Standard',
    capacity: '2 kişilik',
  });

  const fetchRooms = () => {
    roomApi.getRooms()
      .then(data => setRooms(data))
      .catch(err => console.error('Odalar çekilemedi:', err));
  };

  useEffect(() => {
    fetchRooms();
  }, []);

  const handleToggleClean = async (roomId: number, currentStatus: boolean) => {
    try {
      await roomApi.updateRoom(roomId, { is_clean: !currentStatus });
      setRooms(prev => prev.map(room =>
        room.id === roomId ? { ...room, is_clean: !currentStatus } : room
      ));
    } catch (err) {
      console.error('Güncelleme hatası:', err);
      alert('Durum güncellenemedi.');
    }
  };

  const handleAddRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await roomApi.createRoom(newRoom);
      setShowForm(false);
      setNewRoom({ room_number: '', floor: 1, room_type: 'Standard', capacity: '2 kişilik' });
      fetchRooms();
    } catch (err) {
      console.error('Ekleme hatası:', err);
      alert('Oda eklenemedi! Oda numarası zaten kullanımda olabilir veya seçilen tip/kapasite için fiyat tanımlanmamış.');
    }
  };

  return (
    <div style={{ padding: '30px', color: '#111', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>

      {/* Üst başlık */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <div>
          <h1 style={{ margin: 0 }}>🏨 Oda Yönetim Paneli</h1>
          <p style={{ color: '#666' }}>Odaları görüntüle, ekle ve durumlarını güncelle.</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            padding: '10px 20px',
            backgroundColor: showForm ? '#444' : '#3b82f6',
            color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold',
          }}
        >
          {showForm ? 'İptal' : '+ Yeni Oda Ekle'}
        </button>
      </div>

      {/* Yeni oda formu */}
      {showForm && (
        <div style={{ background: '#ffffff', padding: '25px', borderRadius: '15px', marginBottom: '30px', border: '1px solid #e0e0e0' }}>
          <h3 style={{ marginTop: 0, color: '#111' }}>Yeni Oda Tanımla</h3>
          <form onSubmit={handleAddRoom} style={{ display: 'flex', gap: '20px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: '#333' }}>Oda Numarası</label>
              <input
                type="text"
                placeholder="Örn: 101"
                value={newRoom.room_number}
                onChange={e => setNewRoom({ ...newRoom, room_number: e.target.value })}
                required
                style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc', background: '#fff', color: '#111' }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: '#333' }}>Kat</label>
              <input
                type="number"
                min={1}
                value={newRoom.floor}
                onChange={e => setNewRoom({ ...newRoom, floor: Number(e.target.value) })}
                style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc', background: '#fff', color: '#111', width: '80px' }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: '#333' }}>Oda Tipi</label>
              <select
                value={newRoom.room_type}
                onChange={e => setNewRoom({ ...newRoom, room_type: e.target.value })}
                style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc', background: '#fff', color: '#111' }}
              >
                {ROOM_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            {/* FIX: Kapasite alanı eklendi */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ color: '#333' }}>Kapasite</label>
              <select
                value={newRoom.capacity}
                onChange={e => setNewRoom({ ...newRoom, capacity: e.target.value })}
                style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc', background: '#fff', color: '#111' }}
              >
                {CAPACITIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            {/* FIX: Fiyat alanı kaldırıldı — backend PricingService'den otomatik belirliyor */}
            <button
              type="submit"
              style={{ padding: '12px 25px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              Odayı Kaydet
            </button>
          </form>
        </div>
      )}

      {/* Oda listesi */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '25px' }}>
        {rooms.map(room => (
          <div key={room.id} style={{ background: '#ffffff', padding: '20px', borderRadius: '15px', border: '1px solid #e0e0e0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px' }}>
              <h3 style={{ margin: 0, fontSize: '22px', color: '#111' }}>Oda {room.room_number}</h3>
              <span style={{
                padding: '4px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold',
                backgroundColor: room.is_occupied ? '#fee2e2' : '#d1fae5',
                color: room.is_occupied ? '#dc2626' : '#059669',
              }}>
                {room.is_occupied ? 'DOLU' : 'BOŞ'}
              </span>
            </div>

            <p style={{ margin: '5px 0', color: '#666' }}>Tip: <span style={{ color: '#111' }}>{room.room_type}</span></p>
            <p style={{ margin: '5px 0', color: '#666' }}>Kapasite: <span style={{ color: '#111' }}>{room.capacity}</span></p>
            <p style={{ margin: '5px 0', color: '#666' }}>Kat: <span style={{ color: '#111' }}>{room.floor}</span></p>
            <p style={{ margin: '5px 0', color: '#666' }}>Fiyat: <span style={{ color: '#111' }}>{room.price_per_night} ₺</span></p>
            <p style={{ margin: '15px 0', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
              Temizlik:
              <span style={{ color: room.is_clean ? '#059669' : '#dc2626' }}>
                {room.is_clean ? '✅ Temiz' : '🧹 Kirli'}
              </span>
            </p>

            <button
              onClick={() => handleToggleClean(room.id, room.is_clean)}
              style={{
                width: '100%', padding: '10px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontWeight: 'bold',
                backgroundColor: room.is_clean ? '#6b7280' : '#059669',
                color: 'white',
              }}
            >
              {room.is_clean ? 'Kirli Olarak İşaretle' : 'Temizlendi Olarak İşaretle'}
            </button>
          </div>
        ))}
      </div>

      {rooms.length === 0 && (
        <div style={{ textAlign: 'center', marginTop: '50px', color: '#888' }}>
          Henüz hiç oda eklenmemiş. "Yeni Oda Ekle" butonu ile başlayın.
        </div>
      )}
    </div>
  );
}