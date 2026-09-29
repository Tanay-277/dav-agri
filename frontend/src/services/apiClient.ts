const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  code: string;
  details?: any;

  constructor(message: string, code: string = 'API_ERROR', details?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit & { timeoutMs?: number } = {}
): Promise<T> {
  const token = localStorage.getItem('dav_auth_token');
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Authoritative language propagation for all API requests
  const lang = (typeof window !== 'undefined' ? localStorage.getItem('dav_language') : null) || 'mr';
  if (!headers['Accept-Language']) {
    headers['Accept-Language'] = lang;
  }

  // Don't set Content-Type if uploading FormData (browser handles boundary automatically)
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const url = `${API_BASE_URL}${endpoint}`;

  // Configurable timeout via AbortController
  const controller = new AbortController();
  const timeoutMs = options.timeoutMs || 15000;
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: options.signal || controller.signal,
    });

    if (response.status === 401) {
      localStorage.removeItem('dav_auth_token');
    }

    // Check if response is audio binary stream
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('audio/')) {
      const blob = await response.blob();
      return blob as unknown as T;
    }

    const data = await response.json();

    if (!response.ok || data.success === false) {
      const errorMsg = data.error?.message || data.detail || `Request failed with status ${response.status}`;
      const errorCode = data.error?.code || 'HTTP_ERROR';
      throw new ApiError(errorMsg, errorCode, data.error?.details);
    }

    return data.data as T;
  } catch (err: any) {
    if (err.name === 'AbortError') {
      throw new ApiError(`Request to ${endpoint} timed out after ${timeoutMs / 1000}s`, 'TIMEOUT_ERROR');
    }
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(err.message || 'Network request failed', 'NETWORK_ERROR');
  } finally {
    clearTimeout(timeoutId);
  }
}
