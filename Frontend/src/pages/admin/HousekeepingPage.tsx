import { useState, useEffect } from 'react';
import { housekeepingApi } from '../../api/housekeepingApi';
import { roomApi } from '../../api/roomApi';
import type { HousekeepingTask, HousekeepingStatus } from '../../types/housekeeping';
import type { Room } from '../../types/room';

const STATUS_LABELS: Record<HousekeepingStatus, string> = {
  beklemede: 'Beklemede',
  temizleniyor: 'Temizleniyor',
  temiz: 'Temiz',
  onayli: 'Onaylı',
};

const STATUS_COLORS: Record<HousekeepingStatus, string> = {
  beklemede: '#ef4444',
  temizleniyor: '#f59e0b',
  temiz: '#10b981',
  onayli: '#3b82f6',
};

export default function HousekeepingPage() {
  const [tasks, setTasks] = useState<HousekeepingTask[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [showModal, setShowModal] = useState(false);
  const [selectedRoomId, setSelectedRoomId] = useState<number>(0);
  const [notes, setNotes] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tasksData, roomsData] = await Promise.all([
        housekeepingApi.getAllTasks(),
        roomApi.getRooms(),
      ]);
      setTasks(tasksData);
      setRooms(roomsData);
    } catch (error) {
      console.error('Veriler yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRoomNumber = (roomId: number) =>
    rooms.find(r => r.id === roomId)?.room_number ?? `#${roomId}`;

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRoomId) return;
    try {
      await housekeepingApi.createTaskForRoom(selectedRoomId, notes);
      setShowModal(false);
      setSelectedRoomId(0);
      setNotes('');
      loadData();
    } catch (error) {
      console.error('Görev oluşturulurken hata:', error);
      alert('Bu oda için zaten aktif bir görev var.');
    }
  };

  const handleStatusChange = async (taskId: number, status: string) => {
    try {
      await housekeepingApi.updateStatus(taskId, status);
      loadData();
    } catch (error) {
      console.error('Durum güncellenirken hata:', error);
    }
  };

  const handleApprove = async (taskId: number) => {
    try {
      await housekeepingApi.approveTask(taskId);
      loadData();
    } catch (error) {
      console.error('Görev onaylanırken hata:', error);
    }
  };

  const handleComplete = async (taskId: number) => {
    try {
      await housekeepingApi.completeCleaning(taskId);
      loadData();
    } catch (error) {
      console.error('Görev tamamlanırken hata:', error);
    }
  };

  const handleDelete = async (taskId: number) => {
    if (!confirm('Bu görevi silmek istediğinizden emin misiniz?')) return;
    try {
      await housekeepingApi.deleteTask(taskId);
      loadData();
    } catch (error) {
      console.error('Görev silinirken hata:', error);
    }
  };

  const filteredTasks = filter === 'all' ? tasks : tasks.filter(t => t.status === filter);

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center', paddingTop: '100px', color: '#666' }}>
        Yükleniyor...
      </div>
    );
  }

  // İstatistik kartları için sayılar
  const counts = {
    beklemede: tasks.filter(t => t.status === 'beklemede').length,
    temizleniyor: tasks.filter(t => t.status === 'temizleniyor').length,
    temiz: tasks.filter(t => t.status === 'temiz').length,
    onayli: tasks.filter(t => t.status === 'onayli').length,
  };

  return (
    <div style={{ padding: '24px' }}>

      {/* Başlık */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111' }}>🧹 Temizlik Yönetimi</h1>
        <button
          onClick={() => setShowModal(true)}
          style={{ padding: '12px 24px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' }}
        >
          + Yeni Görev Oluştur
        </button>
      </div>

      {/*İstatistik kartları */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        {(Object.entries(counts) as [HousekeepingStatus, number][]).map(([status, count]) => (
          <div key={status} style={{ backgroundColor: '#ffffff', padding: '20px', borderRadius: '12px', border: '1px solid #e0e0e0', cursor: 'pointer' }}
            onClick={() => setFilter(filter === status ? 'all' : status)}
          >
            <p style={{ color: '#666', margin: 0, fontSize: '13px' }}>{STATUS_LABELS[status]}</p>
            <h2 style={{ color: STATUS_COLORS[status], margin: '8px 0 0', fontSize: '28px' }}>{count}</h2>
          </div>
        ))}
      </div>

      {/* Filtreler */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        {(['all', 'beklemede', 'temizleniyor', 'temiz', 'onayli'] as const).map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            style={{
              padding: '8px 16px',
              backgroundColor: filter === s ? '#3b82f6' : '#f0f0f0',
              color: filter === s ? 'white' : '#333', border: '1px solid #ddd', borderRadius: '8px', cursor: 'pointer',
            }}
          >
            {s === 'all' ? 'Tümü' : STATUS_LABELS[s]}
          </button>
        ))}
      </div>

      {/* Görev listesi */}
      <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', overflow: 'hidden', border: '1px solid #e0e0e0' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }}>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Oda</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Not</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Durum</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Oluşturulma</th>
              <th style={{ padding: '16px', textAlign: 'center', color: '#666' }}>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {filteredTasks.map((task) => (
              <tr key={task.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '16px', fontWeight: 'bold', color: '#333' }}>
                  Oda {getRoomNumber(task.room_id)}
                </td>
                <td style={{ padding: '16px', color: '#666', fontSize: '13px' }}>
                  {task.notes || '—'}
                </td>
                <td style={{ padding: '16px' }}>
                  <span style={{
                    padding: '4px 12px', borderRadius: '20px', fontSize: '12px',
                    backgroundColor: `${STATUS_COLORS[task.status]}20`,
                    color: STATUS_COLORS[task.status],
                  }}>
                    {STATUS_LABELS[task.status]}
                  </span>
                </td>
                <td style={{ padding: '16px', color: '#666', fontSize: '13px' }}>
                  {new Date(task.created_at).toLocaleDateString('tr-TR')}
                </td>
                <td style={{ padding: '16px', textAlign: 'center', display: 'flex', gap: '6px', justifyContent: 'center' }}>
                  {task.status === 'beklemede' && (
                    <button
                      onClick={() => handleStatusChange(task.id, 'temizleniyor')}
                      style={{ padding: '7px 10px', backgroundColor: '#f59e0b', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}
                    >
                      Başlat
                    </button>
                  )}
                  {task.status === 'temizleniyor' && (
                    <button
                      onClick={() => handleComplete(task.id)}
                      style={{ padding: '7px 10px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}
                    >
                      Tamamla
                    </button>
                  )}
                  {task.status === 'temiz' && (
                    <button
                      onClick={() => handleApprove(task.id)}
                      style={{ padding: '7px 10px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}
                    >
                      Onayla
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(task.id)}
                    style={{ padding: '7px 10px', backgroundColor: '#fee2e2', color: '#dc2626', border: '1px solid #fecaca', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}
                  >
                    Sil
                  </button>
                </td>
              </tr>
            ))}
            {filteredTasks.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
                  Görev bulunamadı
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: '#ffffff', padding: '32px', borderRadius: '16px', width: '400px', border: '1px solid #e0e0e0' }}>
            <h2 style={{ marginBottom: '24px', fontSize: '20px', fontWeight: 'bold', color: '#111' }}>Yeni Temizlik Görevi</h2>
            <form onSubmit={handleCreateTask}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#333' }}>Oda</label>
                <select
                  value={selectedRoomId}
                  onChange={(e) => setSelectedRoomId(parseInt(e.target.value))}
                  required
                  style={{ width: '100%', padding: '12px', backgroundColor: '#f5f5f5', border: '1px solid #ccc', borderRadius: '8px', color: '#111' }}
                >
                  <option value={0}>Oda seçin</option>
                  {rooms.map((room) => (
                    <option key={room.id} value={room.id}>
                      Oda {room.room_number} — {room.room_type}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#333' }}>Not (opsiyonel)</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Örn: Checkout sonrası temizlik"
                  rows={3}
                  style={{ width: '100%', padding: '12px', backgroundColor: '#f5f5f5', border: '1px solid #ccc', borderRadius: '8px', color: '#111', resize: 'none' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ flex: 1, padding: '12px', backgroundColor: '#e0e0e0', color: '#333', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                  İptal
                </button>
                <button type="submit" style={{ flex: 1, padding: '12px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                  Oluştur
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
