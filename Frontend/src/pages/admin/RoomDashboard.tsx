import { useEffect, useState, useMemo } from 'react';
import { roomApi } from '../../api/roomApi';
import type { Room } from '../../types/room';

// ─── Constants ────────────────────────────────────────────────────────────────

const ROOM_TYPES = ['Standard', 'Deluxe', 'Suite'];
const CAPACITIES = ['1 kişilik', '2 kişilik', '2+1 kişilik', '3 kişilik', '3+1 kişilik', '4 kişilik'];

type CategoryKey = 'all' | 'available' | 'occupied' | 'dirty' | 'maintenance';

const CATEGORIES: { key: CategoryKey; label: string; emoji: string; color: string; bg: string; border: string }[] = [
  { key: 'all',         label: 'Tümü',       emoji: '🏨', color: '#1e293b', bg: '#f8fafc', border: '#cbd5e1' },
  { key: 'available',   label: 'Müsait',     emoji: '✅', color: '#065f46', bg: '#ecfdf5', border: '#6ee7b7' },
  { key: 'occupied',    label: 'Dolu',        emoji: '🔴', color: '#991b1b', bg: '#fef2f2', border: '#fca5a5' },
  { key: 'dirty',       label: 'Kirli',       emoji: '🧹', color: '#92400e', bg: '#fffbeb', border: '#fcd34d' },
  { key: 'maintenance', label: 'Arızalı',    emoji: '🔧', color: '#1e3a8a', bg: '#eff6ff', border: '#93c5fd' },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function getRoomCategory(room: Room): Exclude<CategoryKey, 'all'> {
  if (room.status === 'Bakımda' || room.maintenance_status !== 'Functional') return 'maintenance';
  if (room.is_occupied) return 'occupied';
  if (!room.is_clean) return 'dirty';
  return 'available';
}

function getStatusBadge(room: Room): { label: string; color: string; bg: string } {
  const cat = getRoomCategory(room);
  switch (cat) {
    case 'available':   return { label: 'Müsait',  color: '#065f46', bg: '#d1fae5' };
    case 'occupied':    return { label: 'Dolu',     color: '#991b1b', bg: '#fee2e2' };
    case 'dirty':       return { label: 'Kirli',    color: '#92400e', bg: '#fef3c7' };
    case 'maintenance': return { label: 'Arızalı',  color: '#1e3a8a', bg: '#dbeafe' };
  }
}

function getRoomTypeIcon(type: string) {
  if (type === 'Suite') return '🛋️';
  if (type === 'Deluxe') return '🛏️';
  return '🏠';
}

// ─── Add Room Form ────────────────────────────────────────────────────────────

interface AddFormProps {
  rooms: Room[];
  onDone: () => void;
  onCancel: () => void;
}

function AddRoomForm({ onDone, onCancel }: AddFormProps) {
  const [newRoom, setNewRoom] = useState({
    room_number: '',
    floor: 1,
    room_type: 'Standard',
    capacity: '2 kişilik',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await roomApi.createRoom(newRoom);
      onDone();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Oda eklenemedi. Bu tip/kapasite için fiyat tanımlı olmayabilir.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{
      background: '#fff',
      border: '1.5px solid #e2e8f0',
      borderRadius: 16,
      padding: 28,
      marginBottom: 28,
      boxShadow: '0 4px 24px rgba(0,0,0,.06)',
    }}>
      <h3 style={{ margin: '0 0 20px', fontSize: 16, fontWeight: 700, color: '#0f172a' }}>
        ➕ Yeni Oda Tanımla
      </h3>
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          {/* Oda No */}
          <div style={fieldWrap}>
            <label style={labelStyle}>Oda Numarası</label>
            <input
              type="text" placeholder="Örn: 101" required value={newRoom.room_number}
              onChange={(e) => setNewRoom({ ...newRoom, room_number: e.target.value })}
              style={inputStyle}
            />
          </div>
          {/* Kat */}
          <div style={{ ...fieldWrap, width: 90 }}>
            <label style={labelStyle}>Kat</label>
            <input
              type="number" min={1} value={newRoom.floor}
              onChange={(e) => setNewRoom({ ...newRoom, floor: Number(e.target.value) })}
              style={inputStyle}
            />
          </div>
          {/* Tip */}
          <div style={fieldWrap}>
            <label style={labelStyle}>Oda Tipi</label>
            <select value={newRoom.room_type}
              onChange={(e) => setNewRoom({ ...newRoom, room_type: e.target.value })}
              style={inputStyle}>
              {ROOM_TYPES.map((t) => <option key={t}>{t}</option>)}
            </select>
          </div>
          {/* Kapasite */}
          <div style={fieldWrap}>
            <label style={labelStyle}>Kapasite</label>
            <select value={newRoom.capacity}
              onChange={(e) => setNewRoom({ ...newRoom, capacity: e.target.value })}
              style={inputStyle}>
              {CAPACITIES.map((c) => <option key={c}>{c}</option>)}
            </select>
          </div>
          {/* Actions */}
          <div style={{ display: 'flex', gap: 10, paddingBottom: 2 }}>
            <button type="button" onClick={onCancel}
              style={{ padding: '10px 18px', border: '1.5px solid #e2e8f0', borderRadius: 8, background: '#fff', color: '#64748b', cursor: 'pointer', fontWeight: 600, fontSize: 13 }}>
              İptal
            </button>
            <button type="submit" disabled={saving}
              style={{ padding: '10px 20px', background: saving ? '#94a3b8' : '#0f172a', color: '#fff', border: 'none', borderRadius: 8, cursor: saving ? 'not-allowed' : 'pointer', fontWeight: 700, fontSize: 13 }}>
              {saving ? 'Kaydediliyor…' : 'Kaydet'}
            </button>
          </div>
        </div>
        {error && (
          <p style={{ margin: '12px 0 0', color: '#dc2626', fontSize: 13, fontWeight: 500 }}>⚠ {error}</p>
        )}
      </form>
    </div>
  );
}

// ─── Room Card ────────────────────────────────────────────────────────────────

function RoomCard({ room }: { room: Room }) {
  const badge = getStatusBadge(room);
  const cat   = getRoomCategory(room);

  const accentMap: Record<typeof cat, string> = {
    available:   '#10b981',
    occupied:    '#ef4444',
    dirty:       '#f59e0b',
    maintenance: '#3b82f6',
  };
  const accent = accentMap[cat];

  return (
    <div style={{
      background: '#fff',
      border: '1.5px solid #e2e8f0',
      borderRadius: 14,
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      transition: 'box-shadow .2s, transform .2s',
      boxShadow: '0 2px 8px rgba(0,0,0,.04)',
      position: 'relative',
    }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLDivElement).style.boxShadow = '0 8px 28px rgba(0,0,0,.11)';
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)';
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLDivElement).style.boxShadow = '0 2px 8px rgba(0,0,0,.04)';
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)';
      }}
    >
      {/* Accent top bar */}
      <div style={{ height: 4, background: accent }} />

      {/* Body */}
      <div style={{ padding: '18px 20px 20px', flex: 1 }}>
        {/* Header row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 26 }}>{getRoomTypeIcon(room.room_type)}</span>
            <div>
              <p style={{ margin: 0, fontWeight: 800, fontSize: 18, color: '#0f172a', letterSpacing: '-.02em' }}>
                {room.room_number}
              </p>
              <p style={{ margin: 0, fontSize: 11, color: '#94a3b8', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '.06em' }}>
                Kat {room.floor}
              </p>
            </div>
          </div>
          <span style={{
            padding: '4px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700,
            color: badge.color, background: badge.bg,
            border: `1px solid ${badge.color}30`,
          }}>
            {badge.label}
          </span>
        </div>

        {/* Info grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 0' }}>
          <InfoLine icon="🏷️" label={room.room_type} />
          <InfoLine icon="👥" label={room.capacity} />
          <InfoLine icon="💰" label={`${room.price_per_night?.toLocaleString('tr-TR') ?? '—'} ₺/gece`} />
          <InfoLine icon="🔧" label={room.maintenance_status === 'Functional' ? 'Çalışıyor' : room.maintenance_status} />
        </div>

        {/* Feature chips */}
        {room.features && room.features !== 'Standart Oda Özellikleri' && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginTop: 12 }}>
            {room.features.split(',').slice(0, 4).map((f) => (
              <span key={f} style={{
                padding: '2px 8px', background: '#f1f5f9', color: '#475569',
                borderRadius: 6, fontSize: 11, fontWeight: 500,
              }}>
                {f.trim()}
              </span>
            ))}
          </div>
        )}

        {/* Status note */}
        {cat === 'maintenance' && (
          <div style={{ marginTop: 12, padding: '8px 10px', background: '#eff6ff', borderRadius: 8, fontSize: 12, color: '#1e40af', fontWeight: 500 }}>
            🔧 Bakım/Arıza kaydı için Teknik Servis modülünü kullanın
          </div>
        )}
        {cat === 'dirty' && (
          <div style={{ marginTop: 12, padding: '8px 10px', background: '#fffbeb', borderRadius: 8, fontSize: 12, color: '#92400e', fontWeight: 500 }}>
            🧹 Temizlik görevi için Housekeeping modülüne gidin
          </div>
        )}
      </div>
    </div>
  );
}

