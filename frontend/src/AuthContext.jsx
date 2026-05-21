import { createContext, useContext, useState, useEffect } from 'react';
import api from './api';

const AuthContext = createContext(null);

const isDoctorPort = window.location.port === '5174';
const storagePrefix = isDoctorPort ? 'doctor_' : 'patient_';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore user from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(`${storagePrefix}user`);
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem(`${storagePrefix}user`);
        localStorage.removeItem(`${storagePrefix}token`);
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const data = res.data;
    const userData = {
      id: data.user_id,
      role: data.role,
      full_name: data.full_name,
      is_approved: data.is_approved,
      preferred_language: data.preferred_language,
    };
    localStorage.setItem(`${storagePrefix}token`, data.access_token);
    localStorage.setItem(`${storagePrefix}refresh_token`, data.refresh_token);
    localStorage.setItem(`${storagePrefix}user`, JSON.stringify(userData));
    setUser(userData);
    return userData;
  };

  const register = async (payload) => {
    const res = await api.post('/auth/register', payload);
    const data = res.data;
    const userData = {
      id: data.user_id,
      role: data.role,
      full_name: data.full_name,
      is_approved: data.is_approved,
    };
    localStorage.setItem(`${storagePrefix}token`, data.access_token);
    localStorage.setItem(`${storagePrefix}refresh_token`, data.refresh_token);
    localStorage.setItem(`${storagePrefix}user`, JSON.stringify(userData));
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch {
      // Ignore logout errors
    }
    localStorage.removeItem(`${storagePrefix}token`);
    localStorage.removeItem(`${storagePrefix}refresh_token`);
    localStorage.removeItem(`${storagePrefix}user`);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
