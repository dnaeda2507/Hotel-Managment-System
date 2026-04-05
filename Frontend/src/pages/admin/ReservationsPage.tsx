import { useState, useEffect, useCallback } from 'react';
import { reservationApi } from '../../api/reservationApi';
import { roomApi } from '../../api/roomApi';
import type { Reservation, ReservationCreate, ReservationStatus } from '../../types/reservation';
import type { Room } from '../../types/room';

// ─── Constants ────────────────────────────────────────────────────────────────

const STATUS_META: Record<ReservationStatus, { label: string; color: string; bg: string }> = {
  beklemede:      { label: 'Beklemede',      color: '#b45309', bg: '#fef3c7' },
  'onaylandı':    { label: 'Onaylandı',      color: '#065f46', bg: '#d1fae5' },
  'giriş_yapıldı':{ label: 'Giriş Yapıldı', color: '#1e40af', bg: '#dbeafe' },
  'çıkış_yapıldı':{ label: 'Çıkış Yapıldı', color: '#6b7280', bg: '#f3f4f6' },
  'iptal_edildi': { label: 'İptal Edildi',   color: '#991b1b', bg: '#fee2e2' },
};

const STAT_FILTERS: { key: string; label: string; color: string }[] = [
  { key: 'all',           label: 'Tümü',         color: '#3b82f6' },
  { key: 'onaylandı',     label: 'Onaylandı',    color: '#10b981' },
  { key: 'beklemede',     label: 'Beklemede',    color: '#f59e0b' },
  { key: 'giriş_yapıldı',label: 'Girişte',       color: '#6366f1' },
  { key: 'çıkış_yapıldı',label: 'Çıkış Yapıldı',color: '#6b7280' },
  { key: 'iptal_edildi', label: 'İptal',         color: '#ef4444' },
];

// ─── Empty form ───────────────────────────────────────────────────────────────

const emptyForm = (): ReservationCreate => ({
  room_id: 0,
  guest_name: '',
  guest_email: '',
  guest_phone: '',
  guest_id_number: '',
  guest_count: 1,
  special_requests: '',
  check_in_date: '',
  check_out_date: '',
  notes: '',
});

// ─── Component ────────────────────────────────────────────────────────────────

