import { useState } from 'react';
import { pricingAgentApi } from '../../api/pricingAgentApi';
import { useAuth } from '../../hooks/useAuth';

export default function PricingSuggestions() {
  const { user } = useAuth();
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [selected, setSelected] = useState<Record<number, boolean>>({});
  const [loading, setLoading] = useState(false);

  const getSuggestions = async () => {
    if (!checkIn || !checkOut) return alert('Lütfen giriş ve çıkış tarihlerini seçin');
    setLoading(true);
    try {
      const res = await pricingAgentApi.suggest(checkIn, checkOut);
      setSuggestions(res.suggestions || []);
    } catch (err: any) {
      alert('Öneriler alınamadı: ' + (err?.response?.data?.detail || err.message || JSON.stringify(err)));
    } finally {
      setLoading(false);
    }
  };

  const toggle = (i: number) => setSelected((s) => ({ ...s, [i]: !s[i] }));

  const applySelected = async () => {
    const toApply = suggestions
      .map((s, i) => ({ ...s, __idx: i }))
      .filter((s) => selected[s.__idx])
      .map((s) => ({ room_type: s.room_type, capacity: s.capacity, suggested_price: s.suggested_price }));

    if (toApply.length === 0) return alert('Lütfen en az bir öneri seçin');
    if (!confirm(`Seçilen ${toApply.length} öneriyi uygulamak istiyor musunuz?`)) return;

    try {
      const res = await pricingAgentApi.apply(toApply);
      alert('Uygulama tamamlandı. Sonuç: ' + JSON.stringify(res.applied || res));
      // optionally refresh
      setSelected({});
    } catch (err: any) {
      alert('Uygulama sırasında hata: ' + (err?.response?.data?.detail || err.message || JSON.stringify(err)));
    }
  };

  const fmtCurrency = (v: number) => new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY', maximumFractionDigits: 0 }).format(v);

  return (
    <div>
      <h2>Fiyat Önerileri</h2>
      <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        <input type="date" value={checkIn} onChange={(e) => setCheckIn(e.target.value)} />
        <input type="date" value={checkOut} onChange={(e) => setCheckOut(e.target.value)} />
        <button onClick={getSuggestions} disabled={loading} style={{ background: '#667eea', color: 'white', padding: '8px 12px', borderRadius: 6 }}>{loading ? 'Bekleyin...' : 'Öneri Al'}</button>
        {user?.role === 'moderator' && <button onClick={applySelected} style={{ background: '#10b981', color: 'white', padding: '8px 12px', borderRadius: 6 }}>Seçilenleri Uygula</button>}
      </div>

      <div>
        {suggestions.length === 0 ? <div>Öneri yok.</div> : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>
                <th></th>
                <th>Oda Tipi</th>
                <th>Kapasite</th>
                <th>Base Price</th>
                <th>Suggested</th>
                <th>Multiplier</th>
                <th>Reasons</th>
              </tr>
            </thead>
            <tbody>
              {suggestions.map((s, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: 8 }}><input type="checkbox" checked={!!selected[i]} onChange={() => toggle(i)} /></td>
                  <td style={{ padding: 8 }}>{s.room_type}</td>
                  <td style={{ padding: 8 }}>{s.capacity}</td>
                  <td style={{ padding: 8 }}>{fmtCurrency(Number(s.base_price) || 0)}</td>
                  <td style={{ padding: 8 }}>{fmtCurrency(Number(s.suggested_price) || 0)}</td>
                  <td style={{ padding: 8 }}>{(Number(s.multiplier) || 0).toFixed(2)}</td>
                  <td style={{ padding: 8 }}>{s.reasons}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
