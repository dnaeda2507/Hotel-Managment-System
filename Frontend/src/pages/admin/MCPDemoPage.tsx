import { useState, useRef, useEffect } from 'react';
import api from '../../api/authApi';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  ts: string;
}

interface ChatResponse {
  session_id: string;
  response: string;
  is_new_session: boolean;
  message_count: number;
}

interface Dashboard {
  date: string;
  total_rooms: number;
  occupied: number;
  available: number;
  occupancy_pct: number;
  checkins_today: number;
  checkouts_today: number;
  avg_rating: number | null;
  pending_housekeeping: number;
  open_maintenance: number;
}

const QUICK_ACTIONS = [
  // Yorum
  { label: '📊 Genel Rapor',    group: 'Yorum',  msg: 'Otelin genel durumunu analiz et. Son yorumları, kategori özetini ve haftalık trendi birlikte değerlendirerek kapsamlı bir yönetici raporu sun.' },
  { label: '🔴 Sorunlar',       group: 'Yorum',  msg: 'Son yorumlardaki şikayetleri önceliğe göre listele. 🔴 Kritik / 🟡 Orta / 🟢 Düşük olarak sınıflandır.' },
  { label: '📈 Haftalık Trend', group: 'Yorum',  msg: 'Son 4 haftanın yorum sayısı ve puan trendini göster.' },
  { label: '⭐ Düşük Puanlar', group: 'Yorum',  msg: 'Son 90 günde 1 ve 2 yıldız alan yorumları getir. Ortak şikayet konularını tespit et.' },
  // Operasyon
  { label: '🏨 Müsait Odalar',  group: 'Ops',    msg: 'Bugün müsait olan odaları ve fiyatlarını listele.' },
  { label: '📅 Çıkışlar',       group: 'Ops',    msg: 'Bugün ve yarın check-out yapacak misafirleri listele.' },
  { label: '🧹 Temizlik',       group: 'Ops',    msg: 'Temizlik bekleyen odaları listele. Hangi odalar hazır değil?' },
  { label: '🔧 Bakım',          group: 'Ops',    msg: 'Açık teknik arıza taleplerini öncelik sırasıyla listele.' },
  { label: '💰 Fiyat Önerisi',  group: 'Ops',    msg: '1 numaralı oda için bugünkü doluluk ve sezona göre fiyat önerisi hesapla.' },
  { label: '📋 Günlük Özet',   group: 'Ops',    msg: 'Bugünün doluluk durumu, giriş/çıkışlar ve bekleyen operasyonel görevleri özetle.' },
];

const GROUP_COLORS: Record<string, { bg: string; border: string; color: string; badge: string }> = {
  Yorum: { bg: '#eff6ff', border: '#bfdbfe', color: '#1d4ed8', badge: '#dbeafe' },
  Ops:   { bg: '#f0fdf4', border: '#bbf7d0', color: '#166534', badge: '#dcfce7' },
};

