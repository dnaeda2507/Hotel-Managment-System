import { Link } from "react-router-dom";

export default function AboutPage() {
  return (
    <div style={{ minHeight: "100vh", background: "#f5f5f5", fontFamily: "Arial, sans-serif" }}>
      {/* Navigasyon */}
      <nav style={{ display: "flex", justifyContent: "space-between", padding: "20px 50px", background: "white", alignItems: "center", boxShadow: "0 2px 5px rgba(0,0,0,0.1)" }}>
        <Link to="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "28px" }}>🏨</span>
          <span style={{ color: "#667eea", fontSize: "22px", fontWeight: "bold" }}>AI Hotel PMS</span>
        </Link>
        <div style={{ display: "flex", gap: "30px", alignItems: "center" }}>
          <Link to="/" style={{ color: "#333", textDecoration: "none" }}>Ana Sayfa</Link>
          <Link to="/rooms" style={{ color: "#333", textDecoration: "none" }}>Odalar</Link>
          <Link to="/about" style={{ color: "#667eea", textDecoration: "none", fontWeight: "600" }}>Hakkımızda</Link>
          <Link to="/login" style={{ color: "white", textDecoration: "none", padding: "10px 25px", background: "#667eea", borderRadius: "25px" }}>Giriş Yap</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", padding: "80px 20px", textAlign: "center", color: "white" }}>
        <h1 style={{ fontSize: "48px", fontWeight: "bold", margin: 0 }}>Hakkımızda</h1>
        <p style={{ fontSize: "18px", opacity: 0.9, marginTop: "10px" }}>Modern teknoloji ve misafirperverlik</p>
      </div>

      {/* Hikayemiz */}
      <div style={{ padding: "80px 50px", maxWidth: "1000px", margin: "0 auto" }}>
        <h2 style={{ fontSize: "36px", textAlign: "center", marginBottom: "30px" }}>Hikayemiz</h2>
        <div style={{ background: "white", padding: "40px", borderRadius: "20px", boxShadow: "0 10px 30px rgba(0,0,0,0.05)" }}>
          <p style={{ color: "#666", lineHeight: "1.8", marginBottom: "20px" }}>AI Hotel PMS, 2025 yılında konaklama sektöründe devrim yaratmak vizyonuyla kuruldu.</p>
          <p style={{ color: "#666", lineHeight: "1.8" }}>Misyonumuz, otel işletmelerinin verimliliğini artırmak ve misafirlerimize unutulmaz bir deneyim sunmaktır.</p>
        </div>
      </div>

      {/* Misyon & Vizyon Kartları */}
      <div style={{ padding: "0 50px 80px", maxWidth: "1000px", margin: "0 auto" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "30px" }}>
          <div style={{ background: "white", padding: "40px", borderRadius: "20px", textAlign: "center" }}>
            <div style={{ fontSize: "60px" }}>🎯</div>
            <h3 style={{ fontSize: "24px", marginBottom: "15px" }}>Misyonumuz</h3>
            <p style={{ color: "#666" }}>Otel yönetim süreçlerini dijitalleştirmek</p>
          </div>
          <div style={{ background: "white", padding: "40px", borderRadius: "20px", textAlign: "center" }}>
            <div style={{ fontSize: "60px" }}>👁️</div>
            <h3 style={{ fontSize: "24px", marginBottom: "15px" }}>Vizyonumuz</h3>
            <p style={{ color: "#666" }}>Dünya çapında lider olmak</p>
          </div>
          <div style={{ background: "white", padding: "40px", borderRadius: "20px", textAlign: "center" }}>
            <div style={{ fontSize: "60px" }}>💎</div>
            <h3 style={{ fontSize: "24px", marginBottom: "15px" }}>Değerlerimiz</h3>
            <p style={{ color: "#666" }}>Mükemmeliyet ve müşteri memnuniyeti</p>
          </div>
        </div>
      </div>

      {/* İstatistikler */}
      <div style={{ background: "#111", padding: "60px 50px", color: "white" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "40px", maxWidth: "1000px", margin: "0 auto", textAlign: "center" }}>
          <div><div style={{ fontSize: "40px", fontWeight: "bold", color: "#667eea" }}>500+</div><div>Mutlu Misafir</div></div>
          <div><div style={{ fontSize: "40px", fontWeight: "bold", color: "#667eea" }}>50+</div><div>Oda Kapasitesi</div></div>
          <div><div style={{ fontSize: "40px", fontWeight: "bold", color: "#667eea" }}>24/7</div><div>Destek</div></div>
          <div><div style={{ fontSize: "40px", fontWeight: "bold", color: "#667eea" }}>%99</div><div>Memnuniyet</div></div>
        </div>
      </div>

      {/* İletişim */}
      <div style={{ padding: "80px 50px", maxWidth: "800px", margin: "0 auto", textAlign: "center" }}>
        <h2 style={{ fontSize: "36px", marginBottom: "40px" }}>İletişim</h2>
        <div style={{ display: "grid", gap: "20px" }}>
          <div style={{ background: "white", padding: "20px", borderRadius: "15px", display: "flex", alignItems: "center", gap: "15px", boxShadow: "0 5px 15px rgba(0,0,0,0.05)" }}>
            <span style={{ fontSize: "24px" }}>📍</span>
            <span>Atatürk Cad. No:123, İstanbul</span>
          </div>
          <div style={{ background: "white", padding: "20px", borderRadius: "15px", display: "flex", alignItems: "center", gap: "15px", boxShadow: "0 5px 15px rgba(0,0,0,0.05)" }}>
            <span style={{ fontSize: "24px" }}>📞</span>
            <span>+90 (212) 123 45 67</span>
          </div>
          <div style={{ background: "white", padding: "20px", borderRadius: "15px", display: "flex", alignItems: "center", gap: "15px", boxShadow: "0 5px 15px rgba(0,0,0,0.05)" }}>
            <span style={{ fontSize: "24px" }}>✉️</span>
            <span>info@aihotelpms.com</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer style={{ background: "#111", color: "white", padding: "40px 50px", textAlign: "center", borderTop: "1px solid #333" }}>
        <div style={{ display: "flex", justifyContent: "center", gap: "40px", marginBottom: "20px" }}>
          <Link to="/" style={{ color: "#888", textDecoration: "none" }}>Ana Sayfa</Link>
          <Link to="/rooms" style={{ color: "#888", textDecoration: "none" }}>Odalar</Link>
          <Link to="/about" style={{ color: "#888", textDecoration: "none" }}>Hakkımızda</Link>
          <Link to="/login" style={{ color: "#888", textDecoration: "none" }}>Admin</Link>
        </div>
        <p style={{ color: "#666" }}>© 2025 AI Hotel PMS</p>
      </footer>
    </div>
  );
}