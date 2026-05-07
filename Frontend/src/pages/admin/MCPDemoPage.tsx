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

const QUICK_ACTIONS = [
  {
    label: '📊 Genel Rapor',
    msg: 'Otelin genel durumunu analiz et. Son yorumları, kategori özetini ve haftalık trendi birlikte değerlendirerek kapsamlı bir yönetici raporu sun.',
    group: 'Genel',
  },
  {
    label: '🔴 Sorunlar',
    msg: 'Son yorumlardaki şikayetleri önceliğe göre listele. 🔴 Kritik / 🟡 Orta / 🟢 Düşük olarak sınıflandır, acil müdahale gerekenleri öne çıkar.',
    group: 'Genel',
  },
  {
    label: '📈 Haftalık Trend',
    msg: 'Son 4 haftanın yorum sayısı ve puan trendini göster. Memnuniyet artıyor mu azalıyor mu, yorum hacmi değişti mi?',
    group: 'Genel',
  },
  {
    label: '🍽️ Yemek',
    msg: 'Yemek ve kahvaltı ile ilgili yorumları ara. Misafirlerin yemek hakkındaki şikayetleri ve övgüleri neler?',
    group: 'Konu',
  },
  {
    label: '🧹 Temizlik',
    msg: 'Temizlik ve hijyen ile ilgili yorumları ara. Hangi sorunlar tekrar ediyor, hangi odalar öne çıkıyor?',
    group: 'Konu',
  },
  {
    label: '❄️ Klima',
    msg: 'Klima, ısıtma veya soğutma ile ilgili yorumları ara ve tekrar eden sorunları raporla.',
    group: 'Konu',
  },
  {
    label: '⭐ Düşük Puanlar',
    msg: 'Son 90 günde 1 ve 2 yıldız alan yorumları getir. Ortak şikayet konularını tespit et.',
    group: 'Filtre',
  },
  {
    label: '🏨 Oda 101',
    msg: '101 numaralı odanın tüm yorumlarını getir, ortalama puanını ve tekrar eden sorunları değerlendir.',
    group: 'Oda',
  },
];

export default function MCPDemoPage() {
  const [messages, setMessages]       = useState<Message[]>([]);
  const [input, setInput]             = useState('');
  const [loading, setLoading]         = useState(false);
  const [sessionId, setSessionId]     = useState<string | null>(null);
  const [msgCount, setMsgCount]       = useState(0);
  const [error, setError]             = useState<string | null>(null);
  const bottomRef                     = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

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
      setMessages(prev => prev.slice(0, -1)); // remove optimistic user message
    }
    setLoading(false);
  };

  const clearSession = async () => {
    if (sessionId) {
      await api.delete(`/agents/mcp/chat/session/${sessionId}`).catch(() => {});
    }
    setMessages([]);
    setSessionId(null);
    setMsgCount(0);
    setError(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 40px)', maxWidth: 860, margin: '0 auto', padding: '20px 20px 0', fontFamily: 'sans-serif' }}>

      {/* Header */}
      <div style={{ background: 'linear-gradient(135deg,#1e40af 0%,#3b82f6 100%)', color: '#fff', borderRadius: 12, padding: '16px 22px', marginBottom: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 19 }}>Yorum Analizi — AI Asistan</h2>
          <p style={{ margin: '4px 0 0', opacity: 0.85, fontSize: 12 }}>
            MCP · get_recent_reviews · Gerçek DB verisi
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {sessionId && (
            <span style={{ background: 'rgba(255,255,255,0.2)', borderRadius: 6, padding: '3px 9px', fontSize: 11 }}>
              {msgCount} mesaj
            </span>
          )}
          <button onClick={clearSession} style={{ background: 'rgba(255,255,255,0.15)', color: '#fff', border: '1px solid rgba(255,255,255,0.3)', borderRadius: 7, padding: '6px 14px', cursor: 'pointer', fontSize: 12 }}>
            Yeni Sohbet
          </button>
        </div>
      </div>

      {/* Quick actions */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
        {QUICK_ACTIONS.map(({ label, msg, group }) => {
          const isGeneral = group === 'Genel';
          return (
            <button key={label} onClick={() => sendMessage(msg)} disabled={loading} style={{
              background: isGeneral ? '#eff6ff' : '#f8fafc',
              border: `1px solid ${isGeneral ? '#bfdbfe' : '#e2e8f0'}`,
              borderRadius: 20,
              padding: '5px 13px', fontSize: 12, cursor: loading ? 'not-allowed' : 'pointer',
              color: isGeneral ? '#1d4ed8' : '#475569',
              fontWeight: isGeneral ? 600 : 400,
              opacity: loading ? 0.5 : 1,
            }}>
              {label}
            </button>
          );
        })}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12, paddingBottom: 16 }}>

        {messages.length === 0 && !loading && (
          <div style={{ textAlign: 'center', color: '#94a3b8', marginTop: 60 }}>
            <div style={{ fontSize: 40, marginBottom: 10 }}>💬</div>
            <p style={{ fontSize: 14 }}>Müşteri yorumları hakkında bir soru sor veya yukarıdaki hızlı aksiyonları kullan.</p>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {m.role === 'assistant' && (
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#3b82f6', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, marginRight: 8, flexShrink: 0, alignSelf: 'flex-end' }}>
                🤖
              </div>
            )}
            <div style={{
              maxWidth: '75%',
              background: m.role === 'user' ? '#3b82f6' : '#f8fafc',
              color:      m.role === 'user' ? '#fff'    : '#1e293b',
              borderRadius: m.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
              padding: '11px 15px',
              fontSize: 14,
              lineHeight: 1.7,
              whiteSpace: 'pre-wrap',
              border: m.role === 'assistant' ? '1px solid #e5e7eb' : 'none',
              boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
            }}>
              {m.content}
              <div style={{ fontSize: 10, opacity: 0.5, marginTop: 4, textAlign: 'right' }}>{m.ts}</div>
            </div>
            {m.role === 'user' && (
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, marginLeft: 8, flexShrink: 0, alignSelf: 'flex-end' }}>
                👤
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8 }}>
            <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#3b82f6', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16 }}>🤖</div>
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
      <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: 12, paddingBottom: 12, background: '#fff' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage(input)}
            placeholder="Memnuniyet raporu yaz, sorunları listele..."
            disabled={loading}
            style={{ flex: 1, padding: '11px 16px', borderRadius: 24, border: '1.5px solid #d1d5db', fontSize: 14, outline: 'none', background: loading ? '#f8fafc' : '#fff' }}
          />
          <button onClick={() => sendMessage(input)} disabled={loading || !input.trim()} style={{
            background: loading || !input.trim() ? '#cbd5e1' : '#3b82f6',
            color: '#fff', border: 'none', borderRadius: '50%', width: 44, height: 44,
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer', fontSize: 18, flexShrink: 0,
          }}>
            ↑
          </button>
        </div>
      </div>
    </div>
  );
}

function TypingDots() {
  return (
    <div style={{ display: 'flex', gap: 5, alignItems: 'center', height: 16 }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: 8, height: 8, borderRadius: '50%', background: '#94a3b8',
          animation: 'bounce 1.2s infinite',
          animationDelay: `${i * 0.2}s`,
        }} />
      ))}
      <style>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  );
}

function now() {
  return new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}
