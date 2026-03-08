import { useState, useEffect } from 'react';
import { maintenanceApi } from '../../api/maintenanceApi';
import { roomApi } from '../../api/roomApi';
import type { MaintenanceTicket, MaintenanceTicketCreate } from '../../types/maintenance';
import type { Room } from '../../types/room';

export default function MaintenancePage() {
  const [tickets, setTickets] = useState<MaintenanceTicket[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  const [formData, setFormData] = useState<MaintenanceTicketCreate>({
    room_id: 0,
    title: '',
    description: '',
    priority: 'orta',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [ticketsData, roomsData] = await Promise.all([
        maintenanceApi.getAllTickets(),
        roomApi.getRooms(),
      ]);
      setTickets(ticketsData);
      setRooms(roomsData);
    } catch (error) {
      console.error('Veriler yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await maintenanceApi.createTicket(formData);
      setShowModal(false);
      setFormData({ room_id: 0, title: '', description: '', priority: 'orta' });
      loadData();
    } catch (error) {
      console.error('Ticket oluşturulurken hata:', error);
    }
  };

  // FIX: updateTicket kullan (updateStatus backend'de yok)
  const handleStatusChange = async (ticketId: number, newStatus: string) => {
    try {
      await maintenanceApi.updateTicket(ticketId, { status: newStatus });
      loadData();
    } catch (error) {
      console.error('Durum güncellenirken hata:', error);
    }
  };

  // FIX: closeTicket kullan (completeTicket backend'de yok)
  const handleClose = async (ticketId: number) => {
    try {
      await maintenanceApi.closeTicket(ticketId);
      loadData();
    } catch (error) {
      console.error('Ticket kapatılırken hata:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'kritik': return '#ef4444';
      case 'orta': return '#f59e0b';
      case 'düşük': return '#10b981';
      default: return '#888';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'açık': return '#ef4444';
      case 'devam_ediyor': return '#f59e0b';
      case 'kapalı': return '#10b981';
      default: return '#888';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'açık': return 'Açık';
      case 'devam_ediyor': return 'Devam Ediyor';
      case 'kapalı': return 'Kapalı';
      default: return status;
    }
  };

  const filteredTickets = filter === 'all' ? tickets : tickets.filter(t => t.status === filter);

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center', paddingTop: '100px', color: '#666' }}>
        Yükleniyor...
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111' }}>🛠️ Teknik Servis</h1>
        <button
          onClick={() => setShowModal(true)}
          style={{ padding: '12px 24px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' }}
        >
          + Yeni Arıza Bildirimi
        </button>
      </div>

      {/* Filtreler */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        {['all', 'açık', 'devam_ediyor', 'kapalı'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            style={{
              padding: '8px 16px',
              backgroundColor: filter === status ? '#3b82f6' : '#f0f0f0',
              color: filter === status ? 'white' : '#333',
              border: '1px solid #ddd',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            {status === 'all' ? 'Tümü' : getStatusLabel(status)}
          </button>
        ))}
      </div>

      {/* Ticket Listesi */}
      <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', overflow: 'hidden', border: '1px solid #e0e0e0' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }}>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Oda</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Başlık</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Öncelik</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Durum</th>
              <th style={{ padding: '16px', textAlign: 'center', color: '#666' }}>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {filteredTickets.map((ticket) => (
              <tr key={ticket.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '16px', color: '#333' }}>
                  {rooms.find(r => r.id === ticket.room_id)?.room_number ?? `#${ticket.room_id}`}
                </td>
                <td style={{ padding: '16px', color: '#333' }}>{ticket.title}</td>
                <td style={{ padding: '16px' }}>
                  <span style={{
                    padding: '4px 12px', borderRadius: '20px', fontSize: '12px',
                    backgroundColor: `${getPriorityColor(ticket.priority)}20`,
                    color: getPriorityColor(ticket.priority),
                  }}>
                    {ticket.priority}
                  </span>
                </td>
                <td style={{ padding: '16px' }}>
                  <span style={{
                    padding: '4px 12px', borderRadius: '20px', fontSize: '12px',
                    backgroundColor: `${getStatusColor(ticket.status)}20`,
                    color: getStatusColor(ticket.status),
                  }}>
                    {getStatusLabel(ticket.status)}
                  </span>
                </td>
                <td style={{ padding: '16px', textAlign: 'center' }}>
                  {ticket.status !== 'kapalı' && (
                    <>
                      {ticket.status === 'açık' && (
                        <button
                          onClick={() => handleStatusChange(ticket.id, 'devam_ediyor')}
                          style={{ marginRight: '8px', padding: '8px 12px', backgroundColor: '#f59e0b', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}
                        >
                          Alındı
                        </button>
                      )}
                      <button
                        onClick={() => handleClose(ticket.id)}
                        style={{ padding: '8px 12px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}
                      >
                        Kapat
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
            {filteredTickets.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
                  Arıza bildirimi bulunamadı
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: '#ffffff', padding: '32px', borderRadius: '16px', width: '450px', border: '1px solid #e0e0e0' }}>
            <h2 style={{ marginBottom: '24px', fontSize: '20px', fontWeight: 'bold', color: '#111' }}>Yeni Arıza Bildirimi</h2>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#333' }}>Oda</label>
                <select
                  value={formData.room_id}
                  onChange={(e) => setFormData({ ...formData, room_id: parseInt(e.target.value) })}
                  required
                  style={{ width: '100%', padding: '12px', backgroundColor: '#f5f5f5', border: '1px solid #ccc', borderRadius: '8px', color: '#111' }}
                >
                  <option value={0}>Oda seçin</option>
                  {rooms.map((room) => (
                    <option key={room.id} value={room.id}>Oda {room.room_number}</option>
                  ))}
                </select>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#333' }}>Başlık</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Arıza başlığı"
                  required
                  style={{ width: '100%', padding: '12px', backgroundColor: '#f5f5f5', border: '1px solid #ccc', borderRadius: '8px', color: '#111' }}
                />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#333' }}>Açıklama</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Arıza açıklaması"
                  rows={3}
                  required
                  style={{ width: '100%', padding: '12px', backgroundColor: '#f5f5f5', border: '1px solid #ccc', borderRadius: '8px', color: '#111', resize: 'none' }}
                />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#333' }}>Öncelik</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  style={{ width: '100%', padding: '12px', backgroundColor: '#f5f5f5', border: '1px solid #ccc', borderRadius: '8px', color: '#111' }}
                >
                  <option value="düşük">Düşük</option>
                  <option value="orta">Orta</option>
                  <option value="kritik">Kritik</option>
                </select>
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