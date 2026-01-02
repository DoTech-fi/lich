/**
 * API Client for {{ cookiecutter.project_name }}
 * Type-safe HTTP client for backend API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

class ApiClientError extends Error {
  constructor(
    public statusCode: number,
    public error: ApiError,
  ) {
    super(error.message);
    this.name = 'ApiClientError';
  }
}

/**
 * Get auth token from storage
 * Uses sessionStorage for security (not localStorage!)
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return sessionStorage.getItem('access_token');
}

/**
 * Make API request with auth headers
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { params, ...fetchOptions } = options;
  
  // Build URL with query params
  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }
  
  // Add auth header
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      error: { code: 'UNKNOWN', message: 'An error occurred' }
    }));
    throw new ApiClientError(response.status, errorData.error);
  }
  
  // Handle empty responses
  const text = await response.text();
  if (!text) return {} as T;
  
  return JSON.parse(text);
}

// ============================================
// Auth API
// ============================================

{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username?: string;
  first_name?: string;
  last_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  status: string;
  is_verified: boolean;
  avatar_url: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface LoginResponse {
  user: UserResponse;
  tokens: TokenResponse;
}

export const authApi = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiRequest<LoginResponse>('/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    // Store tokens
    sessionStorage.setItem('access_token', response.tokens.access_token);
    sessionStorage.setItem('refresh_token', response.tokens.refresh_token);
    
    return response;
  },
  
  async register(data: RegisterRequest): Promise<UserResponse> {
    return apiRequest<UserResponse>('/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  async refreshToken(): Promise<TokenResponse> {
    const refreshToken = sessionStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token');
    
    const response = await apiRequest<TokenResponse>('/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    
    sessionStorage.setItem('access_token', response.access_token);
    sessionStorage.setItem('refresh_token', response.refresh_token);
    
    return response;
  },
  
  async logout(): Promise<void> {
    await apiRequest('/v1/auth/logout', { method: 'POST' });
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
  },
  
  async getMe(): Promise<UserResponse> {
    return apiRequest<UserResponse>('/v1/auth/me');
  },
};

{%- elif cookiecutter.auth_strategy == 'keycloak' %}

export interface AuthConfig {
  keycloak_url: string;
  realm: string;
  client_id: string;
}

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  status: string;
  is_verified: boolean;
  avatar_url: string | null;
  created_at: string;
  updated_at: string | null;
}

export const authApi = {
  async getConfig(): Promise<AuthConfig> {
    return apiRequest<AuthConfig>('/v1/auth/config');
  },
  
  async getMe(): Promise<UserResponse> {
    return apiRequest<UserResponse>('/v1/auth/me');
  },
  
  async logout(): Promise<void> {
    await apiRequest('/v1/auth/logout', { method: 'POST' });
    sessionStorage.removeItem('access_token');
  },
};

{%- else %}

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  status: string;
  is_verified: boolean;
  avatar_url: string | null;
  created_at: string;
  updated_at: string | null;
}

export const authApi = {};

{%- endif %}

// ============================================
// Users API
// ============================================

export interface UpdateUserRequest {
  first_name?: string;
  last_name?: string;
  username?: string;
  avatar_url?: string;
}

export interface UserListResponse {
  items: UserResponse[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export const usersApi = {
  async getMe(): Promise<UserResponse> {
    return apiRequest<UserResponse>('/v1/users/me');
  },
  
  async updateMe(data: UpdateUserRequest): Promise<UserResponse> {
    return apiRequest<UserResponse>('/v1/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
  
  // Admin endpoints
  async list(page = 1, pageSize = 20): Promise<UserListResponse> {
    return apiRequest<UserListResponse>('/v1/users', {
      params: { page: String(page), page_size: String(pageSize) },
    });
  },
  
  async getById(id: string): Promise<UserResponse> {
    return apiRequest<UserResponse>(`/v1/users/${id}`);
  },
  
  async activate(id: string): Promise<UserResponse> {
    return apiRequest<UserResponse>(`/v1/users/${id}/activate`, {
      method: 'POST',
    });
  },
  
  async suspend(id: string): Promise<UserResponse> {
    return apiRequest<UserResponse>(`/v1/users/${id}/suspend`, {
      method: 'POST',
    });
  },
  
  async delete(id: string): Promise<void> {
    await apiRequest(`/v1/users/${id}`, { method: 'DELETE' });
  },
};

// ============================================
// Health API
// ============================================

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export const healthApi = {
  async check(): Promise<HealthResponse> {
    return apiRequest<HealthResponse>('/health');
  },
  
  async ready(): Promise<HealthResponse> {
    return apiRequest<HealthResponse>('/ready');
  },
};

// Export everything
export { ApiClientError, getAuthToken };
export default { authApi, usersApi, healthApi };
