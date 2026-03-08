export default function AdminDashboard() {
  return (
    <div>
      <h1 style={{ color: '#111' }}>Genel Bakış</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginTop: '20px' }}>
        <StatCard title="Doluluk Oranı" value="%75" color="#3b82f6" />
        <StatCard title="Bugün Girişler" value="12" color="#10b981" />
        <StatCard title="Bugün Çıkışlar" value="8" color="#f59e0b" />
        <StatCard title="Arızalı Odalar" value="2" color="#ef4444" />
      </div>
      <div style={{ marginTop: '40px', padding: '100px', textAlign: 'center', border: '2px dashed #ddd', borderRadius: '15px', color: '#888' }}>
        📈 Buraya Canlı Grafikler Gelecek
      </div>
    </div>
  );
}

function StatCard({ title, value, color }: { title: string, value: string, color: string }) {
  return (
    <div style={{ background: '#ffffff', padding: '20px', borderRadius: '12px', border: '1px solid #e0e0e0' }}>
      <p style={{ color: '#666', margin: 0, fontSize: '14px' }}>{title}</p>
      <h2 style={{ color: color, margin: '10px 0 0 0', fontSize: '28px' }}>{value}</h2>
    </div>
  );
}
