import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/authApi';
import type { User, LoginRequest, RegisterRequest } from '../types/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Sayfa yenilenince token varsa kullanıcıyı geri yükle
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setIsLoading(false);
      return;
    }
    authApi
      .me()
      .then((u) => setUser(u))
      .catch(() => localStorage.removeItem('token'))
      .finally(() => setIsLoading(false));
  }, []);

  const redirectByRole = useCallback(
    (role: string) => {
      if (role === 'moderator') {
        navigate('/admin/dashboard', { replace: true });
      } else {
        navigate('/user/dashboard', { replace: true });
      }
    },
    [navigate]
  );

  const login = useCallback(
    async (data: LoginRequest) => {
      try {
        const res = await authApi.login(data);
        localStorage.setItem('token', res.access_token);
        setUser(res.user);
        redirectByRole(res.user.role);
      } catch (error: any) {
        // Handle timeout or network errors
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          throw new Error('Connection timeout. Please check if the server is running.');
        }
        if (!error.response) {
          throw new Error('Network error. Please check your connection.');
        }
        throw error;
      }
    },
    [redirectByRole]
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      try {
        // Register → direkt login yap
        await authApi.register(data);
        const res = await authApi.login(data);
        localStorage.setItem('token', res.access_token);
        setUser(res.user);
        redirectByRole(res.user.role);
      } catch (error: any) {
        // Handle timeout or network errors
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          throw new Error('Connection timeout. Please check if the server is running.');
        }
        if (!error.response) {
          throw new Error('Network error. Please check your connection.');
        }
        throw error;
      }
    },
    [redirectByRole]
  );

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/login', { replace: true });
  }, [navigate]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}

