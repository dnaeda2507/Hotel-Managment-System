import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: "'DM Sans', sans-serif"
    }}>
      {/* Navigation */}
      <nav style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        padding: '20px 50px',
        background: 'rgba(255,255,255,0.1)',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '28px' }}>🏨</span>
          <span style={{ color: 'white', fontSize: '22px', fontWeight: 'bold' }}>AI Hotel PMS</span>
        </div>
        <div style={{ display: 'flex', gap: '30px' }}>
          <Link to="/rooms" style={{ color: 'white', textDecoration: 'none', fontSize: '16px' }}>Odalar</Link>
          <Link to="/about" style={{ color: 'white', textDecoration: 'none', fontSize: '16px' }}>Hakkımızda</Link>
          <Link 
            to="/login" 
            style={{ 
              color: 'white', 
              textDecoration: 'none', 
              fontSize: '16px',
              padding: '10px 25px',
              background: 'rgba(255,255,255,0.2)',
              borderRadius: '25px',
              transition: 'all 0.3s'
            }}
          >
            Giriş Yap
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div style={{ 
        textAlign: 'center', 
        padding: '120px 20px',
        color: 'white'
      }}>
        <h1 style={{ 
          fontSize: '64px', 
          fontWeight: 'bold',
          marginBottom: '20px',
          fontFamily: "'Bricolage Grotesque', sans-serif"
        }}>
          Konforun Yeni Adresi
        </h1>
        <p style={{ 
          fontSize: '22px', 
          opacity: 0.9, 
          marginBottom: '40px',
          maxWidth: '600px',
          margin: '0 auto 40px'
        }}>
          Modern teknoloji ve eşsiz konaklama deneyimini bir arada yaşayın. 
          Yapay zeka destekli otel yönetim sistemimizle hizmetinizdeyiz.
        </p>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
          <Link 
            to="/rooms" 
            style={{ 
              padding: '15px 40px',
              background: 'white',
              color: '#667eea',
              textDecoration: 'none',
              borderRadius: '30px',
              fontSize: '18px',
              fontWeight: '600',
              transition: 'transform 0.3s',
              boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
            }}
          >
            Odaları Keşfet
          </Link>
          <Link 
            to="/login" 
            style={{ 
              padding: '15px 40px',
              background: 'rgba(255,255,255,0.2)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '30px',
              fontSize: '18px',
              fontWeight: '600',
              border: '2px solid white'
            }}
          >
            Admin Girişi
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div style={{ 
        background: 'white',
        padding: '80px 50px',
        borderRadius: '50px 50px 0 0'
      }}>
        <h2 style={{ 
          textAlign: 'center', 
          fontSize: '42px', 
          color: '#111',
          marginBottom: '60px',
          fontFamily: "'Bricolage Grotesque', sans-serif"
        }}>
          Neden Bizi Tercih Edin?
        </h2>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '40px',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {/* Feature 1 */}
          <div style={{ 
            padding: '40px', 
            borderRadius: '20px',
            background: '#f8f9fa',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '50px', marginBottom: '20px' }}>🛏️</div>
            <h3 style={{ fontSize: '24px', color: '#111', marginBottom: '15px' }}>Konforlu Odalar</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              Modern tasarımlı, tam donanımlı odalarımızda konaklamanın keyfini çıkarın.
            </p>
          </div>

          {/* Feature 2 */}
          <div style={{ 
            padding: '40px', 
            borderRadius: '20px',
            background: '#f8f9fa',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '50px', marginBottom: '20px' }}>🍽️</div>
            <h3 style={{ fontSize: '24px', color: '#111', marginBottom: '15px' }}>Oda Servisi</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              7/24 oda servisi ile istediğiniz zaman lezzetli yemeklerin keyfini çıkarın.
            </p>
          </div>

          {/* Feature 3 */}
          <div style={{ 
            padding: '40px', 
            borderRadius: '20px',
            background: '#f8f9fa',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '50px', marginBottom: '20px' }}>🤖</div>
            <h3 style={{ fontSize: '24px', color: '#111', marginBottom: '15px' }}>AI Asistan</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              Yapay zeka destekli concierge hizmetimizle tüm istekleriniz anında karşılanır.
            </p>
          </div>

          {/* Feature 4 */}
          <div style={{ 
            padding: '40px', 
            borderRadius: '20px',
            background: '#f8f9fa',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '50px', marginBottom: '20px' }}>📍</div>
            <h3 style={{ fontSize: '24px', color: '#111', marginBottom: '15px' }}>Merkezi Konum</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              Şehrin en işlek noktasında, tüm ulaşım araçlarına yakın.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer style={{ 
        background: '#111', 
        color: 'white', 
        padding: '40px 50px',
        textAlign: 'center'
      }}>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '40px', marginBottom: '20px' }}>
          <Link to="/rooms" style={{ color: '#888', textDecoration: 'none' }}>Odalar</Link>
          <Link to="/about" style={{ color: '#888', textDecoration: 'none' }}>Hakkımızda</Link>
          <Link to="/login" style={{ color: '#888', textDecoration: 'none' }}>Admin</Link>
        </div>
        <p style={{ color: '#666' }}>© 2025 AI Hotel PMS. Tüm hakları saklıdır.</p>
      </footer>
    </div>
  );
}

