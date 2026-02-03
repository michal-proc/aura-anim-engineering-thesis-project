import { USE_MOCK_DATA } from "@/lib/mock-data";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_APP_BACKEND_URL || "http://localhost:8000";

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  if (USE_MOCK_DATA) {
    throw new Error(
      "API calls are disabled when USE_MOCK_DATA is true. Use mock functions instead.",
    );
  }

  const baseUrl = API_BASE_URL.endsWith("/")
    ? API_BASE_URL.slice(0, -1)
    : API_BASE_URL;
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${baseUrl}${cleanEndpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true",
        ...options?.headers,
      },
    });

    if (
      response.status === 204 ||
      response.headers.get("content-length") === "0"
    ) {
      return {} as T;
    }

    const contentType = response.headers.get("content-type");

    if (!contentType || !contentType.includes("application/json")) {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const text = await response.text();
      throw new Error(
        `Expected JSON response but got ${contentType || "unknown content type"}. Response: ${text.substring(0, 100)}`,
      );
    }

    const data = await response.json();

    if (!response.ok) {
      throw data;
    }

    return data;
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error("Invalid JSON response from server");
    }
    throw error;
  }
}

export async function apiGet<T>(endpoint: string, token?: string): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "GET",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

export async function apiPost<T>(
  endpoint: string,
  data?: unknown,
  token?: string,
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: data ? JSON.stringify(data) : undefined,
  });
}

export async function apiPut<T>(
  endpoint: string,
  data?: unknown,
  token?: string,
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "PUT",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: data ? JSON.stringify(data) : undefined,
  });
}

export async function apiDelete<T>(
  endpoint: string,
  token?: string,
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "DELETE",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

export const apiClient = {
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete,
};
