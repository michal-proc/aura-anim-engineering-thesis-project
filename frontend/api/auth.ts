import { apiRequest } from "./client";
import type {
  LoginUserPayload,
  RegisterUserPayload,
  LoginUserResponse,
  ForgotPasswordPayload,
  ReactivateAccountPayload,
  User,
} from "@/types/auth.types";
import { USE_MOCK_DATA, mockUser } from "@/lib/mock-data";

export const authApi = {
  login: async (payload: LoginUserPayload): Promise<LoginUserResponse> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 800));
      return {
        access_token: "mock-access-token",
        refresh_token: "mock-refresh-token",
        token_type: "Bearer",
        user: mockUser,
      };
    }
    return apiRequest<LoginUserResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  register: async (
    payload: RegisterUserPayload,
  ): Promise<{ success: boolean }> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 800));
      return { success: true };
    }
    return apiRequest<{ success: boolean }>("/users/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getCurrentUser: async (token: string): Promise<User> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 300));
      return mockUser;
    }

    const response = await apiRequest<{ data: User }>("/users/me", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  },

  forgotPassword: async (payload: ForgotPasswordPayload): Promise<void> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      return;
    }
    return apiRequest<void>("/users/forgot-password", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  resetPassword: async (
    email: string,
    token: string,
    newPassword: string,
  ): Promise<void> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 800));
      return;
    }
    return apiRequest<void>(
      `/users/reset-password?email=${encodeURIComponent(email)}&token=${encodeURIComponent(token)}`,
      {
        method: "POST",
        body: JSON.stringify({ new_password: newPassword }),
      },
    );
  },

  reactivate: async (payload: ReactivateAccountPayload): Promise<void> => {
    if (USE_MOCK_DATA) {
      await new Promise((resolve) => setTimeout(resolve, 800));
      return;
    }
    return apiRequest<void>("/users/reactivate", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