export default function MCPDemoPage() {
  const [messages, setMessages]     = useState<Message[]>([]);
  const [input, setInput]           = useState('');
  const [loading, setLoading]       = useState(false);
  const [sessionId, setSessionId]   = useState<string | null>(null);
  const [msgCount, setMsgCount]     = useState(0);
  const [error, setError]           = useState<string | null>(null);
  const [dashboard, setDashboard]   = useState<Dashboard | null>(null);
  const [dashLoading, setDashLoading] = useState(true);
  const bottomRef                   = useRef<HTMLDivElement>(null);

  useEffect(() => { loadDashboard(); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  const loadDashboard = async () => {
    setDashLoading(true);
    try {
      const res = await api.get<Dashboard>('/agents/mcp/dashboard');
      setDashboard(res.data);
    } catch { /* sessiz geç */ }
    setDashLoading(false);
  };

  const sendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMsg: Message = { role: 'user', content: trimmed, ts: now() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const res = await api.post<ChatResponse>('/agents/mcp/chat', {
        message:    trimmed,
        session_id: sessionId,
      });
      const d = res.data;
      if (!sessionId) setSessionId(d.session_id);
      setMsgCount(d.message_count);
      setMessages(prev => [...prev, { role: 'assistant', content: d.response, ts: now() }]);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Bağlantı hatası';
      setError(msg);
      setMessages(prev => prev.slice(0, -1));
    }
    setLoading(false);
  };

  const clearSession = async () => {
    if (sessionId) await api.delete(`/agents/mcp/chat/session/${sessionId}`).catch(() => {});
    setMessages([]);
    setSessionId(null);
    setMsgCount(0);
    setError(null);
  };

  const groups = ['Yorum', 'Ops'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 40px)', maxWidth: 920, margin: '0 auto', padding: '20px 20px 0', fontFamily: 'sans-serif' }}>

      {/* Header */}
      <div style={{ background: 'linear-gradient(135deg,#1e40af 0%,#3b82f6 100%)', color: '#fff', borderRadius: 12, padding: '16px 22px', marginBottom: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 18 }}>Otel Yönetim Asistanı</h2>
          <p style={{ margin: '4px 0 0', opacity: 0.85, fontSize: 11 }}>
            MCP · Review Server (8001) · Ops Server (8002) · GPT-4o-mini
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {sessionId && (
            <span style={{ background: 'rgba(255,255,255,0.2)', borderRadius: 6, padding: '3px 9px', fontSize: 11 }}>
              {msgCount} mesaj
            </span>
          )}
          <button onClick={clearSession} style={{ background: 'rgba(255,255,255,0.15)', color: '#fff', border: '1px solid rgba(255,255,255,0.3)', borderRadius: 7, padding: '6px 14px', cursor: 'pointer', fontSize: 12 }}>
            Yeni Sohbet
          </button>
          <button onClick={loadDashboard} style={{ background: 'rgba(255,255,255,0.15)', color: '#fff', border: '1px solid rgba(255,255,255,0.3)', borderRadius: 7, padding: '6px 10px', cursor: 'pointer', fontSize: 12 }}>
            ↻
          </button>
        </div>
      </div>

      {/* Dashboard status bar */}
      {!dashLoading && dashboard && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 8, marginBottom: 10 }}>
          <StatCard label="Doluluk" value={`%${dashboard.occupancy_pct}`} sub={`${dashboard.occupied}/${dashboard.total_rooms} oda`} color="#3b82f6" />
          <StatCard label="Bugün Giriş" value={String(dashboard.checkins_today)} sub="rezervasyon" color="#10b981" />
          <StatCard label="Bugün Çıkış" value={String(dashboard.checkouts_today)} sub="rezervasyon" color="#f59e0b" />
          <StatCard label="Ort. Puan" value={dashboard.avg_rating ? `${dashboard.avg_rating}/5` : '-'} sub="son 30 gün" color="#8b5cf6" />
          <StatCard label="Bekleyen" value={String(dashboard.pending_housekeeping + dashboard.open_maintenance)} sub={`${dashboard.pending_housekeeping} temizlik · ${dashboard.open_maintenance} bakım`} color="#ef4444" />
        </div>
      )}
      {dashLoading && (
        <div style={{ background: '#f8fafc', border: '1px solid #e5e7eb', borderRadius: 10, padding: '10px 16px', marginBottom: 10, fontSize: 12, color: '#94a3b8' }}>
          Dashboard yükleniyor...
        </div>
      )}

      {/* Quick actions */}
      <div style={{ marginBottom: 10 }}>
        {groups.map(group => (
          <div key={group} style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 5, alignItems: 'center' }}>
            <span style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', minWidth: 42, textTransform: 'uppercase', letterSpacing: 1 }}>{group}</span>
            {QUICK_ACTIONS.filter(a => a.group === group).map(({ label, msg }) => {
              const c = GROUP_COLORS[group];
              return (
                <button key={label} onClick={() => sendMessage(msg)} disabled={loading} style={{
                  background: c.bg, border: `1px solid ${c.border}`, borderRadius: 20,
                  padding: '4px 12px', fontSize: 12, cursor: loading ? 'not-allowed' : 'pointer',
                  color: c.color, opacity: loading ? 0.5 : 1,
                }}>
                  {label}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12, paddingBottom: 16 }}>

        {messages.length === 0 && !loading && (
          <div style={{ textAlign: 'center', color: '#94a3b8', marginTop: 40 }}>
            <div style={{ fontSize: 36, marginBottom: 8 }}>💬</div>
            <p style={{ fontSize: 13, lineHeight: 1.6 }}>
              Yorum analizi veya operasyonel soru sor.<br />
              <span style={{ fontSize: 11 }}>Yorum server'ı (8001) · Ops server'ı (8002) · 12 tool + 3 resource aktif</span>
            </p>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {m.role === 'assistant' && (
              <div style={{ width: 30, height: 30, borderRadius: '50%', background: '#3b82f6', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, marginRight: 8, flexShrink: 0, alignSelf: 'flex-end' }}>
                🤖
              </div>
            )}
            <div style={{
              maxWidth: '75%',
              background: m.role === 'user' ? '#3b82f6' : '#f8fafc',
              color:      m.role === 'user' ? '#fff'    : '#1e293b',
              borderRadius: m.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
              padding: '10px 14px', fontSize: 13, lineHeight: 1.7, whiteSpace: 'pre-wrap',
              border: m.role === 'assistant' ? '1px solid #e5e7eb' : 'none',
              boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
            }}>
              {m.content}
              <div style={{ fontSize: 10, opacity: 0.5, marginTop: 4, textAlign: 'right' }}>{m.ts}</div>
            </div>
            {m.role === 'user' && (
              <div style={{ width: 30, height: 30, borderRadius: '50%', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, marginLeft: 8, flexShrink: 0, alignSelf: 'flex-end' }}>
                👤
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8 }}>
            <div style={{ width: 30, height: 30, borderRadius: '50%', background: '#3b82f6', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14 }}>🤖</div>
            <div style={{ background: '#f8fafc', border: '1px solid #e5e7eb', borderRadius: '18px 18px 18px 4px', padding: '12px 16px' }}>
              <TypingDots />
            </div>
          </div>
        )}

        {error && (
          <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 10, padding: '10px 14px', color: '#991b1b', fontSize: 13 }}>
            <strong>Hata:</strong> {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: 10, paddingBottom: 12, background: '#fff' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage(input)}
            placeholder="Yorum analizi veya otel operasyonları hakkında sor..."
            disabled={loading}
            style={{ flex: 1, padding: '10px 16px', borderRadius: 24, border: '1.5px solid #d1d5db', fontSize: 13, outline: 'none', background: loading ? '#f8fafc' : '#fff' }}
          />
          <button onClick={() => sendMessage(input)} disabled={loading || !input.trim()} style={{
            background: loading || !input.trim() ? '#cbd5e1' : '#3b82f6',
            color: '#fff', border: 'none', borderRadius: '50%', width: 42, height: 42,
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer', fontSize: 18, flexShrink: 0,
          }}>
            ↑
          </button>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, color }: { label: string; value: string; sub: string; color: string }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: '10px 14px', borderLeft: `3px solid ${color}` }}>
      <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: 11, color: '#64748b' }}>{sub}</div>
    </div>
  );
}

function TypingDots() {
  return (
    <div style={{ display: 'flex', gap: 5, alignItems: 'center', height: 16 }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: 7, height: 7, borderRadius: '50%', background: '#94a3b8',
          animation: 'bounce 1.2s infinite', animationDelay: `${i * 0.2}s`,
        }} />
      ))}
      <style>{`@keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }`}</style>
    </div>
  );
}

function now() {
  return new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}
