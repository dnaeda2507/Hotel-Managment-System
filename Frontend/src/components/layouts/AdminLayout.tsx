
import { type ReactNode } from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from '../common/Sidebar';
import Header from '../common/Header';

interface LayoutProps {
  children: ReactNode;
}

// FIX: Route'a göre dinamik başlık
const PAGE_TITLES: Record<string, string> = {
  '/admin/dashboard': 'Genel Bakış',
  '/admin/rooms': 'Oda Yönetimi',
  '/admin/pricing': 'Fiyatlandırma',
  '/admin/maintenance': 'Teknik Servis',
  '/admin/housekeeping': 'Temizlik Yönetimi',
  '/admin/bookings': 'Rezervasyonlar',
  '/admin/lost-found': 'Kayıp Eşyalar',
  '/admin/guests': 'Misafir Listesi',
};

export default function AdminLayout({ children }: LayoutProps) {
  const location = useLocation();
  const title = PAGE_TITLES[location.pathname] ?? 'Yönetim Paneli';

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* FIX: Dinamik başlık */}
        <Header title={title} />
        <main style={{ padding: '30px', color: '#111' }}>
          {children}
        </main>
      </div>
    </div>
  );
}