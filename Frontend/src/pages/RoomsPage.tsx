import { useState } from 'react';
import { Link } from 'react-router-dom';

interface Room {
  id: number;
  name: string;
  type: string;
  price: number;
  capacity: number;
  image: string;
  amenities: string[];
  available: boolean;
}

const mockRooms: Room[] = [
  {
    id: 1,
    name: 'Deluxe Oda',
    type: 'Deluxe',
    price: 2500,
    capacity: 2,
    image: '🛏️',
    amenities: ['WiFi', 'Mini Bar', 'Klima', 'TV', 'Sauna'],
    available: true
  },
  {
    id: 2,
    name: 'Suite Oda',
    type: 'Suite',
    price: 4500,
    capacity: 4,
    image: '🛋️',
    amenities: ['WiFi', 'Mini Bar', 'Klima', 'TV', 'Jakuzi', 'Salon'],
    available: true
  },
  {
    id: 3,
    name: 'Standart Oda',
    type: 'Standart',
    price: 1500,
    capacity: 2,
    image: '🛏️',
    amenities: ['WiFi', 'Klima', 'TV'],
    available: true
  },
  {
    id: 4,
    name: 'Aile Odası',
    type: 'Family',
    price: 3500,
    capacity: 6,
    image: '👨‍👩‍👧‍👦',
    amenities: ['WiFi', 'Mini Bar', 'Klima', 'TV', 'Mutfak'],
    available: false
  },
  {
    id: 5,
    name: 'Executive Suite',
    type: 'Suite',
    price: 6000,
    capacity: 2,
    image: '💼',
    amenities: ['WiFi', 'Mini Bar', 'Klima', 'TV', 'Jakuzi', 'Ofis', 'Bar'],
    available: true
  },
  {
    id: 6,
    name: 'Ekonomi Oda',
    type: 'Economy',
    price: 1000,
    capacity: 1,
    image: '🏠',
    amenities: ['WiFi', 'TV'],
    available: true
  }
];

