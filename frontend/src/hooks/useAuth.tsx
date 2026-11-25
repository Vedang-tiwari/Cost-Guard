import React, { createContext, useContext, useEffect, useState } from 'react';
import { api, clearStoredAuth, getStoredAuth, setStoredAuth } from '../services/api';
import type { UserProfile } from '../types';

interface AuthContextValue {
  isAuthenticated: boolean;
  isLoading: boolean;
  authMode: 'jwt' | 'apikey';
  user: UserProfile | null;
  loginWithCredentials: (email: string, password: string) => Promise<void>;
  registerAccount: (payload: {
    email: string;
    password: string;
    full_name: string;
    organization_name: string;
  }) => Promise<string | null>;
  loginWithApiKey: (apiKey: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [authMode, setAuthMode] = useState<'jwt' | 'apikey'>('jwt');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const init = async () => {
      const { token, mode } = getStoredAuth();
      if (!token) {
        setIsLoading(false);
        return;
      }

      setAuthMode(mode);
      try {
        if (mode === 'jwt') {
          const profile = await api.me();
          setUser(profile);
          setIsAuthenticated(true);
        } else {
          // Verify API key against applications list
          const apps = await api.getApplications();
          setUser({
            id: 'apikey-session',
            email: 'api-client@workspace',
            full_name: apps[0]?.name || 'API Key Session',
            organization_id: apps[0]?.organization_id || null,
            organization_name: 'Connected via API Key',
            created_at: new Date().toISOString(),
          });
          setIsAuthenticated(true);
        }
      } catch {
        clearStoredAuth();
        setIsAuthenticated(false);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    init();
  }, []);

  const loginWithCredentials = async (email: string, password: string) => {
    const res = await api.login(email, password);
    setStoredAuth(res.access_token, 'jwt');
    setAuthMode('jwt');
    setUser(res.user);
    setIsAuthenticated(true);
  };

  const registerAccount = async (payload: {
    email: string;
    password: string;
    full_name: string;
    organization_name: string;
  }) => {
    const res = await api.register(payload);
    setStoredAuth(res.access_token, 'jwt');
    setAuthMode('jwt');
    setUser(res.user);
    setIsAuthenticated(true);
    return res.default_api_key || null;
  };

  const loginWithApiKey = async (apiKey: string) => {
    setStoredAuth(apiKey.trim(), 'apikey');
    setAuthMode('apikey');
    try {
      const apps = await api.getApplications();
      setUser({
        id: 'apikey-session',
        email: 'api-client@workspace',
        full_name: apps[0]?.name || 'API Key Session',
        organization_id: apps[0]?.organization_id || null,
        organization_name: 'Connected via API Key',
        created_at: new Date().toISOString(),
      });
      setIsAuthenticated(true);
    } catch (err) {
      clearStoredAuth();
      setIsAuthenticated(false);
      throw err;
    }
  };

  const logout = () => {
    clearStoredAuth();
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        authMode,
        user,
        loginWithCredentials,
        registerAccount,
        loginWithApiKey,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return ctx;
}