export default function ReservationsPage() {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [rooms, setRooms]               = useState<Room[]>([]);
  const [loading, setLoading]           = useState(true);
  const [filter, setFilter]             = useState('all');
  const [search, setSearch]             = useState('');
  const [showModal, setShowModal]       = useState(false);
  const [detailModal, setDetailModal]   = useState<Reservation | null>(null);
  const [form, setForm]                 = useState<ReservationCreate>(emptyForm());
  const [availability, setAvailability] = useState<{ total_nights: number; total_price: number; price_per_night: number } | null>(null);
  const [checkingAvail, setCheckingAvail] = useState(false);
  const [saving, setSaving]             = useState(false);
  const [error, setError]               = useState('');

  // ── Load data ──────────────────────────────────────────────────────────────

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const [res, rm] = await Promise.all([
        reservationApi.getAll(),
        roomApi.getRooms(),
      ]);
      setReservations(res);
      setRooms(rm);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // ── Check availability when dates + room change ────────────────────────────

  useEffect(() => {
    if (!form.room_id || !form.check_in_date || !form.check_out_date) {
      setAvailability(null);
      return;
    }
    if (form.check_in_date >= form.check_out_date) return;

    setCheckingAvail(true);
    reservationApi
      .checkAvailability(form.room_id, form.check_in_date, form.check_out_date)
      .then((data) => {
        if (data.available) {
          setAvailability({
            total_nights: data.total_nights,
            total_price: data.total_price,
            price_per_night: data.price_per_night,
          });
          setError('');
        } else {
          setAvailability(null);
          setError('Bu tarih aralığında oda müsait değil.');
        }
      })
      .catch(() => { setAvailability(null); setError('Müsaitlik kontrol edilemedi.'); })
      .finally(() => setCheckingAvail(false));
  }, [form.room_id, form.check_in_date, form.check_out_date]);

  // ── Actions ────────────────────────────────────────────────────────────────

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!availability) { setError('Lütfen müsait bir oda ve tarih seçin.'); return; }
    setSaving(true);
    try {
      await reservationApi.create(form);
      setShowModal(false);
      setForm(emptyForm());
      setAvailability(null);
      setError('');
      load();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Rezervasyon oluşturulamadı.');
    } finally {
      setSaving(false);
    }
  };

  const handleCheckIn = async (id: number) => {
    try { await reservationApi.checkIn(id); load(); }
    catch (e: any) { alert(e.response?.data?.detail || 'Hata'); }
  };

  const handleCheckOut = async (id: number) => {
    try { await reservationApi.checkOut(id); load(); }
    catch (e: any) { alert(e.response?.data?.detail || 'Hata'); }
  };

  const handleCancel = async (id: number) => {
    if (!confirm('Bu rezervasyonu iptal etmek istediğinizden emin misiniz?')) return;
    try { await reservationApi.cancel(id); load(); }
    catch (e: any) { alert(e.response?.data?.detail || 'Hata'); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Rezervasyonu kalıcı olarak silmek istiyor musunuz?')) return;
    try { await reservationApi.delete(id); load(); setDetailModal(null); }
    catch (e: any) { alert(e.response?.data?.detail || 'Hata'); }
  };

  // ── Derived data ───────────────────────────────────────────────────────────

  const getRoomLabel = (roomId: number) => {
    const r = rooms.find((x) => x.id === roomId);
    return r ? `Oda ${r.room_number} — ${r.room_type} (${r.capacity})` : `#${roomId}`;
  };

  const filtered = reservations.filter((r) => {
    const matchStatus = filter === 'all' || r.status === filter;
    const q = search.toLowerCase();
    const matchSearch =
      !q ||
      r.guest_name.toLowerCase().includes(q) ||
      r.guest_email.toLowerCase().includes(q) ||
      getRoomLabel(r.room_id).toLowerCase().includes(q);
    return matchStatus && matchSearch;
  });

  const stats = {
    all: reservations.length,
    'onaylandı': reservations.filter((r) => r.status === 'onaylandı').length,
    beklemede: reservations.filter((r) => r.status === 'beklemede').length,
    'giriş_yapıldı': reservations.filter((r) => r.status === 'giriş_yapıldı').length,
    'çıkış_yapıldı': reservations.filter((r) => r.status === 'çıkış_yapıldı').length,
    'iptal_edildi': reservations.filter((r) => r.status === 'iptal_edildi').length,
  } as Record<string, number>;

  const today = new Date().toISOString().split('T')[0];

  // ── Render ─────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div style={{ padding: '100px 24px 24px 24px', textAlign: 'center', color: '#888' }}>
        Yükleniyor…
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, color: '#111', margin: 0 }}>
          📅 Rezervasyonlar
        </h1>
        <button
          onClick={() => { setForm(emptyForm()); setAvailability(null); setError(''); setShowModal(true); }}
          style={btn('#3b82f6')}
        >
          + Yeni Rezervasyon
        </button>
      </div>

      {/* ── Stat pills ─────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
        {STAT_FILTERS.map(({ key, label, color }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            style={{
              padding: '10px 20px',
              borderRadius: 10,
              border: `2px solid ${filter === key ? color : '#e0e0e0'}`,
              background: filter === key ? color : '#fff',
              color: filter === key ? '#fff' : '#444',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: 13,
              transition: 'all .2s',
            }}
          >
            {label} <span style={{ opacity: .75 }}>({stats[key] ?? 0})</span>
          </button>
        ))}
      </div>

      {/* ── Search ─────────────────────────────────────────────────────── */}
      <div style={{ marginBottom: 20 }}>
        <input
          placeholder="Misafir adı, e-posta veya oda ara…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: '100%', maxWidth: 420, padding: '10px 14px',
            border: '1.5px solid #ddd', borderRadius: 8,
            fontSize: 14, color: '#111', outline: 'none',
            boxSizing: 'border-box',
          }}
        />
      </div>

      {/* ── Table ──────────────────────────────────────────────────────── */}
      <div style={{ background: '#fff', borderRadius: 12, border: '1px solid #e0e0e0', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }}>
              {['Misafir', 'Oda', 'Giriş', 'Çıkış', 'Gece', 'Toplam', 'Durum', 'İşlem'].map((h) => (
                <th key={h} style={{ padding: '14px 16px', textAlign: h === 'İşlem' ? 'center' : 'left', color: '#666', fontSize: 13 }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => {
              const meta = STATUS_META[r.status];
              return (
                <tr key={r.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '14px 16px' }}>
                    <p style={{ margin: 0, fontWeight: 600, color: '#111', fontSize: 14 }}>{r.guest_name}</p>
                    <p style={{ margin: 0, color: '#888', fontSize: 12 }}>{r.guest_email}</p>
                  </td>
                  <td style={{ padding: '14px 16px', color: '#333', fontSize: 13 }}>{getRoomLabel(r.room_id)}</td>
                  <td style={{ padding: '14px 16px', color: '#555', fontSize: 13 }}>{r.check_in_date}</td>
                  <td style={{ padding: '14px 16px', color: '#555', fontSize: 13 }}>{r.check_out_date}</td>
                  <td style={{ padding: '14px 16px', color: '#333', fontSize: 13 }}>{r.total_nights}</td>
                  <td style={{ padding: '14px 16px', fontWeight: 700, color: '#059669', fontSize: 13 }}>
                    {r.total_price.toLocaleString('tr-TR')} ₺
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span style={{
                      padding: '4px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600,
                      color: meta.color, background: meta.bg,
                    }}>
                      {meta.label}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                    <div style={{ display: 'flex', gap: 6, justifyContent: 'center', flexWrap: 'wrap' }}>
                      <button onClick={() => setDetailModal(r)} style={smallBtn('#6366f1')}>Detay</button>
                      {(r.status === 'onaylandı' || r.status === 'beklemede') && (
                        <button onClick={() => handleCheckIn(r.id)} style={smallBtn('#10b981')}>Giriş</button>
                      )}
                      {r.status === 'giriş_yapıldı' && (
                        <button onClick={() => handleCheckOut(r.id)} style={smallBtn('#f59e0b')}>Çıkış</button>
                      )}
                      {!['çıkış_yapıldı', 'iptal_edildi'].includes(r.status) && (
                        <button onClick={() => handleCancel(r.id)} style={smallBtn('#ef4444')}>İptal</button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={8} style={{ padding: 48, textAlign: 'center', color: '#aaa' }}>
                  Rezervasyon bulunamadı
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* ── Create Modal ───────────────────────────────────────────────── */}
      {showModal && (
        <Overlay>
          <div style={modalCard(520)}>
            <h2 style={modalTitle}>Yeni Rezervasyon</h2>

            <form onSubmit={handleCreate}>
              {/* Room */}
              <Row label="Oda">
                <select
                  required
                  value={form.room_id}
                  onChange={(e) => setForm({ ...form, room_id: parseInt(e.target.value) })}
                  style={input}
                >
                  <option value={0}>Oda seçin</option>
                  {rooms
                    .filter((r) => !r.is_occupied)
                    .map((r) => (
                      <option key={r.id} value={r.id}>
                        Oda {r.room_number} — {r.room_type} ({r.capacity}) — {r.price_per_night.toLocaleString('tr-TR')} ₺/gece
                      </option>
                    ))}
                </select>
              </Row>

              {/* Dates */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <Row label="Giriş Tarihi">
                  <input
                    type="date"
                    required
                    min={today}
                    value={form.check_in_date}
                    onChange={(e) => setForm({ ...form, check_in_date: e.target.value })}
                    style={input}
                  />
                </Row>
                <Row label="Çıkış Tarihi">
                  <input
                    type="date"
                    required
                    min={form.check_in_date || today}
                    value={form.check_out_date}
                    onChange={(e) => setForm({ ...form, check_out_date: e.target.value })}
                    style={input}
                  />
                </Row>
              </div>

              {/* Availability result */}
              {checkingAvail && (
                <div style={infoBox('#dbeafe', '#1e40af')}>⏳ Müsaitlik kontrol ediliyor…</div>
              )}
              {availability && !checkingAvail && (
                <div style={infoBox('#d1fae5', '#065f46')}>
                  ✅ Müsait — {availability.total_nights} gece × {availability.price_per_night.toLocaleString('tr-TR')} ₺ = <strong>{availability.total_price.toLocaleString('tr-TR')} ₺</strong>
                </div>
              )}
              {error && <div style={infoBox('#fee2e2', '#991b1b')}>⚠ {error}</div>}

              {/* Guest info */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <Row label="Misafir Adı Soyadı">
                  <input required placeholder="Ad Soyad" value={form.guest_name}
                    onChange={(e) => setForm({ ...form, guest_name: e.target.value })} style={input} />
                </Row>
                <Row label="E-posta">
                  <input required type="email" placeholder="ornek@email.com" value={form.guest_email}
                    onChange={(e) => setForm({ ...form, guest_email: e.target.value })} style={input} />
                </Row>
                <Row label="Telefon">
                  <input placeholder="+90 5xx xxx xx xx" value={form.guest_phone}
                    onChange={(e) => setForm({ ...form, guest_phone: e.target.value })} style={input} />
                </Row>
                <Row label="TC / Pasaport No">
                  <input placeholder="Kimlik numarası" value={form.guest_id_number}
                    onChange={(e) => setForm({ ...form, guest_id_number: e.target.value })} style={input} />
                </Row>
                <Row label="Misafir Sayısı">
                  <input type="number" min={1} max={10} value={form.guest_count}
                    onChange={(e) => setForm({ ...form, guest_count: parseInt(e.target.value) })} style={input} />
                </Row>
              </div>

              <Row label="Özel İstekler">
                <textarea
                  rows={2}
                  placeholder="Erken check-in, ek yatak vb."
                  value={form.special_requests}
                  onChange={(e) => setForm({ ...form, special_requests: e.target.value })}
                  style={{ ...input, resize: 'none' }}
                />
              </Row>

              {/* Buttons */}
              <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
                <button type="button" onClick={() => setShowModal(false)} style={btn('#9ca3af', 1)}>İptal</button>
                <button
                  type="submit"
                  disabled={saving || !availability}
                  style={{ ...btn('#3b82f6', 1), opacity: (saving || !availability) ? .5 : 1 }}
                >
                  {saving ? 'Kaydediliyor…' : 'Rezervasyon Oluştur'}
                </button>
              </div>
            </form>
          </div>
        </Overlay>
      )}

      {/* ── Detail Modal ───────────────────────────────────────────────── */}
      {detailModal && (
        <Overlay>
          <div style={modalCard(480)}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: '#111' }}>
                Rezervasyon #{detailModal.id}
              </h2>
              <span style={{
                padding: '5px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600,
                color: STATUS_META[detailModal.status].color,
                background: STATUS_META[detailModal.status].bg,
              }}>
                {STATUS_META[detailModal.status].label}
              </span>
            </div>

            <DetailRow label="Oda" value={getRoomLabel(detailModal.room_id)} />
            {detailModal.capacity && <DetailRow label="Kapasite" value={detailModal.capacity} />}
            {detailModal.features && <DetailRow label="Özellikler" value={detailModal.features} />}
            <DetailRow label="Misafir" value={detailModal.guest_name} />
            <DetailRow label="E-posta" value={detailModal.guest_email} />
            <DetailRow label="Telefon" value={detailModal.guest_phone || '—'} />
            <DetailRow label="TC / Pasaport" value={detailModal.guest_id_number || '—'} />
            <DetailRow label="Kişi Sayısı" value={String(detailModal.guest_count)} />
            <DetailRow label="Giriş" value={detailModal.check_in_date} />
            <DetailRow label="Çıkış" value={detailModal.check_out_date} />
            <DetailRow label="Gece" value={String(detailModal.total_nights)} />
            <DetailRow label="Gece Fiyatı" value={`${detailModal.price_per_night.toLocaleString('tr-TR')} ₺`} />
            <DetailRow
              label="Toplam"
              value={`${detailModal.total_price.toLocaleString('tr-TR')} ₺`}
              highlight
            />
            {detailModal.special_requests && (
              <DetailRow label="Özel İstekler" value={detailModal.special_requests} />
            )}
            {detailModal.notes && <DetailRow label="Notlar" value={detailModal.notes} />}

            <div style={{ display: 'flex', gap: 10, marginTop: 24, flexWrap: 'wrap' }}>
              <button onClick={() => setDetailModal(null)} style={btn('#9ca3af')}>Kapat</button>
              <button onClick={() => handleDelete(detailModal.id)} style={btn('#ef4444')}>Sil</button>
            </div>
          </div>
        </Overlay>
      )}
    </div>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function Overlay({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,.55)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000, overflowY: 'auto', padding: 24,
    }}>
      {children}
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: 'block', marginBottom: 6, fontSize: 13, fontWeight: 500, color: '#444' }}>
        {label}
      </label>
      {children}
    </div>
  );
}

function DetailRow({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '9px 0', borderBottom: '1px solid #f0f0f0' }}>
      <span style={{ color: '#666', fontSize: 13 }}>{label}</span>
      <span style={{ fontWeight: highlight ? 700 : 500, color: highlight ? '#059669' : '#111', fontSize: 13 }}>
        {value}
      </span>
    </div>
  );
}

