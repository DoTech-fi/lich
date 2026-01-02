'use client';

/**
 * Auth Context for {{ cookiecutter.project_name }}
 * Handles authentication state across the app
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
import { authApi, usersApi, UserResponse, LoginRequest, RegisterRequest } from '@/lib/api-client';
{%- elif cookiecutter.auth_strategy == 'keycloak' %}
import { authApi, usersApi, UserResponse } from '@/lib/api-client';
{%- else %}
import { UserResponse } from '@/lib/api-client';
{%- endif %}

interface AuthContextType {
  user: UserResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  {%- endif %}
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await usersApi.getMe();
      setUser(userData);
    } catch {
      setUser(null);
    }
  }, []);

  // Check auth on mount
  useEffect(() => {
    const checkAuth = async () => {
      {%- if cookiecutter.auth_strategy != 'none' %}
      const token = sessionStorage.getItem('access_token');
      if (token) {
        await refreshUser();
      }
      {%- endif %}
      setIsLoading(false);
    };
    
    checkAuth();
  }, [refreshUser]);

  {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
  const login = async (data: LoginRequest) => {
    const response = await authApi.login(data);
    setUser(response.user);
  };

  const register = async (data: RegisterRequest) => {
    await authApi.register(data);
  };
  {%- endif %}

  const logout = async () => {
    {%- if cookiecutter.auth_strategy != 'none' %}
    try {
      await authApi.logout();
    } finally {
      setUser(null);
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
    }
    {%- else %}
    setUser(null);
    {%- endif %}
  };

  return (
    <AuthContext.Provider
      value={% raw %}{{{% endraw %}
        user,
        isLoading,
        isAuthenticated: !!user,
        {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
        login,
        register,
        {%- endif %}
        logout,
        refreshUser,
      {% raw %}}}{% endraw %}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// HOC for protected routes
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
) {
  return function ProtectedComponent(props: P) {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
      return (
        <div style={% raw %}{{{% endraw %} display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' {% raw %}}}{% endraw %}>
          <div>{% if cookiecutter.default_language == 'fa' %}در حال بارگذاری...{% else %}Loading...{% endif %}</div>
        </div>
      );
    }

    if (!isAuthenticated) {
      // Redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      return null;
    }

    return <Component {...props} />;
  };
}
