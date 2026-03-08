
import { useAuth } from '../../hooks/useAuth';

interface HeaderProps {
  title: string;
}

export default function Header({ title }: HeaderProps) {
  const { logout, user } = useAuth(); // FIX: Gerçek kullanıcı bilgisi

  // Avatar için email'in ilk harfi
  const avatarLetter = user?.email?.charAt(0).toUpperCase() ?? 'A';
  const roleLabel = user?.role === 'moderator' ? 'Yönetici' : 'Kullanıcı';

  return (
    <header style={{
      height: '70px',
      backgroundColor: '#ffffff',
      borderBottom: '1px solid #e0e0e0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 30px',
    }}>
      {/* Sol: Dinamik sayfa başlığı */}
      <h2 style={{ color: '#111', margin: 0, fontSize: '20px' }}>{title}</h2>

      {/* Sağ: Kullanıcı bilgisi ve çıkış */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ textAlign: 'right' }}>
          {/* FIX: Hardcode değil, gerçek email */}
          <p style={{ color: '#111', margin: 0, fontSize: '14px', fontWeight: 'bold' }}>
            {user?.email ?? '—'}
          </p>
          {/* FIX: Role'e göre dinamik etiket */}
          <p style={{ color: '#666', margin: 0, fontSize: '12px' }}>{roleLabel}</p>
        </div>

        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '50%',
          backgroundColor: '#3b82f6',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 'bold',
          fontSize: '18px',
        }}>
          {avatarLetter}
        </div>

        <button
          onClick={logout}
          style={{
            padding: '8px 15px',
            backgroundColor: 'transparent',
            border: '1px solid #ef4444',
            color: '#ef4444',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '13px',
            transition: '0.3s',
          }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#ef444422')}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          Güvenli Çıkış
        </button>
      </div>
    </header>
  );
}