function InfoLine({ icon, label }: { icon: string; label: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <span style={{ fontSize: 13 }}>{icon}</span>
      <span style={{ fontSize: 12, color: '#64748b', fontWeight: 500 }}>{label}</span>
    </div>
  );
}

// ─── Section ──────────────────────────────────────────────────────────────────

function RoomSection({ title, emoji, color, bg, border, rooms }: {
  title: string; emoji: string; color: string; bg: string; border: string; rooms: Room[];
}) {
  const [collapsed, setCollapsed] = useState(false);
  if (rooms.length === 0) return null;
  return (
    <div style={{ marginBottom: 32 }}>
      <button
        onClick={() => setCollapsed((c) => !c)}
        style={{
          display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16,
          background: bg, border: `1.5px solid ${border}`,
          borderRadius: 10, padding: '10px 16px',
          cursor: 'pointer', width: '100%', textAlign: 'left',
          transition: 'opacity .15s',
        }}
      >
        <span style={{ fontSize: 20 }}>{emoji}</span>
        <span style={{ fontWeight: 800, fontSize: 15, color, letterSpacing: '-.01em' }}>{title}</span>
        <span style={{
          marginLeft: 6, background: color, color: '#fff',
          borderRadius: 20, padding: '1px 9px', fontSize: 12, fontWeight: 700,
        }}>
          {rooms.length}
        </span>
        <span style={{ marginLeft: 'auto', fontSize: 16, color, opacity: .7 }}>
          {collapsed ? '▸' : '▾'}
        </span>
      </button>
      {!collapsed && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
          gap: 16,
        }}>
          {rooms.map((room) => <RoomCard key={room.id} room={room} />)}
        </div>
      )}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function RoomDashboard() {
  const [rooms, setRooms]         = useState<Room[]>([]);
  const [loading, setLoading]     = useState(true);
  const [showForm, setShowForm]   = useState(false);
  const [activeFilter, setActiveFilter] = useState<CategoryKey>('all');
  const [searchQ, setSearchQ]     = useState('');
  const [viewMode, setViewMode]   = useState<'category' | 'grid'>('category');

  const fetchRooms = async () => {
    try {
      setLoading(true);
      setRooms(await roomApi.getRooms());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRooms(); }, []);

  // ── Derived ────────────────────────────────────────────────────────────────

  const filtered = useMemo(() => {
    let list = rooms;
    if (activeFilter !== 'all') {
      list = list.filter((r) => getRoomCategory(r) === activeFilter);
    }
    if (searchQ.trim()) {
      const q = searchQ.toLowerCase();
      list = list.filter(
        (r) =>
          r.room_number.toLowerCase().includes(q) ||
          r.room_type.toLowerCase().includes(q) ||
          r.capacity.toLowerCase().includes(q)
      );
    }
    return list;
  }, [rooms, activeFilter, searchQ]);

  const grouped = useMemo(() => ({
    available:   filtered.filter((r) => getRoomCategory(r) === 'available'),
    occupied:    filtered.filter((r) => getRoomCategory(r) === 'occupied'),
    dirty:       filtered.filter((r) => getRoomCategory(r) === 'dirty'),
    maintenance: filtered.filter((r) => getRoomCategory(r) === 'maintenance'),
  }), [filtered]);

  const counts: Record<CategoryKey, number> = {
    all:         rooms.length,
    available:   rooms.filter((r) => getRoomCategory(r) === 'available').length,
    occupied:    rooms.filter((r) => getRoomCategory(r) === 'occupied').length,
    dirty:       rooms.filter((r) => getRoomCategory(r) === 'dirty').length,
    maintenance: rooms.filter((r) => getRoomCategory(r) === 'maintenance').length,
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8', fontSize: 15 }}>
        Odalar yükleniyor…
      </div>
    );
  }

  return (
    <div style={{ padding: 24, fontFamily: "'DM Sans', sans-serif" }}>

      {/* ── Page header ──────────────────────────────────────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 26, fontWeight: 800, color: '#0f172a', letterSpacing: '-.03em' }}>
            🏨 Oda Yönetimi
          </h1>
          <p style={{ margin: '4px 0 0', color: '#94a3b8', fontSize: 13 }}>
            {rooms.length} oda · {counts.available} müsait · {counts.occupied} dolu · {counts.dirty} kirli · {counts.maintenance} arızalı
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          {/* View toggle */}
          <div style={{ display: 'flex', border: '1.5px solid #e2e8f0', borderRadius: 8, overflow: 'hidden' }}>
            {(['category', 'grid'] as const).map((m) => (
              <button key={m} onClick={() => setViewMode(m)}
                style={{
                  padding: '8px 14px', border: 'none', cursor: 'pointer', fontSize: 12, fontWeight: 600,
                  background: viewMode === m ? '#0f172a' : '#fff',
                  color: viewMode === m ? '#fff' : '#64748b',
                }}>
                {m === 'category' ? '≡ Kategori' : '⊞ Izgara'}
              </button>
            ))}
          </div>
          <button
            onClick={() => setShowForm((v) => !v)}
            style={{
              padding: '10px 20px', background: showForm ? '#64748b' : '#0f172a',
              color: '#fff', border: 'none', borderRadius: 8,
              cursor: 'pointer', fontWeight: 700, fontSize: 13,
            }}>
            {showForm ? '✕ İptal' : '+ Yeni Oda'}
          </button>
        </div>
      </div>

      {/* ── Add form ─────────────────────────────────────────────────── */}
      {showForm && (
        <AddRoomForm
          rooms={rooms}
          onDone={() => { setShowForm(false); fetchRooms(); }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {/* ── Stat cards ───────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12, marginBottom: 24 }}>
        {CATEGORIES.map(({ key, label, emoji, color, bg, border }) => (
          <button
            key={key}
            onClick={() => setActiveFilter(key)}
            style={{
              padding: '14px 12px',
              background: activeFilter === key ? color : bg,
              border: `1.5px solid ${activeFilter === key ? color : border}`,
              borderRadius: 12, cursor: 'pointer',
              textAlign: 'left', transition: 'all .18s',
              boxShadow: activeFilter === key ? `0 4px 16px ${color}33` : 'none',
            }}
          >
            <p style={{ margin: 0, fontSize: 20 }}>{emoji}</p>
            <p style={{ margin: '6px 0 2px', fontSize: 22, fontWeight: 800, color: activeFilter === key ? '#fff' : color }}>
              {counts[key]}
            </p>
            <p style={{ margin: 0, fontSize: 11, fontWeight: 600, color: activeFilter === key ? 'rgba(255,255,255,.8)' : '#94a3b8', textTransform: 'uppercase', letterSpacing: '.05em' }}>
              {label}
            </p>
          </button>
        ))}
      </div>

      {/* ── Search ───────────────────────────────────────────────────── */}
      <div style={{ marginBottom: 24 }}>
        <input
          placeholder="Oda no, tip veya kapasite ara…"
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
          style={{
            padding: '10px 14px', width: '100%', maxWidth: 360,
            border: '1.5px solid #e2e8f0', borderRadius: 8,
            fontSize: 13, color: '#0f172a', outline: 'none',
            background: '#fff', boxSizing: 'border-box',
          }}
        />
      </div>

      {/* ── Content ──────────────────────────────────────────────────── */}
      {filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 64, color: '#94a3b8', fontSize: 14 }}>
          Bu kriterlere uyan oda bulunamadı.
        </div>
      ) : viewMode === 'grid' ? (
        /* Flat grid mode */
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 16 }}>
          {filtered.map((room) => <RoomCard key={room.id} room={room} />)}
        </div>
      ) : (
        /* Categorized sections */
        <>
          <RoomSection title="Müsait Odalar"  emoji="✅" color="#065f46" bg="#ecfdf5" border="#6ee7b7" rooms={grouped.available} />
          <RoomSection title="Dolu Odalar"    emoji="🔴" color="#991b1b" bg="#fef2f2" border="#fca5a5" rooms={grouped.occupied} />
          <RoomSection title="Kirli Odalar"   emoji="🧹" color="#92400e" bg="#fffbeb" border="#fcd34d" rooms={grouped.dirty} />
          <RoomSection title="Arızalı Odalar" emoji="🔧" color="#1e3a8a" bg="#eff6ff" border="#93c5fd" rooms={grouped.maintenance} />
        </>
      )}

      {/* ── Info note ────────────────────────────────────────────────── */}
      <div style={{
        marginTop: 32, padding: '14px 18px', background: '#f8fafc',
        border: '1.5px solid #e2e8f0', borderRadius: 10,
        display: 'flex', gap: 16, flexWrap: 'wrap',
      }}>
        <span style={{ fontSize: 12, color: '#64748b', fontWeight: 500 }}>ℹ️ <strong>Not:</strong></span>
        <span style={{ fontSize: 12, color: '#64748b' }}>🧹 Temizlik durumu → <strong>Housekeeping</strong> modülünden yönetilir</span>
        <span style={{ fontSize: 12, color: '#64748b' }}>🔧 Arıza bildirimi → <strong>Teknik Servis</strong> modülünden yönetilir</span>
        <span style={{ fontSize: 12, color: '#64748b' }}>📅 Check-in/out → <strong>Rezervasyonlar</strong> modülünden yapılır</span>
      </div>
    </div>
  );
}

// ─── Style atoms ─────────────────────────────────────────────────────────────

const fieldWrap: React.CSSProperties = {
  display: 'flex', flexDirection: 'column', gap: 6, minWidth: 130,
};

const labelStyle: React.CSSProperties = {
  fontSize: 12, fontWeight: 600, color: '#475569', letterSpacing: '.02em',
};

const inputStyle: React.CSSProperties = {
  padding: '9px 12px', border: '1.5px solid #e2e8f0', borderRadius: 8,
  fontSize: 13, color: '#0f172a', background: '#fff', outline: 'none',
};
