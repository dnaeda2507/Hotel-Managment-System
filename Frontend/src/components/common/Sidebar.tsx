import { useNavigate, useLocation } from 'react-router-dom';

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  // Menü öğelerini bir dizi olarak tanımlayalım (yönetimi kolay olur)
  const menuItems = [
    { name: 'Genel Bakış', path: '/admin/dashboard', icon: '📊' },
    { name: 'Oda Yönetimi', path: '/admin/rooms', icon: '🏨' },
    { name: 'Fiyatlandırma', path: '/admin/pricing', icon: '💰' },
    { name: 'Fiyat Önerileri', path: '/admin/pricing-suggestions', icon: '🧾' },
    { name: 'Teknik Servis', path: '/admin/maintenance', icon: '🛠️' },
    { name: 'Temizlik (Housekeeping)', path: '/admin/housekeeping', icon: '🧹' },
    { name: 'Kayıp Eşyalar', path: '/admin/lost-found', icon: '🔍' },
    { name: 'Rezervasyonlar', path: '/admin/bookings', icon: '📅' },
    { name: 'Misafir Listesi', path: '/admin/guests', icon: '👥' },
  ];

  return (
    <aside style={{ 
      width: '260px', 
      backgroundColor: '#ffffff', 
      borderRight: '1px solid #e0e0e0', 
      display: 'flex', 
      flexDirection: 'column',
      height: '100vh',
      position: 'sticky',
      top: 0
    }}>
      {/* LOGO ALANI */}
      <div style={{ 
        padding: '30px 25px', 
        fontSize: '22px', 
        fontWeight: 'bold', 
        color: '#3b82f6', 
        borderBottom: '1px solid #e0e0e0',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        <span>🏨</span> AI HOTEL PMS
      </div>

      {/* NAVİGASYON LİNKLERİ */}
      <nav style={{ flex: 1, padding: '20px 0' }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          
          return (
            <div
              key={item.path}
              onClick={() => navigate(item.path)}
              style={{
                padding: '15px 25px',
                margin: '4px 15px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                borderRadius: '10px',
                color: isActive ? '#fff' : '#444',
                backgroundColor: isActive ? '#3b82f6' : 'transparent',
                transition: 'all 0.3s ease',
                fontWeight: isActive ? '600' : '400'
              }}
              // Hover efekti için küçük bir dokunuş
              onMouseEnter={(e) => !isActive && (e.currentTarget.style.backgroundColor = '#f0f0f0')}
              onMouseLeave={(e) => !isActive && (e.currentTarget.style.backgroundColor = 'transparent')}
            >
              <span style={{ fontSize: '18px' }}>{item.icon}</span>
              <span>{item.name}</span>
            </div>
          );
        })}
      </nav>

      {/* ALT BİLGİ / VERSİYON */}
      <div style={{ 
        padding: '20px', 
        borderTop: '1px solid #e0e0e0', 
        fontSize: '12px', 
        color: '#888', 
        textAlign: 'center' 
      }}>
        v1.0.5 - Entity Mode Active
      </div>
    </aside>
  );
}