// ─── Style tokens ─────────────────────────────────────────────────────────────

const input: React.CSSProperties = {
  width: '100%', padding: '10px 12px', border: '1.5px solid #ddd',
  borderRadius: 8, fontSize: 14, color: '#111', outline: 'none',
  background: '#fafafa', boxSizing: 'border-box',
};

function btn(color: string, flex?: number): React.CSSProperties {
  return {
    flex: flex ?? undefined,
    padding: '10px 20px', background: color, color: '#fff',
    border: 'none', borderRadius: 8, cursor: 'pointer',
    fontSize: 14, fontWeight: 600,
  };
}

function smallBtn(color: string): React.CSSProperties {
  return {
    padding: '5px 10px', background: color, color: '#fff',
    border: 'none', borderRadius: 6, cursor: 'pointer',
    fontSize: 12, fontWeight: 600, whiteSpace: 'nowrap',
  };
}

function modalCard(w: number): React.CSSProperties {
  return {
    background: '#fff', borderRadius: 16, padding: 32,
    width: '100%', maxWidth: w, maxHeight: '90vh',
    overflowY: 'auto', border: '1px solid #e0e0e0',
  };
}

const modalTitle: React.CSSProperties = {
  margin: '0 0 24px', fontSize: 20, fontWeight: 700, color: '#111',
};

function infoBox(bg: string, color: string): React.CSSProperties {
  return {
    padding: '10px 14px', borderRadius: 8, marginBottom: 14,
    background: bg, color, fontSize: 13, fontWeight: 500,
  };
}
