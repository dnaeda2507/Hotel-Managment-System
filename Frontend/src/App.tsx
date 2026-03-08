import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';
import RoomsPage from './pages/RoomsPage';
import AboutPage from './pages/AboutPage';
import RoomDashboard from './pages/admin/RoomDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';
import MaintenancePage from './pages/admin/MaintenancePage';
import PricingPage from './pages/admin/PricingPage';
import HousekeepingPage from './pages/admin/HousekeepingPage';

import AdminLayout from './components/layouts/AdminLayout';

function UserDashboard() {
  return <div style={{ color: '#111', padding: 40, backgroundColor: '#f5f5f5', minHeight: '100vh' }}>User Dashboard — yapım aşamasında</div>;
}

function AppRoutes() {
  return (
    <Routes>
      {/* 1. PUBLIC ROUTES */}
      <Route path="/" element={<HomePage />} />
      <Route path="/home" element={<HomePage />} />
      <Route path="/rooms" element={<RoomsPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

       {/* ADMIN (MODERATOR) ROUTES */}
      <Route
        path="/admin/*"
        element={
          <ProtectedRoute allowedRole="moderator">
            <AdminLayout>
              <Routes>
                <Route path="dashboard" element={<AdminDashboard />} />
                <Route path="rooms" element={<RoomDashboard />} />
                <Route path="maintenance" element={<MaintenancePage />} />
                <Route path="pricing" element={<PricingPage />} />
                <Route path="housekeeping" element={<HousekeepingPage />} />
                <Route path="bookings" element={<div style={{ color: '#111' }}>Rezervasyonlar (Yakında)</div>} />
                <Route path="lost-found" element={<div style={{ color: '#111' }}>Kayıp Eşyalar (Yakında)</div>} />
                <Route path="guests" element={<div style={{ color: '#111' }}>Misafir Listesi (Yakında)</div>} />
                <Route path="*" element={<Navigate to="dashboard" replace />} />
              </Routes>
            </AdminLayout>
          </ProtectedRoute>
        }
      />


      {/* 3. GUEST ROUTES */}
      <Route
        path="/user/dashboard"
        element={
          <ProtectedRoute allowedRole="user">
            <UserDashboard />
          </ProtectedRoute>
        }
      />

      {/* 4. DEFAULT REDIRECTS */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}







     
     
     