export default function RoomsPage() {
  const [filter, setFilter] = useState<string>('all');
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);

  const filteredRooms = filter === 'all' 
    ? mockRooms 
    : mockRooms.filter(room => room.type.toLowerCase() === filter);

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: '#f5f5f5',
      fontFamily: "'DM Sans', sans-serif"
    }}>
      {/* Navigation */}
      <nav style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        padding: '20px 50px',
        background: 'white',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '28px' }}>🏨</span>
            <span style={{ color: '#667eea', fontSize: '22px', fontWeight: 'bold' }}>AI Hotel PMS</span>
          </Link>
        </div>
        <div style={{ display: 'flex', gap: '30px' }}>
          <Link to="/" style={{ color: '#333', textDecoration: 'none', fontSize: '16px' }}>Ana Sayfa</Link>
          <Link to="/rooms" style={{ color: '#667eea', textDecoration: 'none', fontSize: '16px', fontWeight: '600' }}>Odalar</Link>
          <Link to="/about" style={{ color: '#333', textDecoration: 'none', fontSize: '16px' }}>Hakkımızda</Link>
          <Link 
            to="/login" 
            style={{ 
              color: 'white', 
              textDecoration: 'none', 
              fontSize: '16px',
              padding: '10px 25px',
              background: '#667eea',
              borderRadius: '25px'
            }}
          >
            Giriş Yap
          </Link>
        </div>
      </nav>

      {/* Hero Banner */}
      <div style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '60px 20px',
        textAlign: 'center',
        color: 'white'
      }}>
        <h1 style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '15px' }}>
          Odalarımız
        </h1>
        <p style={{ fontSize: '18px', opacity: 0.9 }}>
          Size uygun odayı seçin ve rezervasyon yapın
        </p>
      </div>

      {/* Filters */}
      <div style={{ 
        padding: '30px 50px',
        background: 'white',
        display: 'flex',
        gap: '15px',
        justifyContent: 'center',
        flexWrap: 'wrap'
      }}>
        {['all', 'deluxe', 'suite', 'standart', 'family', 'economy'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            style={{
              padding: '12px 25px',
              border: 'none',
              borderRadius: '25px',
              background: filter === type ? '#667eea' : '#f0f0f0',
              color: filter === type ? 'white' : '#333',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'all 0.3s'
            }}
          >
            {type === 'all' ? 'Tüm Odalar' : type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      {/* Room Grid */}
      <div style={{ 
        padding: '50px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
        gap: '30px',
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        {filteredRooms.map((room) => (
          <div
            key={room.id}
            style={{
              background: 'white',
              borderRadius: '20px',
              overflow: 'hidden',
              boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
              transition: 'transform 0.3s',
            }}
          >
            {/* Room Image Area */}
            <div style={{ 
              height: '200px', 
              background: room.available 
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : 'linear-gradient(135deg, #666 0%, #444 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '80px',
              position: 'relative'
            }}>
              {room.image}
              {!room.available && (
                <div style={{
                  position: 'absolute',
                  top: '15px',
                  right: '15px',
                  background: '#dc3545',
                  color: 'white',
                  padding: '5px 15px',
                  borderRadius: '20px',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  DOLU
                </div>
              )}
            </div>

            {/* Room Info */}
            <div style={{ padding: '25px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3 style={{ fontSize: '22px', color: '#111', fontWeight: '600' }}>{room.name}</h3>
                <span style={{ 
                  background: '#e8f5e9', 
                  color: '#2e7d32', 
                  padding: '5px 12px', 
                  borderRadius: '15px',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {room.type}
                </span>
              </div>

              <p style={{ color: '#666', marginBottom: '15px' }}>
                Kapasite: {room.capacity} kişi
              </p>

              {/* Amenities */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px' }}>
                {room.amenities.map((amenity, idx) => (
                  <span key={idx} style={{ 
                    background: '#f5f5f5', 
                    color: '#666',
                    padding: '5px 10px', 
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}>
                    {amenity}
                  </span>
                ))}
              </div>

              {/* Price & Action */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span style={{ fontSize: '28px', fontWeight: 'bold', color: '#667eea' }}>
                    ₺{room.price}
                  </span>
                  <span style={{ color: '#666', fontSize: '14px' }}> / gece</span>
                </div>
                <button
                  onClick={() => setSelectedRoom(room)}
                  disabled={!room.available}
                  style={{
                    padding: '12px 25px',
                    background: room.available ? '#667eea' : '#ccc',
                    color: 'white',
                    border: 'none',
                    borderRadius: '10px',
                    cursor: room.available ? 'pointer' : 'not-allowed',
                    fontSize: '14px',
                    fontWeight: '600',
                    transition: 'all 0.3s'
                  }}
                >
                  {room.available ? 'Rezervasyon Yap' : 'Müsait Değil'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Room Detail Modal */}
      {selectedRoom && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            borderRadius: '20px',
            padding: '40px',
            maxWidth: '500px',
            width: '90%'
          }}>
            <h2 style={{ fontSize: '28px', marginBottom: '20px' }}>{selectedRoom.name}</h2>
            <p style={{ color: '#666', marginBottom: '15px' }}>Tip: {selectedRoom.type}</p>
            <p style={{ color: '#666', marginBottom: '15px' }}>Kapasite: {selectedRoom.capacity} kişi</p>
            <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#667eea', marginBottom: '20px' }}>
              ₺{selectedRoom.price} <span style={{ fontSize: '16px', color: '#666' }}>/ gece</span>
            </p>
            
            <div style={{ display: 'flex', gap: '15px' }}>
              <button
                onClick={() => setSelectedRoom(null)}
                style={{
                  flex: 1,
                  padding: '15px',
                  background: '#f0f0f0',
                  color: '#333',
                  border: 'none',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                Kapat
              </button>
              <button
                style={{
                  flex: 1,
                  padding: '15px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: '600'
                }}
              >
                Rezervasyon Yap
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer style={{ 
        background: '#111', 
        color: 'white', 
        padding: '40px 50px',
        textAlign: 'center',
        marginTop: '50px'
      }}>
        <p style={{ color: '#666' }}>© 2025 AI Hotel PMS. Tüm hakları saklıdır.</p>
      </footer>
    </div>
  );
}

