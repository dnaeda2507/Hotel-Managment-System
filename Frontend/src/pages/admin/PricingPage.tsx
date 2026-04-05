import { useState, useEffect } from 'react';
import { pricingApi } from '../../api/pricingApi';
import type { RoomPricing, RoomPricingCreate } from '../../types/pricing';

export default function PricingPage() {
  const [prices, setPrices] = useState<RoomPricing[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPrice, setEditingPrice] = useState<RoomPricing | null>(null);
  
  const [formData, setFormData] = useState<RoomPricingCreate>({
    room_type: 'Standard',
    capacity: '2 kişilik',
    price_per_night: 0,
    is_active: true,
  });

  useEffect(() => {
    loadPrices();
  }, []);

  const loadPrices = async () => {
    try {
      setLoading(true);
      const data = await pricingApi.getAllPrices();
      setPrices(data);
    } catch (error) {
      console.error('Fiyatlar yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingPrice) {
        await pricingApi.updatePrice(editingPrice.id, formData);
      } else {
        await pricingApi.createPrice(formData);
      }
      setShowModal(false);
      setEditingPrice(null);
      setFormData({
        room_type: 'Standard',
        capacity: '2 kişilik',
        price_per_night: 0,
        is_active: true,
      });
      loadPrices();
    } catch (error) {
      console.error('Fiyat kaydedilirken hata:', error);
    }
  };

  const handleEdit = (price: RoomPricing) => {
    setEditingPrice(price);
    setFormData({
      room_type: price.room_type,
      capacity: price.capacity,
      price_per_night: price.price_per_night,
      is_active: price.is_active,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Bu fiyatı silmek istediğinizden emin misiniz?')) {
      try {
        await pricingApi.deletePrice(id);
        loadPrices();
      } catch (error) {
        console.error('Fiyat silinirken hata:', error);
      }
    }
  };

  const handleToggleActive = async (price: RoomPricing) => {
    try {
      await pricingApi.toggleActive(price.id);
      loadPrices();
    } catch (error) {
      console.error('Fiyat durumu değiştirilirken hata:', error);
    }
  };

  const roomTypes = ['Standard', 'Deluxe', 'Suite'];
  const capacities = ['1 kişilik', '2 kişilik', '2+1 kişilik', '3 kişilik', '3+1 kişilik', '4 kişilik'];

  if (loading) {
    return (
      <div style={{ padding: '100px 24px 24px 24px', textAlign: 'center' }}>
        <div style={{ color: '#666' }}>Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111' }}>💰 Fiyatlandırma Yönetimi</h1>
        <button
          onClick={() => {
            setEditingPrice(null);
            setFormData({
              room_type: 'Standard',
              capacity: '2 kişilik',
              price_per_night: 0,
              is_active: true,
            });
            setShowModal(true);
          }}
          style={{
            padding: '12px 24px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600',
          }}
        >
          + Yeni Fiyat Ekle
        </button>
      </div>

      <div style={{ 
        backgroundColor: '#ffffff', 
        borderRadius: '12px', 
        overflow: 'hidden',
        border: '1px solid #e0e0e0'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }}>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Oda Tipi</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#666' }}>Kapasite</th>
              <th style={{ padding: '16px', textAlign: 'right', color: '#666' }}>Fiyat (₺)</th>
              <th style={{ padding: '16px', textAlign: 'center', color: '#666' }}>Durum</th>
              <th style={{ padding: '16px', textAlign: 'center', color: '#666' }}>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {prices.map((price) => (
              <tr key={price.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '16px', color: '#333' }}>{price.room_type}</td>
                <td style={{ padding: '16px', color: '#333' }}>{price.capacity}</td>
                <td style={{ padding: '16px', textAlign: 'right', fontWeight: 'bold', color: '#10b981' }}>
                  {price.price_per_night.toLocaleString('tr-TR')} ₺
                </td>
                <td style={{ padding: '16px', textAlign: 'center' }}>
                  <span
                    onClick={() => handleToggleActive(price)}
                    style={{
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      cursor: 'pointer',
                      backgroundColor: price.is_active ? '#d1fae5' : '#fee2e2',
                      color: price.is_active ? '#059669' : '#dc2626',
                    }}
                  >
                    {price.is_active ? 'Aktif' : 'Pasif'}
                  </span>
                </td>
                <td style={{ padding: '16px', textAlign: 'center' }}>
                  <button
                    onClick={() => handleEdit(price)}
                    style={{ marginRight: '8px', padding: '8px 16px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                  >
                    Düzenle
                  </button>
                  <button
                    onClick={() => handleDelete(price.id)}
                    style={{ padding: '8px 16px', backgroundColor: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                  >
                    Sil
                  </button>
                </td>
              </tr>
            ))}
            {prices.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
                  Henüz fiyat tanımlanmamış
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: '#ffffff',
            padding: '32px',
            borderRadius: '16px',
            width: '400px',
            border: '1px solid #e0e0e0',
          }}>
            <h2 style={{ marginBottom: '24px', fontSize: '20px', fontWeight: 'bold', color: '#111' }}>
              {editingPrice ? 'Fiyat Düzenle' : 'Yeni Fiyat Ekle'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#333' }}>Oda Tipi</label>
                <select
                  value={formData.room_type}
                  onChange={(e) => setFormData({ ...formData, room_type: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '12px',
                    backgroundColor: '#f5f5f5',
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                    color: '#111',
                  }}
                >
                  {roomTypes.map((type) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#333' }}>Kapasite</label>
                <select
                  value={formData.capacity}
                  onChange={(e) => setFormData({ ...formData, capacity: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '12px',
                    backgroundColor: '#f5f5f5',
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                    color: '#111',
                  }}
                >
                  {capacities.map((cap) => (
                    <option key={cap} value={cap}>{cap}</option>
                  ))}
                </select>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', color: '#333' }}>Fiyat (₺)</label>
                <input
                  type="number"
                  value={formData.price_per_night}
                  onChange={(e) => setFormData({ ...formData, price_per_night: parseFloat(e.target.value) })}
                  style={{
                    width: '100%',
                    padding: '12px',
                    backgroundColor: '#f5f5f5',
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                    color: '#111',
                  }}
                />
              </div>
              <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: '#e0e0e0',
                    color: '#333',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                  }}
                >
                  İptal
                </button>
                <button
                  type="submit"
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                  }}
                >
                  {editingPrice ? 'Güncelle' : 'Ekle'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
