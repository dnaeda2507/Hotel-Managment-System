
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import type { UserRole } from '../../types/auth';

interface Props {
  children: React.ReactNode;
  allowedRole: UserRole;
}

export function ProtectedRoute({ children, allowedRole }: Props) {
  const { user, isLoading, isAuthenticated } = useAuth();

  if (isLoading) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#0f0f14',
        color: '#555',
        fontSize: '14px',
      }}>
        Yükleniyor...
      </div>
    );
  }

  // Giriş yapmamış → login'e gönder
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  // Yanlış role → kendi dashboard'ına gönder
  if (user.role !== allowedRole) {
    return <Navigate to={`/${user.role === 'moderator' ? 'admin' : 'user'}/dashboard`} replace />;
  }

  return <>{children}</>;
}